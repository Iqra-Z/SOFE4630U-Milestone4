import json
import os
from google.cloud import pubsub_v1

PROJECT_ID = os.environ.get("GCP_PROJECT")
TOPIC_NAME = os.environ.get("TOPIC_NAME", "smart-meter")
SUB_ID = os.environ.get("SUB_ID", "smart-meter-convert-sub")

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
sub_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    try:
        data = json.loads(message.data.decode("utf-8"))

        # Expecting these fields from validated stage
        temp_c = data.get("temperature_c")
        press_kpa = data.get("pressure_kpa")

        # If missing, just ack and drop (shouldn't happen after FilterReading)
        if temp_c is None or press_kpa is None:
            message.ack()
            return

        temp_f = float(temp_c) * 1.8 + 32.0
        press_psi = float(press_kpa) / 6.895

        out = {
            "device_id": data.get("device_id"),
            "timestamp": data.get("timestamp"),
            "temperature_c": float(temp_c),
            "temperature_f": temp_f,
            "pressure_kpa": float(press_kpa),
            "pressure_psi": press_psi
        }

        attrs = {"stage": "processed"}
        publisher.publish(topic_path, json.dumps(out).encode("utf-8"), **attrs)

        message.ack()

    except Exception as e:
        # nack so it can retry if something transient happens
        message.nack()

def main():
    print(f"ConvertReading listening on {sub_path} ...", flush=True)
    streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
    streaming_pull_future.result()

if __name__ == "__main__":
    main()
