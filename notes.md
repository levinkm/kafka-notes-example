# Event

-   This is a combination of notification used to trigger other activities
-   They are usualy represented in a key value pair. This event can be serialized or deserialized based on the language being used. This can be to JSON, ProtBuff etc

-   The key in a Kafka message is a just an identifier.

# Topics

-   Fundamental unit of event organissation. It is like a table consisting different events.
-   The same kinds of events can be transformed using the key.
-   They can be refered to as logs but not queues. Has two characteristics.
    1.  Appends only
    2.  Can only seek by offset and not indexed
-   Events in a topic are immutable.
-   Topics are fundamentaly durable. Can be configured the messames to expire after they have reached a certain age or limit.

## Topic Partitions

-   Kafka gives us ability to pertition topics into partitons.
-   The messages being created is being distributed to this partitions based on the keys provided. (keeping in mind that messages in kafka are in form of key-value pairs)
-   if the massages do not have a key then they are distributed to the partitions in a round-robin manner.
-   It allows Kafka to put the massages with the same key to land in the same partitons. Hence preserving ordering by key.

# Brokers

A computer, instance, or container running the Kafka process.

-   Each broker manages partions and handles write and read requests to the partions.
-   manages replication of partions. They are kept simply for easy understanding snd scalling.

# Kafka Replication

It can be riskier to store data in partions under one broker. This is because this brokers are suscetible to failier. To monouver around this, we will need to copy partition data to other several brokers to keep ot safe. This copies are called Follower replicas while the main Broker is called leader replica.

-   in general, writes and reads happens at the leader broker.

# Kafka Producers

-   This is where most developers spend their time.
    partioning lives in the producer. It decides wherer to place the key value messages produced
-   is responsible for:
    1.  partition assignment
    2.  Batch events for improved throughput
    3.  Compression
    4.  Retries
    5.  Responsible callbacks
    6.  Transaction handling

### producer configuration

```python
producer = Producer(config)
```

-   **acks** -> this is used to determine the level of acknowledgeent reqiored before returning from produce request, (0,1,all). The default value is "all"
-   **batch.size** -> number of bytes that will be batched before sending produce request. Default value is 16384.
-   **linger.ms** -> Number of milliseconds to wait for batch before sending produce request. Default 0.
-   **compression.type** -> Algorithm used to compress data sent to the broker. can be set to _None_, _gzip_, _snapy_, _lz4_, or _zstd_ . Default is _None_
-   **retries** -> Number od times to retry a request that failed for potentially transient reasons.
-   **delivery.timeout.ms** -> This is the time limit for overal produce request. Can also be used to limit retries. Default value is 120,000ms (2 mins).
-   **transactional.id** -> A unique id for the producer that enables transaction recovery across multiple sessions of a single producer instance. Default is _None_
-   **enable.idempotence** -> When set to _True_, the producer adds a unique sequence number to messages. Default is _True_. This ensures that only one copy if this message is written to the stream.

#### Key Mothods of the producer class

1. produce() :
   Below is what we use to send message to topics.

```python

producer.produce(topic, [val],[key],[partition],[on_delivery],[timestamp],[headers])

# example

for i in range(10):
	producer.produce("bookings",{"user_id": "34342ksdf-eww","booked": "True"}, str(i), on_delivery = callback, headers={'foo':'bar'})

produce.flush()

```

-   In the above code we only passed the topic(_which is required_), the value , the key, on-delivery and headers. It is not amust to pass the partiton key since the key provided can be used to determine the partiton where the value will be placed.
-   This function will also perfom compression if configured and also perfom retries if any network issues is experinced.
-   The produce method is asynchronas, to ensure that all the current produced requests are complete we need to call the _produce.flush()_ method.

2. init*transactions() -> used to initialize transactions handling for this producer instance. parameters that can be passed is \_timeout*.

3. begin_transactions() -> used to begin a new transaction.

4. commit*transaction() -> Flush any active produce requests and mark transaction as commited. accepts \_timeout* as the parameter.

5. abort*transaction() -> used to purge all produce requests in this transaction and mark transaction as aborted. takes \_timeout* as the parameter.

