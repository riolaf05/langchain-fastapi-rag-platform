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
        try:
            self.logger.info(f"MESSAGE RECEIVED. TYPE: {kwargs['Type']}")
            self.logger.info(kwargs["Message"])

            if kwargs['Type'] == "Notification":
                logging.info("NOTIFICATION_RECEIVED")

                ######### ADD LOGIC FOR LLM INFERENCE HERE
                json_item=json.loads(kwargs["Message"])
                bucket_name=json_item['Records'][0]['s3']['bucket']['name']
                filename=json_item['Records'][0]['s3']['object']['key']
                s3 = AWSS3(bucket_name) 
                os.makedirs('/tmp/'+filename.split('/'))[:-1]
                s3.download_file(filename.replace('+', ' '), '/tmp/'+str(filename))
                
                #########

            elif kwargs['Type'] == "SubscriptionConfirmation":
                SUBSCRIBER.confirm_subscription(kwargs["Token"])

            return True

        except Exception as e:
            self.logger.error("Subscriber fail! %s" % str(e))
            return False