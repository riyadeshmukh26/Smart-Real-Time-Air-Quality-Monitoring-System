
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, avg, count, round as spark_round
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType
)

# Create Spark Session
spark = (
    SparkSession.builder
    .appName("AirQualityStreaming")
    .master("local[2]")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Define incoming Kafka JSON schema
schema = StructType([
    StructField("City", StringType(), True),
    StructField("Datetime", StringType(), True),
    StructField("PM2.5", DoubleType(), True),
    StructField("PM10", DoubleType(), True),
    StructField("AQI", DoubleType(), True),
    StructField("AQI_Bucket", StringType(), True),
    StructField("streamed_at", StringType(), True)
])

# Read streaming messages from Kafka
kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "air_quality_data")
    .option("startingOffsets", "latest")
    .load()
)

# Convert Kafka JSON messages to columns
air_quality = (
    kafka_stream
    .selectExpr("CAST(value AS STRING) AS json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
    
.filter(
    col("City").isNotNull()
    & col("`PM2.5`").isNotNull()
    & col("PM10").isNotNull()
    & col("AQI").isNotNull()
)

)

# Calculate average pollution values per city
analytics = (
    air_quality
    .groupBy("City")
    .agg(
        count("*").alias("Total_Records"),
        spark_round(avg(col("`PM2.5`")), 2).alias("Avg_PM25"),
        spark_round(avg("PM10"), 2).alias("Avg_PM10"),
        spark_round(avg("AQI"), 2).alias("Avg_AQI")
    )
)

# Display updated analytics in terminal

import os

OUTPUT_FILE = "/opt/spark-output/air_quality_analytics.csv"


import csv
import os

OUTPUT_FILE = "/opt/spark-output/air_quality_analytics.csv"
from datetime import datetime, timezone
def save_analytics(batch_df, batch_id):
    rows = batch_df.orderBy("City").collect()
    temp_file = OUTPUT_FILE + ".tmp"

    columns = [
        "City",
        "Total_Records",
        "Avg_PM25",
        "Avg_PM10",
        "Avg_AQI"
    ]

    with open(temp_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)

        for row in rows:
            writer.writerow([row[column] for column in columns])

    os.replace(temp_file, OUTPUT_FILE)

    # Save timestamped AQI history for live trend graph
    history_file = "/opt/spark-output/history/aqi_history.csv"

    file_exists = os.path.exists(history_file)

    with open(history_file, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists or os.path.getsize(history_file) == 0:
            writer.writerow(["Timestamp", "City", "Avg_AQI"])

        timestamp = datetime.now(timezone.utc).isoformat()

        for row in rows:
            writer.writerow([
                timestamp,
                row["City"],
                row["Avg_AQI"]
            ])


    print(f"Batch {batch_id}: Saved {len(rows)} cities")



query = (
    analytics.writeStream
    .outputMode("complete")
    .foreachBatch(save_analytics)
    .trigger(processingTime="10 seconds")
    .start()
)


print("Spark Structured Streaming started!")
print("Waiting for Kafka air quality records...")

query.awaitTermination()
