from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

transcript_lines = [
    {"speaker": "Alice", "text": "Good morning everyone.", "timestamp": "00:00:01"},
    {"speaker": "Bob", "text": "Thanks for joining the call.", "timestamp": "00:00:05"},
    {"speaker": "Alice", "text": "Let's go through the agenda.", "timestamp": "00:00:10"},
    {"speaker": "Bob", "text": "First item is the Q3 review.", "timestamp": "00:00:15"},
    {"speaker": "Alice", "text": "Agreed. Sales are up 20 percent.", "timestamp": "00:00:20"},
]

print("Sending transcript lines to Kafka...")

for line in transcript_lines:
    producer.send('transcript-lines', value=line)
    print(f"Sent: [{line['speaker']}] {line['text']}")
    time.sleep(1)

producer.flush()
print("Done.")