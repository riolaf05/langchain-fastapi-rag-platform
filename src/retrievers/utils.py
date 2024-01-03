import logging
import requests
import json
import time
import boto3
import os
import io
import openai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers.audio import OpenAIWhisperParser, OpenAIWhisperParserLocal
from langchain.docstore.document import Document
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
load_dotenv()
from urllib.request import urlopen
import spacy
import chromadb
import numpy as np
import random
import datetime
load_dotenv()
     
# AWS Texttract
class AWSTexttract:

    def __init__(self):
        self.client = boto3.client('textract', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))

    def get_text(self, file_path):
        
        if type(file_path) == str:
            #cioè se passo il path del file
            with open(file_path, 'rb') as file:
                img_test = file.read()
                bytes_test = bytearray(img_test)
                print('Image loaded', file_path)
            response = self.client.detect_document_text(Document={'Bytes': bytes_test})
        else:
            #se passo il formato PIL
            buf = io.BytesIO()
            file_path.save(buf, format='JPEG')
            byte_im = buf.getvalue()
            response = self.client.detect_document_text(Document={'Bytes': byte_im})

        text = ''
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + '\n'

        return text
    
# AWS Transcribe
class AWSTranscribe:
    
        def __init__(self, job_uri):
            self.transcribe = boto3.client('transcribe', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))
            self.job_verification = False
            self.job_uri=job_uri

        def generate_job_name(self):
            return "chatgpt_summary_"+str(time.time_ns())+"_"+str(random.randint(0,500))

        def check_job_name(self, job_name):
            """
            Check if the transcribe job name is existed or not
            """
            self.job_verification = True
            # all the transcriptions
            existed_jobs = self.transcribe.list_transcription_jobs()
            for job in existed_jobs['TranscriptionJobSummaries']:
                if job_name == job['TranscriptionJobName']:
                    self.job_verification = False
                break
            # if job_verification == False:
            #     command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")   
            #     if command.lower() == "y" or command.lower() == "yes":                
            #         self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                # elif command.lower() == "n" or command.lower() == "no":      
                #     job_name = input("Insert new job name? ")      
                #     self.check_job_name(job_name)
                # else:
                #     print("Input can only be (Y/N)")
                #     command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
            return job_name
    
        def amazon_transcribe(self, job_uri, job_name, audio_file_name, language):
            """
            For single speaker
            """
            # Usually, I put like this to automate the process with the file name
            # "s3://bucket_name" + audio_file_name  
            # Usually, file names have spaces and have the file extension like .mp3
            # we take only a file name and delete all the space to name the job
            job_name = job_name
            job_uri=self.job_uri+audio_file_name
            # file format  
            file_format = audio_file_name.split('.')[-1]
            
            # check if name is taken or not
            job_name = self.check_job_name(job_name)
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat = file_format,
                LanguageCode=language)
            
            while True:
                result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(15)
            if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
                response = urlopen(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                data = json.loads(response.read())
            return data['results']['transcripts'][0]['transcript']

# AWS S3
class AWSS3:
    
        def __init__(self, bucket=None):
            self.s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))
            self.bucket = bucket

        def read_metadata(self, key, id):
            response = self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return response['Metadata'][id]

        def list_items(self, key):
            list=self.s3_client.list_objects_v2(Bucket=self.bucket,Prefix=key)
            return list.get('Contents', [])
        
        def upload_file(self, file, s3_file):
            """Upload a file to an S3 bucket
            """
            try:
                #the first argument is the file path

                self.s3_client.upload_file(file, self.bucket, s3_file, ExtraArgs={'Metadata': {'Name': s3_file}})
                logging.info('File Successfully Uploaded on S3')
                return True
            except FileNotFoundError:
                time.sleep(9)
                logging.error('File not found.')
                return False
        
        def download_file(self, bucket, object_name, file_name):
            """Download a file from an S3 bucket
    
            :param bucket: Bucket to download from
            :param object_name: S3 object name
            :param file_name: File to download, path
            :return: True if file was downloaded, else False
    
            """
            # Download the file
            try:
                response = self.s3_client.download_file(bucket, object_name, file_name)
            except Exception as e:
                logging.error(e)
                return False
            return True

