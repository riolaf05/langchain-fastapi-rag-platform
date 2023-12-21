from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain import OpenAI
import sys
import boto3
import os
from dotenv import load_dotenv
load_dotenv(override=True)

def build_chain():
  region = os.environ["AWS_REGION"]
  kendra_index_id = os.environ["KENDRA_INDEX_ID"]
  profile=os.environ["AWS_PROFILE"]

  kendra_client = boto3.client("kendra", region_name=region)

  llm = OpenAI(batch_size=5, temperature=0, max_tokens=300)
      
  retriever = AmazonKendraRetriever(index_id=kendra_index_id, region_name=region, client=kendra_client)

  prompt_template = """
  The following is a friendly conversation between a human and an AI. 
  The AI is talkative and provides lots of specific details from its context.
  If the AI does not know the answer to a question, it truthfully says it 
  does not know.
  {context}
  Instruction: Based on the above documents, provide a detailed answer for, {question} Answer "don't know" 
  if not present in the document. 
  Solution:"""
  PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )

  #The first chain condenses the current question and the chat history into a standalone question.
  # You can use use a cheaper and faster model for the simpler task of condensing the question, 
  # and then a more expensive model for answering the question. 
  # the condense_question_prompt param can be used to change the default prompt for condensing the question.
  condense_qa_template = """
  Given the following conversation and a follow up question, rephrase the follow up question 
  to be a standalone question.

  Chat History:
  {chat_history}
  Follow Up Input: {question}
  Standalone question:"""
  standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)

  qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        condense_question_prompt=standalone_question_prompt, 
        return_source_documents=True, 
        combine_docs_chain_kwargs={"prompt":PROMPT})
  return qa

def run_chain(chain, prompt: str, history=[]):
  return chain({"question": prompt, "chat_history": history})
