import logging
import json
import os
import sys
import shutil
import tempfile
from contextlib import contextmanager

from utils.aws_services import AWSS3
from utils.database_managers import QDrantDBManager
from utils.speech_to_text import SpeechToText
from utils.embedding import EmbeddingFunction
from utils.language_models import LangChainAI
from utils.subscription_manager import SubscriptionManager

from config.environments import SUBS_ENDPOINT

SUBSCRIBER = SubscriptionManager(SUBS_ENDPOINT)


class SummarizationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s :%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.lang_chain = LangChainAI()
        self.s3 = AWSS3(self.bucket_name)
        self.stt = SpeechToText("gpt-3.5-turbo")

    @contextmanager
    def temporary_directory(self):
        """
        Context manager for creating and cleaning up a temporary directory.
        """
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            # Remove the directory after the test
            shutil.rmtree(temp_dir, ignore_errors=True)

    def process(self, **kwargs: dict[str, any]) -> bool:
        """
        Processes a message received from SNS.
        :param kwargs: Request arguments
        :return: True if the message was processed successfully, False otherwise
        """
        try:
            message_type = kwargs["Type"]
            if not message_type:
                self.logger.error("Invalid message format: 'Type field is missing")
                return False

            self.logger.info(f"MESSAGE RECEIVED. TYPE: {message_type}")

            if message_type == "Notification":
                self.logger.info(kwargs["Message"])
                self.logger.info("NOTIFICATION_RECEIVED")

                self._process_notification(kwargs["Message"])

            elif message_type == "SubscriptionConfirmation":
                SUBSCRIBER.confirm_subscription(kwargs["Token"])

            else:
                self.logger.warning(f"Unsuported message type: {message_type}")

            return True

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return False

    def _process_notification(self, message: str) -> None:
        """
        Precesses a notification message recevied from SNS.
        :param message: The notification message
        """
        try:
            json_item = json.loads(message)
            records = json_item["Records"]
            if not records:
                self.logger.error("Invalid message format: 'Records' field is missing")
                return

            file_key = records[0]["s3"]["object"]["key"].replace("+", " ")

            filename = file_key.split("/")[-1]  # e.g. 'file.txt'
            save_path = "/".join(
                file_key.split("/")[:-1]
            )  # e.g. 'news4p/raw_documents'

            with self.temporary_directory() as temp_dir:
                local_save_path = os.path.join(
                    temp_dir, save_path
                )  # e.g. '/tmp/news4p/raw_documents'
                self._download_and_process_file(file_key, filename, local_save_path)

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            self.logger.error(f"Invalid message format: {e}")
        except Exception as e:
            self.logger.error(f"Error processing notification message: {e}")

    def _download_and_process_file(self, file_key, filename, local_save_path):
        """
        Downloads a file from S3, processes it, and uploads the processed file to S3.
        :param file_key: The key of the file in S3
        :param filename: The name of the file
        :param local_save_path: The local path to save the downloaded file
        """
        try:
            # Download file from S3
            self.s3.download_file(file_key, os.path.join(local_save_path, filename))
            self.logger.info(
                f"Downloaded file '{filename}' from S3 bucket '{self.bucket_name}' to local path '{local_save_path}'"
            )

        except Exception as e:
            self.logger.error(f"Error downloading file from S3: {e}")

        try:
            # Process raw file
            if file_key.split("/")[-2] == "raw_documents":
                self.logger.info(f"Processing raw file '{filename}'")

                transcribed_text = self.stt.transcribe(
                    os.path.join(local_save_path, filename)
                )
                logging.info(
                    f"File '{filename}' has been transcribed to '{transcribed_text}'"
                )

                text_file = f"{filename.split('.')[:-1][0]}.txt"
                text_file_full_path = os.path.join(local_save_path, text_file)

                with open(text_file_full_path, "w") as f:
                    f.write(transcribed_text)

                with open(text_file_full_path, "rb") as f:
                    # Upload processed file to S3
                    self.s3.upload_file(
                        f, os.path.join("processed_documents", text_file)
                    )
                    self.logger.info(
                        f"Uploaded processed file '{text_file}' to S3 bucket '{self.bucket_name}' in '/processed_documents' directory"
                    )
                    # Delete the file from raw_documents/ directory in S3 bucket
                    self.s3.delete_file(file_key)
                    self.logger.info(
                        f"Deleted the raw file '{filename}' in '/raw_documents' directory"
                    )

            else:
                self.logger.info(
                    f"No further processing required for file or it's not in raw_documents/ directory '{filename}'"
                )

        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
