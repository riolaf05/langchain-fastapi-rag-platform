#References https://github.com/Saikat-M/RAG_Using_Knowledge_base_Amazon_Bedrock/tree/main

import boto3
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv(override=True)
from utils.aws_bedrock import getAWSBedrockAnswers

st.subheader('RAG using custom retrieval strategy and prompt', divider='rainbow')

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['text'])

questions = st.chat_input('Enter you questions here...')
if questions:
    with st.chat_message('user'):
        st.markdown(questions)
    st.session_state.chat_history.append({"role":'user', "text":questions})

    response = getAWSBedrockAnswers(questions)
    # st.write(response)
    answer = response['output']['text']

    with st.chat_message('assistant'):
        st.markdown(answer)
    st.session_state.chat_history.append({"role":'assistant', "text": answer})

    if len(response['citations'][0]['retrievedReferences']) != 0:
        context = response['citations'][0]['retrievedReferences'][0]['content']['text']
        doc_url = response['citations'][0]['retrievedReferences'][0]['location']['s3Location']['uri']
        
        #Below lines are used to show the context and the document source for the latest Question Answer
        st.markdown(f"<span style='color:#FFDA33'>Context used: </span>{context}", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#FFDA33'>Source Document: </span>{doc_url}", unsafe_allow_html=True)
    
    else:
        st.markdown(f"<span style='color:red'>No Context</span>", unsafe_allow_html=True)
    