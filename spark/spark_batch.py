
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    to_timestamp,
    year,
    month,
    to_date,
    avg,
    count
)
from pathlib import Path
import csv

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

INPUT_FILE = "/opt/spark-data/city_hour_cleaned.csv"
OUTPUT_DIR = Path("/opt/spark-output/time_machine")

# --------------------------------------------------
# 2. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("AirBloom-Time-Machine-Batch")
    .master("local[2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# --------------------------------------------------
# 3. READ HISTORICAL DATASET
# --------------------------------------------------

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(INPUT_FILE)
)

print("Historical dataset loaded successfully.")

# --------------------------------------------------
# 4. DATA CLEANING AND PREPROCESSING
# --------------------------------------------------

df = (
    df
    .withColumn(
        "Historical_DateTime",
        to_timestamp(col("Datetime"))
    )
    .withColumn(
        "Year",
        year(col("Historical_DateTime"))
    )
    .withColumn(
        "Month",
        month(col("Historical_DateTime"))
    )
    .withColumn(
        "Date",
        to_date(col("Historical_DateTime"))
    )
    .withColumn(
        "AQI",
        col("AQI").cast("double")
    )
    .withColumn(
        "PM2.5",
        col("`PM2.5`").cast("double")
    )
    .withColumn(
        "PM10",
        col("PM10").cast("double")
    )

    # Additional harmful pollutants

    .withColumn(
        "NO2",
        col("NO2").cast("double")
    )
    .withColumn(
        "SO2",
        col("SO2").cast("double")
    )
    .withColumn(
        "CO",
        col("CO").cast("double")
    )
    .withColumn(
        "O3",
        col("O3").cast("double")
    )

    .filter(
        col("City").isNotNull()
        & col("Historical_DateTime").isNotNull()
    )
)

print("Data preprocessing completed.")

# --------------------------------------------------
# 5. YEARLY AIR QUALITY ANALYTICS
# --------------------------------------------------

yearly = (
    df.groupBy("City", "Year")
    .agg(
        avg(col("AQI")).alias("Avg_AQI"),
        avg(col("`PM2.5`")).alias("Avg_PM25"),
        avg(col("PM10")).alias("Avg_PM10"),

        avg(col("NO2")).alias("Avg_NO2"),
        avg(col("SO2")).alias("Avg_SO2"),
        avg(col("CO")).alias("Avg_CO"),
        avg(col("O3")).alias("Avg_O3"),

        count(col("AQI")).alias("Total_Records")
    )
    .orderBy("City", "Year")
)

# --------------------------------------------------
# 6. MONTHLY AIR QUALITY ANALYTICS
# --------------------------------------------------

monthly = (
    df.groupBy("City", "Year", "Month")
    .agg(
        avg(col("AQI")).alias("Avg_AQI"),
        avg(col("`PM2.5`")).alias("Avg_PM25"),
        avg(col("PM10")).alias("Avg_PM10"),

        avg(col("NO2")).alias("Avg_NO2"),
        avg(col("SO2")).alias("Avg_SO2"),
        avg(col("CO")).alias("Avg_CO"),
        avg(col("O3")).alias("Avg_O3"),

        count(col("AQI")).alias("Total_Records")
    )
    .orderBy("City", "Year", "Month")
)

# --------------------------------------------------
# 7. DAILY AIR QUALITY ANALYTICS
# --------------------------------------------------

daily = (
    df.groupBy("City", "Date")
    .agg(
        avg(col("AQI")).alias("Avg_AQI"),
        avg(col("`PM2.5`")).alias("Avg_PM25"),
        avg(col("PM10")).alias("Avg_PM10"),

        avg(col("NO2")).alias("Avg_NO2"),
        avg(col("SO2")).alias("Avg_SO2"),
        avg(col("CO")).alias("Avg_CO"),
        avg(col("O3")).alias("Avg_O3"),

        count(col("AQI")).alias("Total_Records")
    )
    .orderBy("City", "Date")
)

# --------------------------------------------------
# 8. SAVE SPARK PROCESSED DATA AS CSV
# --------------------------------------------------

def save_csv(dataframe, filename):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = OUTPUT_DIR / filename

    columns = dataframe.columns

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Write column names
        writer.writerow(columns)

        # Write Spark processed records
        for row in dataframe.toLocalIterator():
            writer.writerow([
                row[column] for column in columns
            ])

    print(f"Saved successfully: {output_path}")


# --------------------------------------------------
# 9. GENERATE OUTPUT FILES
# --------------------------------------------------

save_csv(
    yearly,
    "yearly_air_quality.csv"
)

save_csv(
    monthly,
    "monthly_air_quality.csv"
)

save_csv(
    daily,
    "daily_air_quality.csv"
)

print("------------------------------------")
print("AirBloom Spark Batch Processing Done!")
print("All three CSV files generated.")
print("Pollutants: PM2.5, PM10, NO2, SO2, CO, O3")
print("------------------------------------")

# --------------------------------------------------
# 10. STOP SPARK
# --------------------------------------------------

spark.stop()
