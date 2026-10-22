from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    avg,
    count,
    round as spark_round
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType
)

import os
import csv
from datetime import datetime, timezone

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("AirBloom-AirQualityStreaming")
    .master("local[2]")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# --------------------------------------------------
# 2. DEFINE KAFKA JSON SCHEMA
# --------------------------------------------------

schema = StructType([
    StructField("City", StringType(), True),
    StructField("Datetime", StringType(), True),

    StructField("PM2.5", DoubleType(), True),
    StructField("PM10", DoubleType(), True),

    # Additional harmful pollutants
    StructField("NO2", DoubleType(), True),
    StructField("SO2", DoubleType(), True),
    StructField("CO", DoubleType(), True),
    StructField("O3", DoubleType(), True),

    StructField("AQI", DoubleType(), True),
    StructField("AQI_Bucket", StringType(), True),
    StructField("streamed_at", StringType(), True)
])

# --------------------------------------------------
# 3. READ KAFKA STREAM
# --------------------------------------------------

kafka_stream = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "kafka:29092"
    )
    .option("subscribe", "air_quality_data")
    .option("startingOffsets", "latest")
    .load()
)

# --------------------------------------------------
# 4. CONVERT JSON TO SPARK COLUMNS
# --------------------------------------------------

air_quality = (
    kafka_stream
    .selectExpr(
        "CAST(value AS STRING) AS json_value"
    )
    .select(
        from_json(
            col("json_value"),
            schema
        ).alias("data")
    )
    .select("data.*")
    .filter(
        col("City").isNotNull()
        & col("`PM2.5`").isNotNull()
        & col("PM10").isNotNull()
        & col("AQI").isNotNull()
    )
)

# --------------------------------------------------
# 5. CALCULATE CITY-WISE AVERAGES
# --------------------------------------------------

analytics = (
    air_quality
    .groupBy("City")
    .agg(
        count("*").alias("Total_Records"),

        spark_round(
            avg(col("`PM2.5`")), 2
        ).alias("Avg_PM25"),

        spark_round(
            avg(col("PM10")), 2
        ).alias("Avg_PM10"),

        spark_round(
            avg(col("NO2")), 2
        ).alias("Avg_NO2"),

        spark_round(
            avg(col("SO2")), 2
        ).alias("Avg_SO2"),

        spark_round(
            avg(col("CO")), 2
        ).alias("Avg_CO"),

        spark_round(
            avg(col("O3")), 2
        ).alias("Avg_O3"),

        spark_round(
            avg(col("AQI")), 2
        ).alias("Avg_AQI")
    )
)

# --------------------------------------------------
# 6. OUTPUT FILE PATHS
# --------------------------------------------------

OUTPUT_FILE = (
    "/opt/spark-output/air_quality_analytics.csv"
)

HISTORY_FILE = (
    "/opt/spark-output/history/aqi_history.csv"
)

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

os.makedirs(
    os.path.dirname(HISTORY_FILE),
    exist_ok=True
)

# --------------------------------------------------
# 7. SAVE ANALYTICS TO CSV
# --------------------------------------------------

def save_analytics(batch_df, batch_id):

    rows = batch_df.orderBy("City").collect()

    temp_file = OUTPUT_FILE + ".tmp"

    columns = [
        "City",
        "Total_Records",
        "Avg_PM25",
        "Avg_PM10",
        "Avg_NO2",
        "Avg_SO2",
        "Avg_CO",
        "Avg_O3",
        "Avg_AQI"
    ]

    # Save latest city-wise analytics
    with open(
        temp_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(columns)

        for row in rows:
            writer.writerow([
                row[column]
                for column in columns
            ])

    # Replace previous output atomically
    os.replace(
        temp_file,
        OUTPUT_FILE
    )

    # ----------------------------------------------
    # SAVE LIVE AQI HISTORY
    # ----------------------------------------------

    file_exists = os.path.exists(
        HISTORY_FILE
    )

    with open(
        HISTORY_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if (
            not file_exists
            or os.path.getsize(HISTORY_FILE) == 0
        ):
            writer.writerow([
                "Timestamp",
                "City",
                "Avg_AQI"
            ])

        timestamp = (
            datetime.now(timezone.utc).isoformat()
        )

        for row in rows:

            writer.writerow([
                timestamp,
                row["City"],
                row["Avg_AQI"]
            ])

    print(
        f"Batch {batch_id}: "
        f"Saved analytics for {len(rows)} cities"
    )

# --------------------------------------------------
# 8. START SPARK STRUCTURED STREAMING
# --------------------------------------------------

query = (
    analytics.writeStream
    .outputMode("complete")
    .foreachBatch(save_analytics)
    .trigger(
        processingTime="10 seconds"
    )
    .start()
)

print("------------------------------------")
print("AirBloom Spark Streaming Started!")
print("Monitoring:")
print("PM2.5, PM10, NO2, SO2, CO, O3, AQI")
print("------------------------------------")
print("Waiting for Kafka air quality records...")

query.awaitTermination()
