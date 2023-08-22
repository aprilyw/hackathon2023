# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


import re
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
# from dotenv import load_dotenv
from logging import getLogger
from enum import IntEnum
import os
from llm.LLM import LLM
from llm.gptbot import GapGPT

logger = getLogger(__name__)

env = os.getenv("ENV", "local")
env_file = f".env-{env}"
# load_dotenv(dotenv_path=f"../../.env-{env}")

MODEL_NAME = os.getenv("MODEL_NAME")

logger = getLogger(__name__)

# -------------------------------------------------
# Custom Rasa action to trigger our RasaGPT LLM API
# -------------------------------------------------
class ActionGPTFallback(Action):
    def __init__(self):
    #     self.llm = LLM()
        self.agent = None

    def name(self) -> str:
        return "action_gpt_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # ------------
        # Get metadata
        # ------------
        data = tracker.latest_message
        logger.info(f'data: {data}')

        #bot = self.llm
        #response = bot.chat_query(data['text'])

        query = data['text']

        # url_pattern = r'<(https?://\S+)>'
        # urls = re.findall(url_pattern, query)
        # logger.info(f'urls: {urls}')

        if 'http' in query:
            logger.info(f'query: {query}')
            # url_pattern = r'https?://\S+\.pdf'
            # urls = re.findall(url_pattern, query)

            if not self.agent:
                self.agent = GapGPT(
                    model_type='openai',
                    doc_type='webpage',
                    doc_path=query[1:-1],
                )
                logger.info("agent initialized")
                response = "url received. What would you like to know?"
                dispatcher.utter_message(text=response)
                return []
                    
        else:
            logger.info("Not a link")
            response = self.agent.chat(query)
            dispatcher.utter_message(text=response)
            return []


# r’https?://\S+\.pdf’