# Lambda
class AWSLambda:
    def __init__(self):
        self.lambda_client = boto3.client('lambda', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('AWS_REGION'))
    
    def invoke_lambda(self, function_name, payload):
        """Invoke a lambda function
        """
        try:
            response = self.lambda_client.invoke(FunctionName=function_name, InvocationType='RequestResponse', Payload=payload)
            logging.info('Lambda invoked')
            body=response['Payload'].read()
            json_object = json.loads(body)
            return json_object['body']
        except Exception as e:
            logging.error(e)
            return False

# Spacy NLP
class TextSplitter:

    def __init__(self):
        self.nlp = spacy.load("it_core_news_sm")

    def process(self, text):
        doc = self.nlp(text)
        sents = list(doc.sents)
        vecs = np.stack([sent.vector / sent.vector_norm for sent in sents])
        return sents, vecs

    def cluster_text(self, sents, vecs, threshold):
        clusters = [[0]]
        for i in range(1, len(sents)):
            if np.dot(vecs[i], vecs[i-1]) < threshold:
                clusters.append([])
            clusters[-1].append(i)
        
        return clusters

    
    def clean_text(self, text):
        # Add your text cleaning process here
        return text
        
    def split_text(self, data, threshold=0.3):
        '''
        Split thext using semantic clustering and spacy see https://getpocket.com/read/3906332851
        '''
    

        # Initialize the clusters lengths list and final texts list
        clusters_lens = []
        final_texts = []

        # Process the chunk
        sents, vecs = self.process(data)

        # Cluster the sentences
        clusters = self.cluster_text(sents, vecs, threshold)

        for cluster in clusters:
            cluster_txt = self.clean_text(' '.join([sents[i].text for i in cluster]))
            cluster_len = len(cluster_txt)
            
            # Check if the cluster is too short
            if cluster_len < 60:
                continue
            
            # Check if the cluster is too long
            elif cluster_len > 3000:
                threshold = 0.6
                sents_div, vecs_div = self.process(cluster_txt)
                reclusters = self.cluster_text(sents_div, vecs_div, threshold)
                
                for subcluster in reclusters:
                    div_txt = self.clean_text(' '.join([sents_div[i].text for i in subcluster]))
                    div_len = len(div_txt)
                    
                    if div_len < 60 or div_len > 3000:
                        continue
                    
                    clusters_lens.append(div_len)
                    final_texts.append(div_txt)
                    
            else:
                clusters_lens.append(cluster_len)
                final_texts.append(cluster_txt)
        
        #converting to Langchain documents
        ##lo posso fare anche con .create_documents !!
        # final_docs=[]
        # for doc in final_texts:
        #     final_docs.append(Document(page_content=doc, metadata={"source": "local"}))
            
        return final_texts
    
    def create_langchain_documents(texts, metadata={"source": "local"}):
        final_docs=[]
        for doc in texts:
            final_docs.append(Document(page_content=doc, metadata=metadata))
        return final_docs

# DynamoDB
class DynamoDBManager:
    def __init__(self, region, table_name):
        self.region = region
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),  region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def write_item(self, item):
        try:
            response = self.table.put_item(Item=item)
            print("Item added successfully:", response)
        except Exception as e:
            print("Error writing item:", e)
    
    def update_item(self, key, update_expression, expression_values):
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            print("Item updated successfully:", response)
        except Exception as e:
            print("Error updating item:", e)
    def get_item(self, key):
        try:
            response = self.table.get_item(Key=key)
            print("Item retrieved successfully:", response)
            return response
        except Exception as e:
            print("Error retrieving item:", e)

