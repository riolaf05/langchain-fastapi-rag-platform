import logging
import json
import os

from utils.aws_services import AWSS3
from utils.database_managers import QDrantDBManager
from utils.speech_to_text import SpeechToText
from utils.embedding import EmbeddingFunction
from utils.language_models import LangChainAI
from utils.subscription_manager import SubscriptionManager
from utils.text_processing import OCRText

from config.environments import SUBS_ENDPOINT

SUBSCRIBER = SubscriptionManager(SUBS_ENDPOINT)

class TextService:
    def __init__(self):
        self.logger = logging.getLogger("subscriber")
        self.logger.setLevel(logging.INFO)
        self.bucket_name = os.getenv('AWS_TEXT_S3_BUCKET_NAME')
        self.qdrant_client = QDrantDBManager(
            url=os.getenv('QDRANT_URL'),
            port=6333,
            collection_name=os.getenv('COLLECTION_NAME'),
            vector_size=1536,
            embedding=EmbeddingFunction('openAI').embedder,
            record_manager_url="sqlite:///record_manager_cache.sql"
        )
        self.lang_chain = LangChainAI()
        self.s3 = AWSS3(self.bucket_name)

    def process(self, **kwargs):
        """
        Processes a message received from SNS.
        :param kwargs: Request arguments
        :return:
        """
        # try:

        self.logger.info(f"MESSAGE RECEIVED. TYPE: {kwargs['Type']}")
        self.logger.info(kwargs["Message"])

        if kwargs['Type'] == "Notification":
            logging.info("NOTIFICATION_RECEIVED")

            json_item=json.loads(kwargs["Message"])
            file_key=json_item['Records'][0]['s3']['object']['key'].replace('+', ' ')

            # #downloading file..
            filename=file_key.split('/')[-1]
            save_path='/'.join(file_key.split('/')[:-1]) #news4p/raw_documents
            local_save_path='/tmp/'+save_path #/tmp/news4p/raw_documents

            if not os.path.exists(save_path): 
                os.makedirs(save_path) 
            self.s3.download_file(file_key, os.path.join(local_save_path, filename))
            logging.info("File "+ filename+" downloaded!")

            #processing raw file..
            if file_key.split('/')[-2] == "raw_documents":
                print("processing raw file...")

                ###Process starts here..

                if filename.split('.')[-1] != "pdf" or filename.split('.')[-1] != "txt":
                    ocr_text=self.ocr.read_pdf(local_save_path)
                    text_file = filename.split('.')[:-1][0]+'.txt'
                    f = open(os.path.join('/tmp/', text_file), "w")
                    f.write(ocr_text) 
                    f.close()

                #load on S3
                self.s3.upload_file(os.path.join('/tmp/', text_file), os.path.join("news4p/processed_documents", filename))

                #delete local file
                os.remove(os.path.join(local_save_path, text_file))
                print("File "+ filename+" processed!")

            #next steps of the pipeline..
            if file_key.split('/')[-2] == "processed_documents":
                print("embeddng output file...")

                #embedding
                #TODO
                
            else:
                #add an exit strategy to avoid infinite loop!!
                pass

            ##delete local raw file
                # os.remove(os.path.join(save_path, filename))
                # logging.info("File "+ filename+" removed!")

        elif kwargs['Type'] == "SubscriptionConfirmation":
            SUBSCRIBER.confirm_subscription(kwargs["Token"])

        return True

        # except Exception as e:
        #     self.logger.error("Subscriber fail! %s" % str(e))
        #     return False
