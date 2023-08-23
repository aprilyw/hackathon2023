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
        self.agent = GapGPT(
                    model_type='openai',
                    doc_type='pdf',
                    doc_path='/Users/apwang/dev/hackathon2023/rasa-test-2/docs/OLContent.pdf',
                )

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

        response = self.agent.chat(query)
        dispatcher.utter_message(text=response)
        return []


# r’https?://\S+\.pdf’