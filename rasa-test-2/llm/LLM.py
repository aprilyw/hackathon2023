from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class LLM():
    def __init__(self):
        template = """Question: {question}

        Answer: Let's think step by step."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        local_path = ("./models/orca-mini-3b.ggmlv3.q4_0.bin")
        # Callbacks support token-wise streaming
        callbacks = [StreamingStdOutCallbackHandler()]

        # Verbose is required to pass to the callback manager
        llm = GPT4All(model=local_path, callbacks=callbacks, verbose=True)

        # If you want to use a custom model add the backend parameter
        # Check https://docs.gpt4all.io/gpt4all_python.html for supported backends
        llm = GPT4All(model=local_path, backend="gptj", callbacks=callbacks, verbose=True)

        self.llm_chain = LLMChain(prompt=prompt, llm=llm)

    def chat_query(self, user_message):
        return(self.llm_chain.run(user_message))

