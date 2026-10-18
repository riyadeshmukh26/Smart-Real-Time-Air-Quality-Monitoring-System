
import pandas as pd
import json
import time
from kafka import KafkaProducer

# Connect to Apache Kafka
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(
        v, allow_nan=False
    ).encode("utf-8")
)

# Read cleaned Indian Air Quality Dataset
df = pd.read_csv("city_hour_cleaned.csv")

print("Dataset loaded successfully!")
print("Total records:", len(df))

# Select 5 Indian cities
selected_cities = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Jaipur"
]

# Filter dataset for selected cities
df = df[df["City"].isin(selected_cities)].copy()

# Sort historical readings within each city
df = df.sort_values(["City", "Datetime"])

# Assign sequence number to each city's records
df["city_record_number"] = df.groupby("City").cumcount()

# Interleave readings from different cities
df = df.sort_values(["city_record_number", "City"])

# Remove temporary column
df = df.drop(columns=["city_record_number"])

print("Selected cities:", selected_cities)
print("Total selected records:", len(df))
print("Starting simulated real-time streaming...\n")

# Send historical records as simulated live readings
try:
    for index, (_, row) in enumerate(df.iterrows(), start=1):

        # Replace remaining missing values with None
        record = {
            key: None if pd.isna(value) else value
            for key, value in row.to_dict().items()
        }

        # Preserve original historical timestamp
        record["original_datetime"] = record.get("Datetime")

        # Add current streaming timestamp
        record["streamed_at"] = pd.Timestamp.now(
            tz="UTC"
        ).isoformat()

        # Send record to Kafka
        producer.send(
            "air_quality_data",
            value=record
        )
        producer.flush()

        print(
            f"Sent record {index}: "
            f"{record.get('City')} | "
            f"PM2.5: {record.get('PM2.5')} | "
            f"PM10: {record.get('PM10')} | "
            f"AQI: {record.get('AQI')}"
        )

        # Simulate live sensor readings
        time.sleep(2)

except KeyboardInterrupt:
    print("\nStreaming stopped by user.")

finally:
    producer.close()
