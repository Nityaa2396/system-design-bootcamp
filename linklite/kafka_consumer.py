from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'transcript-lines',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='transcript-display-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("Listening for transcript lines...")

for message in consumer:
    line = message.value
    print(f"[{line['speaker']}] {line['text']} ({line['timestamp']})")