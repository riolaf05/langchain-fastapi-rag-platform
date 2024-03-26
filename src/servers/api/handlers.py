import logging
from config import SUBSCRIBER
from utils import AWSS3
import json
import os

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
        # try:
        self.logger.info(f"MESSAGE RECEIVED. TYPE: {kwargs['Type']}")
        self.logger.info(kwargs["Message"])

        if kwargs['Type'] == "Notification":
            logging.info("NOTIFICATION_RECEIVED")

            json_item=json.loads(kwargs["Message"])
            bucket_name=json_item['Records'][0]['s3']['bucket']['name']
            file_key=json_item['Records'][0]['s3']['object']['key']

            #downloading file..
            filename=file_key.split('/')[-1].replace('+', ' ')
            save_path='/tmp/'+'/'.join(file_key.split('/')[:-1])

            os.makedirs(save_path)
            s3 = AWSS3(bucket_name) 
            s3.download_file(file_key, os.path.join(save_path, filename))
            logging.info("File "+ filename+" downloaded!")

            if file_key.split('/')[-2] == "raw_documents":
                print("processing raw file...")
                #TODO 

            if file_key.split('/')[-2] == "processed_documents":
                print("processing processed file...")
                #TODO

            else:
                #add an exit strategy to avoid infinite loop!!
                pass

            #remove local file
                os.remove(os.path.join(save_path, filename))
                logging.info("File "+ filename+" removed!")

        elif kwargs['Type'] == "SubscriptionConfirmation":
            SUBSCRIBER.confirm_subscription(kwargs["Token"])

        return True

        # except Exception as e:
        #     self.logger.error("Subscriber fail! %s" % str(e))
        #     return False