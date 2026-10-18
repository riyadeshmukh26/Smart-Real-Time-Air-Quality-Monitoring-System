
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Real-Time Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "output" / "air_quality_analytics.csv"

st.title("🌍 Real-Time Air Quality Monitoring Dashboard")
st.caption("Apache Kafka + Apache Spark + Streamlit")
st.info("Historical air quality data replayed as a simulated real-time stream.")

@st.fragment(run_every="5s")
def show_dashboard():
    if not DATA_FILE.exists():
        st.warning("Waiting for Spark to generate analytics...")
        return

    try:
        df = pd.read_csv(DATA_FILE)
    except (pd.errors.EmptyDataError, OSError):
        st.warning("Waiting for updated analytics...")
        return

    if df.empty:
        st.warning("Waiting for air quality records...")
        return

    cities = sorted(df["City"].unique().tolist())

    selected_city = st.selectbox(
        "Select City",
        cities,
        key="selected_city"
    )

    city_data = df[df["City"] == selected_city].iloc[0]

    st.subheader(f"Air Quality Overview — {selected_city}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Average AQI", f"{city_data['Avg_AQI']:.2f}")
    col2.metric("PM2.5", f"{city_data['Avg_PM25']:.2f}")
    col3.metric("PM10", f"{city_data['Avg_PM10']:.2f}")
    col4.metric("Records Processed", int(city_data["Total_Records"]))

    aqi = city_data["Avg_AQI"]

    if aqi <= 50:
        category = "Good 🟢"
    elif aqi <= 100:
        category = "Satisfactory 🟡"
    elif aqi <= 200:
        category = "Moderate 🟠"
    elif aqi <= 300:
        category = "Poor 🔴"
    elif aqi <= 400:
        category = "Very Poor 🟣"
    else:
        category = "Severe ⚫"

    st.subheader("Air Quality Status")
    st.write(f"**{category}**")

    st.subheader("Pollutant Levels")

    pollutant_df = pd.DataFrame({
        "Pollutant": ["PM2.5", "PM10"],
        "Concentration": [
            city_data["Avg_PM25"],
            city_data["Avg_PM10"]
        ]
    })

    fig = px.bar(
        pollutant_df,
        x="Pollutant",
        y="Concentration",
        color="Pollutant",
        title=f"Average Pollutant Concentrations — {selected_city}",
        labels={"Concentration": "Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("City-wise AQI Comparison")

    comparison = px.bar(
        df,
        x="City",
        y="Avg_AQI",
        color="Avg_AQI",
        title="Average AQI by City"
    )
    st.plotly_chart(comparison, use_container_width=True)

    st.subheader("Processed Air Quality Data")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption("Dashboard automatically refreshes every 5 seconds.")

show_dashboard()