6. send*offsets_to_transaction() -> Used to communicate with consumer group when transsaction includes producers and consumers. Takes 3 parameters: \_offsets*, _group_metadata_, _timeout_.

# Kafka Consumers

These are like components subscribed to a topic. They consume events posted to the topic by the producer.
In Kafka reading a message does not get it destroyed, instead it still remains there for other componets that might want to use it later.
Many consumers can read from one topic.
A single instance of a consumer will receive messages from all the partions of the topic it is subscribed to.
If there is a second instance of the consumer application then, the partitoning are distributed equaly to the consumers. This is called **Reballancing**.
This alllows scalling and error handling by default. Theres is nothing required to make this scalling happen.
This rebalancing forms the backborn of several features of kafka.
The consumer keeps track of completed events that has succesfully been processed. this can be done by us or automatically, depending on the config property.

### Consumer Constructor

Just like the producer. it takes the config dictionary. the config also has the bootsrap server of the broker to connect to.

```python
consumer = Consumer(config)
```

#### Consumer Configurations

1. group.id -> Uniquely identifies this application so that additional instance are included in a consumer group. 2. outo.offset.reset -> Determines offset to begin consuming at if no valid stored offset os available. The defailt value is _latest_.
2. enable.auto.commit -> if true, periodically commit offsets in the background. The default value is _true_. The recomended way is to set this value to false and commit the offsets manualy.
3. isolation.level -> used in transactional processing. (_read_uncommitted_, _read_committed_). The default value is _read_committed_. when set to _read_uncommitted_ value, the consumer reads all the events that were uncommited including those that were aborted.

#### Subscribe ti Topics

```python
consumer.subscribe(['bookings'],on_assign=assignment_callback)

def assignment_callback(consumer,topic_partitions):
	for tp in topic_partions:
		print(tp.topic)
		print(tp.partiton)
		print(tp.offset)

while True:
	event = consumer.poll(timeout=1.0)
	if event is None:
		continue
	if event.error():
		# handle error
	else:
		# process event

```

#### Consumer - Message Class

it has the following methods:

1. error() -> returns KafkaError or None
2. key() -> returns a str, bytes or None
3. value() -> returns str, bytes or None
4. headers() -> returns Lists of tuples (key, value)
5. timestamp() -> returns a Tuple of timestamp type (TIMESTAMP_CREATE_TIME or TIMESTAMP_LOG_APPEND_TIME) and value
6. topic() -> returns str or None
7. partition() -> returns int or None
8. offset() -> returns int or None

#### Consumer - Process Events

```python

while True:
	event = comsumer.poll(timeout=1.0)
	if event is None:
                continue
	if event.error():
                # handle error
        else:
            key = event.key().decode('utf8')
		    val = event.value().decode('utf8')
		    print(f'Received {val} with key of {key}')

		commit.commit(event) # to coomit the offset if auto commit is set to false.


```

## Confluent Schemas registry

### Serializers

    - converts data into bytes to be stored in kafka topic

```python
serializer = JSONSerializer(sr_client,schema_registry_client, to_dict=obj_to_dict)

key = string_serializer(str(uuid4())),
val = serializer(obj, SerializationContext(topic, MessageField.VALUE))

produce.produce(topic = topic, key = key, value = val)

```

### Deserializers

-   Converts bytes from Kafka topics into usable data

```python
deserializer = JSONDeserializer(sr_client, from_dict = dict_to_obj)

obj = deserilizer(event.value(), serializationContext(event.topic(), MessageField.VALUE))


```

### SchemaRegistryClient

-   Provides access to the schema registry

    ```python
    sr_client = SchemaRegistryClient({
    	'url' : '<schema Registry endpoint >'
    	'basic.auth.user.info':'<SR_UserName: SR_Password>'
    })

    ```

# Kafka Ecosytem

## Kafka connect

This is an ecosystem of plugable connectors
On the other hand it is a client application.
This is an application tunning outside the kafka clusters. It abstract alot of code connectors from the user.
Connect worker runs one or more workers.
Source connectors - act as producers.
Sink connectors - act as consumers.
