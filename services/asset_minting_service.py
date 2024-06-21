import logging
import json
import os
import requests

from utils.aws_services import AWSS3
from utils.subscription_manager import SubscriptionManager
from config.environments import SUBS_ENDPOINT

SUBSCRIBER = SubscriptionManager(SUBS_ENDPOINT)
MINT_BASE_URL = os.getenv("MINT_BASE_URL")


class AssetMintingService:
    def __init__(self):
        self.logger = logging.getLogger("subscriber")
        self.logger.setLevel(logging.INFO)
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.s3 = AWSS3(self.bucket_name)

    def mint_assets(self, **kwargs):
        """
        Processes a message received from SNS.
        :param kwargs: Request arguments
        :return: bool or None
        """
        try:
            self.logger.info(f"MESSAGE RECEIVED. TYPE: {kwargs['Type']}")
            self.logger.info(kwargs["Message"])

            if kwargs["Type"] == "Notification":
                self.logger.info("NOTIFICATION_RECEIVED")

                json_item = json.loads(kwargs["Message"])
                file_key = json_item["Records"][0]["s3"]["object"]["key"].replace(
                    "+", " "
                )

                # Processing raw file..
                if file_key.split("/")[-2] == "raw_documents":
                    self.logger.info("Processing raw file...")
                    # Trigger the endpoint
                    response = requests.post(
                        f"{MINT_BASE_URL}/api/trigger-prepare-ipfs"
                    )
                    if response.status_code == 200:
                        self.logger.info("Triggered endpoint successfully.")
                        return True
                    else:
                        self.logger.error(
                            f"Failed to trigger endpoint. Status code: {response.status_code}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            # Handle the error accordingly, e.g., return None to indicate failure
            return None