# Chroma vector DB
class ChromaDBManager:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=os.getenv("PERSIST_DIR_PATH"))

    def get_or_create_collection(self, collection_name):
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            print(f"Collection {collection_name} created successfully.")
        except Exception as e:
            print(f"Error creating collection {collection_name}: {e}")
        return collection
    
    def store_documents(self, collection, docs):
        '''
        Stores document to a collection
        Gets Langchain documents in input.
        By default, Chroma uses the Sentence Transformers all-MiniLM-L6-v2 model to create embeddings. 
        '''
        #add documents to collection
        collection_documents = [document.page_content for document in docs]
        collection_metadata = [document.metadata for document in docs]
        
        #get a str id for each collection id, starting from the current maximum id of the collection
        collection_ids = [str(collection_id + 1) for collection_id in range(len(collection_documents))]

        #filter metadata
        self.replace_empty_medatada(collection_metadata)

        #add documents to collection
        #this method creates the embedding and the colection 
        #By default, Chroma uses the Sentence Transformers all-MiniLM-L6-v2 model to create embeddings. 
        collection.add(ids=collection_ids, documents=collection_documents, metadatas=collection_metadata)

        #the collection are automatically stored since we're using a persistant client
        return collection.count()
    
        
    def replace_empty_medatada(self, metadata_list):
        #iter through metadata elements
        for metadata in metadata_list:
            #get index of metadata element
            index = metadata_list.index(metadata)
            #get metadata keys
            metadata_keys = metadata.keys()
            #iter through metadata keys
            for key in metadata_keys:
                #if key is empty
                if metadata[key] == []:
                    #replace it with None
                    metadata_list[index][key] = ''
                if type(metadata[key]) == datetime.datetime:
                    #replace it str
                    metadata_list[index][key] = str(metadata[key])

    def retrieve_documents(collection, query, n_results=3):
        '''
        To run a similarity search, 
        you can use the query method of the collection.
        '''
        llm_documents = []

        #similarity search <- #TODO compare with Kendra ? 
        res=collection.query(query_texts=[query], n_results=n_results)

        #create documents from collection
        documents=[document for document in res['documents'][0]]
        metadatas=[metadata for metadata in res['metadatas'][0]]
        
        for i in range(len(documents)):
            doc=Document(page_content=documents[i], metadata=metadatas[i])
            llm_documents.append(doc)
        return llm_documents
                    

