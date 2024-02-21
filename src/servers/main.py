from flask import Flask
from utils import LangChainAI

app = Flask('app')

@app.route('/')
def hello_world():
  
  langchain_client = LangChainAI()
  return 'Hello, World!'


app.run(host='0.0.0.0', port=8080)
