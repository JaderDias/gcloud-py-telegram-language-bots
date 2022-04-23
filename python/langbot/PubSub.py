from google.cloud import pubsub_v1, storage

publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

def publish(language: str) -> None:
    # When you publish a message, the client returns a future.
    topic_path = publisher.topic_path(storage_client.project, f"{language}_bot_trigger")
    print(topic_path)
    future = publisher.publish(topic_path, language.encode("utf-8"))
    print(future.result())