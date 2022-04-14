from google.cloud import pubsub_v1, storage

publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()
topic_path = publisher.topic_path(storage_client.project, "langbot_trigger")

def publish(data: str) -> None:
    # When you publish a message, the client returns a future.
    print(topic_path)
    future = publisher.publish(topic_path, data.encode("utf-8"))
    print(future.result())