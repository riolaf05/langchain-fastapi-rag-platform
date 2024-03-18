
import os
import logger
from fastapi import FastAPI, status
from utils import LangChainAI, QDrantDBManager, EmbeddingFunction

app = FastAPI()
langchain_client = LangChainAI()
qdrantClient = QDrantDBManager(
    url=os.getenv('QDRANT_URL'),
    port=6333,
    collection_name=os.getenv('QDRANT_COLLECTION'),
    vector_size=1536,
    embedding=EmbeddingFunction('openAI').embedder,
    record_manager_url="sqlite:///record_manager_cache.sql"
)

@app.route('/rss_embed')
def rss_embed(url):

  splitted_docs = langchain_client.rss_loader(url)
  qdrantClient.index_documents(splitted_docs)
  logger.info("Transcription completed...")

  return {"name": len(splitted_docs)}

@app.route('/web_embed')
def web_embed(url):

  splitted_docs = langchain_client.webpage_loader(url)
  qdrantClient.index_documents(splitted_docs)
  logger.info("Transcription completed...")
  
  return {"name": len(splitted_docs)}


app.run(host='0.0.0.0', port=8080)
