# 🌿 Smart Real-Time Air Quality Monitoring System

A real-time air quality monitoring and analytics system built using **Apache Kafka, Apache Spark, Python, and Streamlit**.

The project simulates live air quality readings using a historical Indian air quality dataset, processes incoming data using Spark Structured Streaming, and displays AQI and pollutant insights through an interactive dashboard.

## 📌 Project Overview

Air pollution is a major environmental concern in urban areas. This project demonstrates how real-time data streaming and analytics can be used to monitor air quality across multiple Indian cities.

The system uses historical air quality measurements replayed as simulated live readings, rather than physical IoT sensors or a live government API.

## 🎯 Objectives

- Simulate real-time air quality data streaming.
- Process streaming data using Apache Kafka and Apache Spark.
- Monitor AQI, PM2.5, and PM10 levels.
- Compare air quality across different Indian cities.
- Visualize AQI trends using an interactive dashboard.
- Classify air quality into different pollution categories.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data preprocessing and Kafka Producer |
| Apache Kafka | Real-time message streaming |
| Apache Spark | Streaming data processing and analytics |
| Streamlit | Interactive web dashboard |
| Pandas | Data manipulation |
| Plotly | Interactive visualizations |
| Docker | Running Kafka and Spark containers |
| CSV | Dataset and processed analytics storage |

## 🏗️ System Architecture

```text
Historical Air Quality Dataset (CSV)
                 |
                 v
         Data Preprocessing
                 |
                 v
        Python Kafka Producer
                 |
                 v
          Apache Kafka
       (air_quality_data)
                 |
                 v
      Spark Structured Streaming
                 |
                 v
       AQI & Pollutant Analytics
                 |
                 v
         Processed CSV Files
                 |
                 v
        Streamlit Dashboard
```

## 🌆 Cities Monitored

- Delhi
- Mumbai
- Bengaluru
- Hyderabad
- Jaipur

## ✨ Features

- Simulated real-time air quality streaming
- Automatic dashboard refresh every 5 seconds
- City-wise AQI monitoring
- PM2.5 and PM10 concentration analysis
- AQI classification into six categories
- Interactive pollutant comparison charts
- City-wise AQI comparison
- Live streaming AQI trend visualization
- Records processed counter
- CSV-based analytics and history storage

## 📂 Project Structure

```text
mini_project_dasss/
│
├── city_hour.csv                 # Original dataset (not on GitHub)
├── city_hour_cleaned.csv         # Cleaned dataset (not on GitHub)
├── data_cleaning.py              # Dataset preprocessing
├── kafka_producer.py             # Kafka Producer
├── dashboard.py                  # Streamlit dashboard
├── docker-compose.yml            # Kafka and Spark configuration
├── spark/
│   └── spark_streaming.py        # Spark streaming analytics
├── output/
│   ├── air_quality_analytics.csv # Latest aggregated results
│   └── history/
│       └── aqi_history.csv       # Streaming AQI history
├── .gitignore
└── README.md
```

The dataset and generated output files are excluded from GitHub. The `output/` directory is created locally when preparing and running the project.

## 📊 Dataset

The project uses the **Air Quality Data in India (2015–2020)** dataset, available on Kaggle.

Dataset source: [Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india)

The dataset contains historical measurements such as:

- City
- Date and time
- PM2.5
- PM10
- AQI
- AQI category

**Note:** Download or obtain `city_hour.csv` and place it in the project root directory before running data preprocessing.

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/riyadeshmukh26/Smart-Real-Time-Air-Quality-Monitoring-System.git
cd Smart-Real-Time-Air-Quality-Monitoring-System
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, the activation command is different.

### 3. Install Python dependencies

```bash
pip install pandas streamlit plotly kafka-python
```

### 4. Prepare the dataset

Place `city_hour.csv` in the project root directory.

Run:

```bash
python data_cleaning.py
```

This creates `city_hour_cleaned.csv`.

### 5. Start Kafka and Spark containers

Ensure Docker Desktop is running.

```bash
docker compose up -d
```

### 6. Create the Kafka topic

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --create \
  --if-not-exists \
  --topic air_quality_data \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

### 7. Start Spark Streaming

Create the output directories if they do not exist:

```bash
mkdir -p output/history
```

In a new terminal, run:

```bash
docker exec -it spark \
  /opt/spark/bin/spark-submit \
  --master "local[2]" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1 \
  /opt/spark-apps/spark_streaming.py
```

### 8. Start Kafka Producer

In another terminal, with the Python virtual environment activated:

```bash
python kafka_producer.py
```

### 9. Launch the Streamlit dashboard

In another terminal:

```bash
streamlit run dashboard.py
```

Open:

http://localhost:8501

## 📈 AQI Categories

| AQI Range | Category |
|---|---|
| 0–50 | Good |
| 51–100 | Satisfactory |
| 101–200 | Moderate |
| 201–300 | Poor |
| 301–400 | Very Poor |
| 401–500 | Severe |

## 💾 Data Storage

The project currently uses CSV-based storage rather than a traditional database.

- `city_hour.csv` — original dataset
- `city_hour_cleaned.csv` — preprocessed dataset
- `output/air_quality_analytics.csv` — latest city-wise aggregate results
- `output/history/aqi_history.csv` — timestamped cumulative average AQI snapshots

Kafka stores messages in its broker storage, while Spark processes incoming records and writes aggregated results to CSV.

## ⚠️ Important Note

This project is a prototype that replays historical air quality readings as a simulated live stream.

The displayed AQI values are cumulative averages of processed historical records and **must not be interpreted as current real-world air quality conditions**.

The trend graph uses streaming processing timestamps, not the original measurement dates.

## 🔮 Future Enhancements

- AQI pollution alerts
- Health recommendations based on AQI
- Live streaming connection status
- Historical filtering and downloadable reports
- Database integration
- Integration with actual IoT sensors or live air quality APIs

## 👩‍💻 Collaboration

This project is developed collaboratively using Git and GitHub.

Contributors can create separate branches, implement features, and submit pull requests for review.

## 📄 Project Status

**Under Development** — Core streaming, analytics, and dashboard functionality implemented.