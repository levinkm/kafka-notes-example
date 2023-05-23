from configparser import ConfigParser
from pathlib import Path
import pathlib


BASE_DIR = Path(__file__).resolve().parent.parent


from confluent_kafka import Consumer

if __name__ == "__main__":
    # parse the config
    config_parser = ConfigParser()
    config_parser.read("config.ini")  # make sure to have created the "config.ini" file
    # read the default and consumer configs
    config = dict(config_parser["default"])
    config.update(config_parser["consumer"])

    # create Consumer instance
    consumer = Consumer(config)

    # subscribe to topic
    topic = "bookings"
    consumer.subscribe([topic])

    # poll for new messages from kafka and print them.
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("Waiting..")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # extract the (optional) key and value and print

                print(
                    f"Consumed event from topic{msg.topic()}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}"
                )
    except KeyboardInterrupt:
        pass
    finally:
        # leave group and commit final offsets
        consumer.close()
