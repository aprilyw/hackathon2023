import openai
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.document_loaders import TextLoader, WebBaseLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
import uuid
import requests
import os
from langchain.llms import GPT4All

from langchain.llms import LlamaCpp
from langchain.chat_models import ChatOpenAI

openai_key  = "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"

class LocalDB:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)#, model_kwargs={"device": "cuda"})
        self.db = None

    def load_pdf(self, path):
        print(f'loading pdf from {path}')
        loader = PyPDFLoader(path)
        self.docs = loader.load()
        return self.docs

    def load_pdf_from_url(self, path):
        response = requests.get(path)

        if response.status_code == 200:
            file_name = '/Users/apwang/dev/hackathon2023/rasa-test-2/docs/' + str(uuid.uuid4()) + ".pdf"
            with open(file_name, "wb") as pdf_file:
                pdf_file.write(response.content)
            current_directory = os.getcwd()
            file_path = os.path.join(current_directory, file_name)
            print(f"pdf downloaded successfully. File path: {file_path}")
            return self.load_pdf(file_path)
        else:
            raise Exception('Unable to download the file')

    def load_webpage(self, path):
        loader = WebBaseLoader(path)
        self.docs = loader.load()
        return self.docs

    def vectorize(self, docs):
        self.db = DocArrayInMemorySearch.from_documents(docs, self.embeddings)
        
    def load_db(self, doc_type, path):
        if doc_type == 'pdf':
            doc = self.load_pdf(path)
        elif doc_type == 'webpage':
            if path.endswith('.pdf'):
                doc = self.load_pdf_from_url(path)
            else:
                doc = self.load_webpage(path)
        else:
            raise Exception('Type not supported yet')
            
        docs = self.text_splitter.split_documents(doc)
        self.vectorize(docs)

class GapGPT(LocalDB):
    def __init__(self, doc_type, doc_path, model_type, model_path=None, chain_type="stuff", temperature=0.5, k=8):
        super().__init__()
        self.load_db(doc_type, doc_path)
        self.chat_history = []
        self._load_model(model_type, model_path)
        retriever = self.db.as_retriever(search_type="similarity", search_kwargs={"k": k})
        self.qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm, 
            chain_type=chain_type, 
            retriever=retriever, 
            return_source_documents=True,
            return_generated_question=True,
        )

    def _load_model(self, model_type, model_path):
        if model_type == 'gpt4all':
            self.llm = GPT4All(model=model_path, backend="gptj", verbose=True)
        elif model_type == 'llama':
            self.llm = LlamaCpp(model_path=model_path, n_ctx=1000)
        else:
            self.llm = ChatOpenAI(
                model_name='gpt-3.5-turbo', 
                temperature=0,
                openai_api_key=openai_key,
            )
        
    def chat(self, query):
        result = self.qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.extend([(query, result["answer"])])
        self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer'] 
        return self.answer