from langchain import OpenAI, VectorDBQA, LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import chainlit as cl
load_dotenv()
from utils import build_chain, run_chain

qa = build_chain()
chat_history = [] #FIXME

@cl.on_message
async def main(message: str):
    answer = run_chain(qa, message, chat_history)
    await cl.Message(content=answer).send()