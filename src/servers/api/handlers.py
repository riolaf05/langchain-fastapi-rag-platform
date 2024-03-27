import logging
from config import SUBSCRIBER
from utils import AWSS3
import json
import os
from utils import QDrantDBManager, LangChainAI, EmbeddingFunction, SpeechToText

BUCKET_NAME='news4p-documents-bucket'

qdrantClient = QDrantDBManager(
    url=os.getenv('QDRANT_URL'),
    port=6333,
    collection_name=os.getenv('COLLECTION_NAME'),
    vector_size=1536,
    embedding=EmbeddingFunction('openAI').embedder,
    record_manager_url="sqlite:///record_manager_cache.sql"
)
langChain = LangChainAI()
s3 = AWSS3(BUCKET_NAME) 
stt = SpeechToText('transcribe')

class SubscribeHandler:

    def __init__(self):
        self.logger = logging.getLogger("subscriber")
        self.logger.setLevel(logging.INFO)

    def process(self, **kwargs):
        """
        Processes a message received from SNS.
        :param kwargs: Request arguments
        :return:
        """
        try:

            self.logger.info(f"MESSAGE RECEIVED. TYPE: {kwargs['Type']}")
            self.logger.info(kwargs["Message"])

            if kwargs['Type'] == "Notification":
                logging.info("NOTIFICATION_RECEIVED")

                json_item=json.loads(kwargs["Message"])
                file_key=json_item['Records'][0]['s3']['object']['key'].replace('+', ' ')

                #downloading file..
                filename=file_key.split('/')[-1]
                save_path='/tmp/'+'/'.join(file_key.split('/')[:-1])

                if not os.path.exists(save_path): 
                    os.makedirs(save_path) 
                
                s3.download_file(file_key, os.path.join(save_path, filename))
                logging.info("File "+ filename+" downloaded!")

                #processing raw file..
                if file_key.split('/')[-2] == "raw_documents":
                    print("processing raw file...")
                    
                    #speech-to-text
                    text=stt.transcribe(os.path.join(save_path, filename))
                    text_file = filename.split('.')[:-1][0]+'.txt'
                    f = open(os.path.join('/tmp/', text_file), "w")
                    f.write(text)
                    f.close()

                    #load on S3
                    s3.upload_file(os.path.join('/tmp/', text_file), os.path.join("news4p/processed_documents", filename))

                    #delete local file
                    os.remove(os.path.join(save_path, text_file))
                    print("File "+ filename+" processed!")



                #second process in the pipeline (summary, clean, etc.)
                if file_key.split('/')[-2] == "processed_documents":
                    print("processing processed file...")

                    #summary
                    #TODO

                else:
                    #add an exit strategy to avoid infinite loop!!
                    pass

                ##delete local raw file
                    os.remove(os.path.join(save_path, filename))
                    logging.info("File "+ filename+" removed!")

            elif kwargs['Type'] == "SubscriptionConfirmation":
                SUBSCRIBER.confirm_subscription(kwargs["Token"])

            return True

        except Exception as e:
            self.logger.error("Subscriber fail! %s" % str(e))
            return False