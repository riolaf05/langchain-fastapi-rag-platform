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
from utils import ChromaDBManager, LangChainAI, run_chain

dbUtils = ChromaDBManager()
langchainUtils = LangChainAI()
chat_history = [] #FIXME
chain = langchainUtils.create_chatbot_chain() #creates a chatbot with similarity search over vector DB as retriever

@cl.on_message
async def main(message: str):

    #answer 
    answer = run_chain(chain, message, chat_history)
    collection = dbUtils.get_or_create_collection("media-chat-service")
    matching_docs = dbUtils.retrieve_documents(collection, message)
    answer = chain.run(input_documents=matching_docs, question=message)
    await cl.Message(content=answer).send()