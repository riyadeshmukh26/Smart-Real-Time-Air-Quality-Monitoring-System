
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page settings
st.set_page_config(
    page_title="AirBloom | Air Quality Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = Path(__file__).parent / "output" / "air_quality_analytics.csv"

HISTORY_FILE = (
    Path(__file__).parent
    / "output"
    / "history"
    / "aqi_history.csv"
)

# Pastel styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(
            135deg,
            #FFF9F5 0%,
            #F3F9F6 50%,
            #F6F2FF 100%
        );
        color: #344054;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1350px;
    }

    h1, h2, h3 {
        color: #344054 !important;
        font-family: Arial, sans-serif;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #E8E8F0;
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 8px 25px rgba(130, 140, 160, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        color: #667085;
    }

    div[data-testid="stMetricValue"] {
        color: #344054;
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.75);
        border-radius: 22px;
        padding: 12px;
        border: 1px solid #E8E8F0;
    }

    .hero-card {
        background: linear-gradient(110deg, #DDF5E9, #EDE5FF);
        border-radius: 28px;
        padding: 30px 35px;
        margin-bottom: 25px;
        border: 1px solid #E8E8F0;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 750;
        color: #344054;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #667085;
        font-size: 16px;
    }

    .status-card {
        background: #FFFFFFCC;
        border: 1px solid #E8E8F0;
        border-radius: 20px;
        padding: 22px;
        margin: 15px 0;
    }

    .status-title {
        color: #667085;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .status-value {
        font-size: 24px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard header
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🌿 AirBloom</div>
    <div class="hero-subtitle">
        Breathe better with beautiful air quality insights.
        Real-time analytics powered by Apache Kafka & Spark.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "🌸 Historical Indian air quality readings replayed "
    "as a simulated live data stream."
)


def get_aqi_status(aqi):
    if aqi <= 50:
        return "Good", "#42A88C", "#E0F5EC"
    elif aqi <= 100:
        return "Satisfactory", "#76A55A", "#EEF6E2"
    elif aqi <= 200:
        return "Moderate", "#D5A03A", "#FFF4D8"
    elif aqi <= 300:
        return "Poor", "#E28762", "#FFE9DE"
    elif aqi <= 400:
        return "Very Poor", "#B76B9B", "#F7E6F2"
    else:
        return "Severe", "#B85D68", "#FFE5E8"


@st.fragment(run_every="5s")
def show_dashboard():

    if not DATA_FILE.exists():
        st.warning("Waiting for Spark analytics...")
        return

    try:
        df = pd.read_csv(DATA_FILE)
    except (pd.errors.EmptyDataError, OSError):
        st.warning("Waiting for updated data...")
        return

    if df.empty:
        st.info("Waiting for air quality records...")
        return

    cities = sorted(
        df["City"].dropna().unique().tolist()
    )

    selected_city = st.selectbox(
        "📍 Choose a city",
        cities,
        key="selected_city"
    )

    city_data = df[
        df["City"] == selected_city
    ].iloc[0]

    # Overview
    st.markdown(
        f"### ✨ Air Quality Overview — {selected_city}"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🌍 Average AQI",
        f"{city_data['Avg_AQI']:.2f}"
    )

    col2.metric(
        "🌫️ PM2.5",
        f"{city_data['Avg_PM25']:.2f} µg/m³"
    )

    col3.metric(
        "🍃 PM10",
        f"{city_data['Avg_PM10']:.2f} µg/m³"
    )

    col4.metric(
        "📊 Records Processed",
        int(city_data["Total_Records"])
    )

    # AQI status
    aqi = city_data["Avg_AQI"]

    status, color, background = get_aqi_status(aqi)

    st.markdown(
        f"""
        <div class="status-card"
             style="background:{background};">
            <div class="status-title">
                AVERAGE AIR QUALITY CATEGORY
            </div>
            <div class="status-value"
                 style="color:{color};">
                ● {status}
            </div>
            <div style="color:#667085; margin-top:8px;">
                Based on the average AQI of streamed
                historical records.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Air quality insights
    st.markdown("### 📊 Air Quality Insights")

    left, right = st.columns(2)

    with left:
        pollutant_df = pd.DataFrame({
            "Pollutant": ["PM2.5", "PM10"],
            "Concentration": [
                city_data["Avg_PM25"],
                city_data["Avg_PM10"]
            ]
        })

        fig1 = px.bar(
            pollutant_df,
            x="Pollutant",
            y="Concentration",
            color="Pollutant",
            color_discrete_map={
                "PM2.5": "#B8A5E8",
                "PM10": "#89CDB8"
            },
            title="Pollutant Concentrations",
            labels={
                "Concentration": "Average concentration (µg/m³)"
            }
        )

        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#344054",
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:
        fig2 = px.bar(
            df.sort_values("Avg_AQI"),
            x="City",
            y="Avg_AQI",
            color="Avg_AQI",
            color_continuous_scale=[
                "#9EDBC5",
                "#D8C5F2",
                "#F0B4B8"
            ],
            title="City-wise AQI Comparison"
        )

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#344054",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # Live AQI trend graph
    st.markdown("### 📈 Live AQI Trends")

    if HISTORY_FILE.exists():

        try:
            history_df = pd.read_csv(HISTORY_FILE)

            history_df["Timestamp"] = pd.to_datetime(
                history_df["Timestamp"],
                utc=True
            )

            # Show last 30 minutes of streaming history
            latest_time = history_df["Timestamp"].max()

            history_df = history_df[
                history_df["Timestamp"]
                >= latest_time - pd.Timedelta(minutes=30)
            ]

            # Filter selected city
            city_history = history_df[
                history_df["City"] == selected_city
            ].sort_values("Timestamp")

            if not city_history.empty:

                fig3 = px.line(
                    city_history,
                    x="Timestamp",
                    y="Avg_AQI",
                    markers=True,
                    title=(
                        f"Live Streaming AQI Trend — "
                        f"{selected_city}"
                    ),
                    labels={
                        "Timestamp": "Streaming Time (UTC)",
                        "Avg_AQI": "Average AQI"
                    }
                )

                fig3.update_traces(
                    line_color="#9B8AD0",
                    line_width=3
                )

                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#344054",
                    margin=dict(
                        l=20,
                        r=20,
                        t=60,
                        b=20
                    )
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

                st.caption(
                    "🕒 This graph shows the changing cumulative "
                    "average AQI as historical readings are replayed. "
                    "The X-axis represents streaming/processing time "
                    "(UTC), not the original measurement date."
                )

            else:
                st.info(
                    "Waiting for AQI history for this city."
                )

        except (
            pd.errors.EmptyDataError,
            OSError,
            ValueError
        ):
            st.info("Waiting for AQI history...")

    else:
        st.info(
            "AQI history file has not been created yet."
        )

    # Processed data table
    st.markdown("### 🌷 City Air Quality Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "🔄 Dashboard automatically refreshes every 5 seconds."
    )


show_dashboard()
