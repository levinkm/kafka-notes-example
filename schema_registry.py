from confluent_kafka import


sr_client = SchemaRegistryClient({
	'url' : '<schema Registry endpoint >'
	'basic.auth.user.info':'<SR_UserName: SR_Password>'
})
