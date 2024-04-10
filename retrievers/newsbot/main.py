from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import pandas as pd
import json

response_schemas = [
    ResponseSchema(
        name="title", 
        description="title of the news"
    ),
    ResponseSchema(
        name="text",
        description="long text (at least 3 row long) of the retrieved news",
    ),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions=output_parser.get_format_instructions()

template = """
You will be given a series of topic.
For each topic find a list of the most 5 recent news about that topic.

{format_instructions}

Wrap your final output with closed and open brackets (a list of json objects in python format, not markdown).

INPUT:
{user_topics}

YOUR RESPONSE:
"""

prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["user_topics", "standardized_industries"],
    partial_variables={"format_instructions": format_instructions}
)

_input = prompt.format_prompt(user_topics=['quantum computing', 'cloud computing'])