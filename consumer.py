from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer

if __name__ == '__main__':
    # parse the command line.
    parser = ArgumentPArser()
    parser.add_argument('config_file',type=FileType("r"))
    args = parser.parse_args()

    #parse the config
    config_parser = ConfigPArser()
    consfig_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['consumer'])

    # create Consumer instance
    consumer = Consumer(Config)

    # subscribe to topic
    topic = "bookings"
    cosumer.subscribe([topic])

    # poll for new messages from kafka and print them.
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print('Waiting..')
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                #extract the (optional) key and value and print

                print(f"Consumed event from topic{msg.topic()}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}")
    except KeyboardInterrupt:
        pass
    finally:
        #leave group and commit final offsets
        consumer.close()
