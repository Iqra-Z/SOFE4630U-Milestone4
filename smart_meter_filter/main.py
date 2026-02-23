import os
import json
import time
from google.cloud import pubsub_v1

PROJECT_ID = os.environ["GCP_PROJECT"]
TOPIC_NAME = os.environ.get("TOPIC_NAME", "smart-meter")
SUBSCRIPTION_ID = os.environ["SUB_ID"]

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
sub_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def has_none(payload: dict) -> bool:
    # Check any value in the payload dict for None (null)
    for k, v in payload.items():
        if v is None:
            return True
    return False

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    try:
        data = message.data.decode("utf-8")
        payload = json.loads(data)

        # Drop records with missing measurements
        if has_none(payload):
            print(f"DROPPED (contains None): {payload}")
            message.ack()
            return

        # Republish validated record
        future = publisher.publish(
            topic_path,
            json.dumps(payload).encode("utf-8"),
            stage="validated"
        )
        future.result()
        print(f"VALIDATED -> republished stage=validated: {payload}")
        message.ack()

    except Exception as e:
        print(f"ERROR: {e}")
        message.nack()

def main():
    print(f"FilterReading listening on {sub_path} ...")
    streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()

if __name__ == "__main__":
    main()
