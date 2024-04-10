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

import sys
sys.path.append(r"C:\Users\ELAFACRB1\Codice\GitHub\media-chat-service\src\embedding")
from utils import ChromaDBManager, LangChainAI, QDrantDBManager, EmbeddingFunction

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
embedding = EmbeddingFunction('openAI').embedder
vectore_store=qdrantClient = QDrantDBManager(
    url="http://ec2-18-209-145-26.compute-1.amazonaws.com:6333/dashboard",
    port=6333,
    collection_name="rio-rag-platform",
    vector_size=1536,
    embedding=embedding,
    record_manager_url=r"sqlite:///C:\Users\ELAFACRB1\Codice\GitHub\media-chat-service\src\embedding\record_manager_cache.sql"
)
vectore_store_client=vectore_store.vector_store

COLLECTION_NAME="rio-rag-platform"

# dbUtils = ChromaDBManager()
# langchainUtils = LangChainAI()
# chat_history = [] #FIXME
# chain = langchainUtils.create_chatbot_chain() #creates a chatbot with similarity search over vector DB as retriever

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectore_store_client.as_retriever()
)


@cl.on_chat_start
async def on_chat_start():

    # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="./assets/bot.png")
    ]
    await cl.Message(content="Ciao 👋, sono il tuo assistente personale!", elements=elements).send()

@cl.on_message
async def main(message: str):

    # collection = dbUtils.get_or_create_collection(COLLECTION_NAME) #retrieve collection
    # matching_docs = dbUtils.retrieve_documents(collection, message) #similarity search
    
    # answer = chain.run(input_documents=matching_docs, question=message)
    try:
        answer=qa_chain({"query": message.content})
        await cl.Message(content=answer['result']).send()
    except Exception as e:
        print(e)
        return
    