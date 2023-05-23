from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
import json

import socket
from configparser import ConfigParser


class JsonSerializer:
    def __init__(self):
        pass

    def __call__(self, value):
        return json.dumps(value).encode("utf-8")


config_parser = ConfigParser()
config_parser.read("config.ini")  # make sure to have created the "config.ini" file
# read the default and consumer configs
config = dict(config_parser["default"])
config.update(
    {
        "client.id": socket.gethostname(),
        "key.serializer": StringSerializer("utf_8"),
        # "value.serializer": JsonSerializer(),
    }
)

topic = "accounts"

producer = SerializingProducer(config)


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush()."""
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))
        print(msg.value().decode("utf-8"))


producer.produce(
    topic,
    # key="key",
    value=json.dumps({"user_id": "34342ksdf-eww", "booked": "True"}).encode("utf-8"),
    on_delivery=delivery_report,
)

producer.flush()
