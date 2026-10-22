
import pandas as pd
import json
import time
from kafka import KafkaProducer

# --------------------------------------------------
# 1. CONNECT TO APACHE KAFKA
# --------------------------------------------------

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(
        v, allow_nan=False
    ).encode("utf-8")
)

# --------------------------------------------------
# 2. READ CLEANED DATASET
# --------------------------------------------------

df = pd.read_csv("city_hour_cleaned.csv")

print("Dataset loaded successfully!")
print("Total records:", len(df))

# --------------------------------------------------
# 3. SELECT INDIAN CITIES
# --------------------------------------------------

selected_cities = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Jaipur"
]

df = df[df["City"].isin(selected_cities)].copy()

# Sort historical records within each city
df = df.sort_values(["City", "Datetime"])

# Assign sequence numbers
df["city_record_number"] = (
    df.groupby("City").cumcount()
)

# Interleave records from different cities
df = df.sort_values([
    "city_record_number",
    "City"
])

df = df.drop(columns=["city_record_number"])

# --------------------------------------------------
# 4. POLLUTANTS TO MONITOR
# --------------------------------------------------

pollutants = [
    "PM2.5",
    "PM10",
    "NO2",
    "SO2",
    "CO",
    "O3"
]

print("\nMonitoring pollutants:", pollutants)
print("Selected cities:", selected_cities)
print("Total selected records:", len(df))
print("\nStarting simulated real-time streaming...\n")

# --------------------------------------------------
# 5. SEND DATA TO KAFKA
# --------------------------------------------------

try:

    for index, (_, row) in enumerate(
        df.iterrows(),
        start=1
    ):

        # Convert missing values to None
        record = {
            key: (
                None
                if pd.isna(value)
                else value.item()
                if hasattr(value, "item")
                else value
            )
            for key, value in row.to_dict().items()
        }

        # Preserve original historical timestamp
        record["original_datetime"] = (
            record.get("Datetime")
        )

        # Add current streaming timestamp
        record["streamed_at"] = (
            pd.Timestamp.now(tz="UTC").isoformat()
        )

        # Publish record to Kafka topic
        producer.send(
            "air_quality_data",
            value=record
        )

        producer.flush()

        # Display all pollutants in terminal
        print(
            f"Sent record {index}: "
            f"{record.get('City')} | "
            f"PM2.5: {record.get('PM2.5')} | "
            f"PM10: {record.get('PM10')} | "
            f"NO2: {record.get('NO2')} | "
            f"SO2: {record.get('SO2')} | "
            f"CO: {record.get('CO')} | "
            f"O3: {record.get('O3')} | "
            f"AQI: {record.get('AQI')}"
        )

        # Simulate real-time sensor readings
        time.sleep(2)

except KeyboardInterrupt:

    print("\nStreaming stopped by user.")

finally:

    producer.close()
