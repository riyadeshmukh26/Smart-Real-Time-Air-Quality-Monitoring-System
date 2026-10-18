
import pandas as pd

# Load original dataset
df = pd.read_csv("city_hour.csv")

print("Original records:", len(df))

# Remove rows missing important measurements
df_clean = df.dropna(
    subset=["PM2.5", "PM10", "AQI"]
).copy()

# Sort readings by city and historical time
df_clean["Datetime"] = pd.to_datetime(
    df_clean["Datetime"],
    errors="coerce"
)

df_clean = df_clean.dropna(subset=["Datetime"])
df_clean = df_clean.sort_values(
    by=["City", "Datetime"]
)

# Save cleaned dataset
df_clean.to_csv("city_hour_cleaned.csv", index=False)

print("Cleaned records:", len(df_clean))
print("Removed records:", len(df) - len(df_clean))
print("\nSample cleaned records:")
print(
    df_clean[
        ["City", "Datetime", "PM2.5", "PM10", "AQI"]
    ].head(10)
)
