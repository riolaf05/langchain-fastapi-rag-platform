
import os
import telepot
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import json
from dotenv import load_dotenv
load_dotenv(override=True)

TOPICS = ['quantum computing', 'cloud computing']
TELEGRAM_CHAT_ID=os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_GROUP_ID=os.getenv('TELEGRAM_GROUP_ID')
RESPONSE_SCHEMAS = [
    ResponseSchema(
        name="title", 
        description="title of the news"
    ),
    ResponseSchema(
        name="text",
        description="long text (at least 3 row long) of the retrieved news",
    ),
]
TEMPLATE = """
    You will be given a series of topic.
    For each topic find a list of the most 5 recent news about that topic.

    {format_instructions}

    Wrap your final output with closed and open brackets (a list of json objects in python format, not markdown).

    INPUT:
    {user_topics}

    YOUR RESPONSE:
"""


output_parser = StructuredOutputParser.from_response_schemas(RESPONSE_SCHEMAS)
format_instructions=output_parser.get_format_instructions()
chat_model = ChatOpenAI(temperature=0)
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(TEMPLATE)  
    ],
    input_variables=["user_topics"],
    partial_variables={"format_instructions": format_instructions}
)
_input = prompt.format_prompt(user_topics=TOPICS)
output = chat_model(_input.to_messages())

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        
        output = chat_model(_input.to_messages())

        # bot.sendMessage(chat_id, res)
        bot.sendMessage(TELEGRAM_GROUP_ID, "ciao ecco qualche news dal tuo bot AI")
        for title in json.loads(output.content):
            bot.sendMessage(TELEGRAM_GROUP_ID, 
                '''
                Titolo: {}
                News: {}
                '''.format(title['title'], title['text'])
            )

bot = telepot.Bot(TELEGRAM_CHAT_ID)
bot.message_loop(on_chat_message)

print('Listening ...')

import time
while 1:
    time.sleep(10)