from google.cloud import pubsub_v1, storage
from Logger import logger

publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

def publish(language: str) -> None:
    # When you publish a message, the client returns a future.
    topic_path = publisher.topic_path(storage_client.project, f"{language}_bot_trigger")
    logger.info(topic_path)
    future = publisher.publish(topic_path, language.encode("utf-8"))
    logger.info(future.result())