# LangChain
class LangChainAI:

    def __init__(self, 
                 model_name="gpt-3.5-turbo-16k",
                 chatbot_model="gpt-3.5-turbo", 
                 chunk_size=1000, 
                 chunk_overlap=20
                 ):
        
        self.text_summarizer = TextSplitter()

        self.chatbot_model=chatbot_model
        
        self.llm = ChatOpenAI(
          model_name=model_name, # default model
          temperature=0.9
          ) #temperature dictates how whacky the output should be
        self.chains = []
        self.chunk_size=chunk_size,
        self.chunk_overlap=chunk_overlap

    def split_docs(self, documents):
        '''
        Takes a list of document as an array
        Splitting the documents into chunks of text
        converting them into a list of documents
        '''
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        docs = text_splitter.create_documents(documents)
        # docs = text_splitter.split_documents(documents)
        return docs
    
    def translate_text(self, text):
        prompt_template = PromptTemplate.from_template(
            "traduci {text} in italiano."
        )
        prompt_template.format(text=text)
        llmchain = LLMChain(llm=self.llm, prompt=prompt_template)
        res=llmchain.run(text)+'\n\n'
        return res
    
    def summarize_text(self, text):
        '''
        The map reduce documents chain first applies an LLM chain to each document individually (the Map step), 
        treating the chain output as a new document. 
        It then passes all the new documents to a separate combine documents chain to get a single output (the Reduce step). 
        It can optionally first compress, or collapse, 
        the mapped documents to make sure that they fit in the combine documents chain 
        (which will often pass them to an LLM). This compression step is performed recursively if necessary.
        '''
        chain = load_summarize_chain(self.llm, chain_type="map_reduce", verbose = True) 
        docs = self.text_summarizer.split_text(text) 
        max_chunk_len = len(max(docs, key = len))
        doc_splitter = RecursiveCharacterTextSplitter(chunk_size=max_chunk_len, chunk_overlap=20)
        docs = doc_splitter.create_documents(docs)
        summarized_data = chain.run(docs)
        translated_summarized_data = self.translate_text(summarized_data) #to resolve a bug in the summarize chain which returns the text in english
        return translated_summarized_data

    def bullet_point_text(self, text):
        '''
        Making the text more understandable by creating bullet points,
        using the chain StuffDocumentsChain:
        this chain will take a list of documents, 
        inserts them all into a prompt, and passes that prompt to an LLM
        See: https://python.langchain.com/docs/use_cases/summarization
        '''
        docs = self.text_summarizer.split_text(text) 
        max_chunk_len = len(max(docs, key = len))
        doc_splitter = RecursiveCharacterTextSplitter(chunk_size=max_chunk_len, chunk_overlap=20)
        docs = doc_splitter.create_documents(docs)

        # Define prompt
        prompt_template = """Scrivi una lista di bullet point che sintetizzano il contenuto dei documenti:
        "{text}"
        Lista dei bullet points:"""
        prompt = PromptTemplate.from_template(prompt_template)

        # Define LLM chain
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        # Define StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )
        res=stuff_chain.run(docs)
        return res
    
    def paraphrase_text(self, text):
        '''
        Paraphrasing the text using the chain
        '''
        prompt = PromptTemplate(
        input_variables=["long_text"],
        template="Puoi parafrasare questo testo (in italiano)? {long_text} \n\n",
        )
        llmchain = LLMChain(llm=self.llm, prompt=prompt)
        res=llmchain.run(text)+'\n\n'
        return res
    
    def expand_text(self, text):
        '''
        Enhancing the text using the chain
        '''
        prompt = PromptTemplate(
        input_variables=["long_text"],
        template="Puoi arricchiere l'esposizione di questo testo (in italiano)? {long_text} \n\n",
        )
        llmchain = LLMChain(llm=self.llm, prompt=prompt)
        res=llmchain.run(text)+'\n\n'
        return res

    def draft_text(self, text):
        '''
        Makes a draft of the text using the chain
        '''
        prompt = PromptTemplate(
        input_variables=["long_text"],
        template="Puoi fare una minuta della trascrizione di una riunione contenuta in questo testo (in italiano)? {long_text} \n\n",
        )
        llmchain = LLMChain(llm=self.llm, prompt=prompt)
        res=llmchain.run(text)+'\n\n'
        return res

    def chat_prompt(self, text):
        #TODO
        pass

    def extract_video(self, url):
        '''
        Estrae il testo di un video da un url in ingresso
        '''
        local = False
        text=""
        save_dir=""
        # Transcribe the videos to text
        if local:
            loader = GenericLoader(
                YoutubeAudioLoader([url], save_dir), OpenAIWhisperParserLocal()
            )
        else:
            loader = GenericLoader(YoutubeAudioLoader([url], save_dir), OpenAIWhisperParser())
        docs = loader.load()
        for docs in docs:
            #write all the text into the var
            text+=docs.page_content+'\n\n'
        return text

    def github_prompt(self, url):
        #TODO
        pass

    def summarize_repo(self, url):
        #TODO
        pass

    def generate_paragraph(self, text):
        #TODO
        pass

    def final_chain(self, user_questions):
        # Generating the final answer to the user's question using all the chains

        sentences=[]

        for text in user_questions:
            # print(text)
            
            # Chains
            prompt = PromptTemplate(
                input_variables=["long_text"],
                template="Puoi rendere questo testo più comprensibile? {long_text} \n\n",
            )
            llmchain = LLMChain(llm=self.llm, prompt=prompt)
            res=llmchain.run(text)+'\n\n'
            print(res)
            sentences.append(res)

        print(sentences)
        
        # Chain 2
        template = """Puoi ordinare il testo di queste frasi secondo il significato? {sentences}\n\n"""
        prompt_template = PromptTemplate(input_variables=["sentences"], template=template)
        question_chain = LLMChain(llm=self.llm, prompt=prompt_template, verbose=True)

        # Final Chain
        template = """Puoi sintetizzare questo testo in una lista di bullet points utili per la comprensione rapida del testo? '{text}'"""
        prompt_template = PromptTemplate(input_variables=["text"], template=template)
        answer_chain = LLMChain(llm=self.llm, prompt=prompt_template)

        overall_chain = SimpleSequentialChain(
            chains=[question_chain, answer_chain],
            verbose=True,
        )

        res = overall_chain.run(sentences)
    
        return res
    
    def create_chatbot_chain(self):
        model_name = self.chatbot_model
        llm = ChatOpenAI(model_name=model_name)
        chain = load_qa_chain(llm, chain_type="stuff", verbose=False)
        return chain

