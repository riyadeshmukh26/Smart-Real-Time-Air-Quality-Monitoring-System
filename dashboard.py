
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import calendar

# ==================================================
# 1. PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="AirBloom | Air Quality Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "output" / "air_quality_analytics.csv"
HISTORY_FILE = BASE_DIR / "output" / "history" / "aqi_history.csv"

TIME_MACHINE_DIR = BASE_DIR / "output" / "time_machine"

YEARLY_FILE = TIME_MACHINE_DIR / "yearly_air_quality.csv"
MONTHLY_FILE = TIME_MACHINE_DIR / "monthly_air_quality.csv"
DAILY_FILE = TIME_MACHINE_DIR / "daily_air_quality.csv"

# ==================================================
# 2. POLLUTANT CONFIGURATION
# ==================================================

POLLUTANTS = {
    "PM2.5": {
        "column": "Avg_PM25",
        "unit": "µg/m³",
        "icon": "🌫️",
        "color": "#B8A5E8"
    },
    "PM10": {
        "column": "Avg_PM10",
        "unit": "µg/m³",
        "icon": "🍃",
        "color": "#89CDB8"
    },
    "NO₂": {
        "column": "Avg_NO2",
        "unit": "µg/m³",
        "icon": "🏭",
        "color": "#F2BD8E"
    },
    "SO₂": {
        "column": "Avg_SO2",
        "unit": "µg/m³",
        "icon": "💨",
        "color": "#E6A6C7"
    },
    "CO": {
        "column": "Avg_CO",
        "unit": "mg/m³",
        "icon": "🚗",
        "color": "#A8C4E8"
    },
    "O₃": {
        "column": "Avg_O3",
        "unit": "µg/m³",
        "icon": "☀️",
        "color": "#E8CE89"
    }
}

NUMERIC_COLUMNS = [
    "Avg_AQI",
    "Avg_PM25",
    "Avg_PM10",
    "Avg_NO2",
    "Avg_SO2",
    "Avg_CO",
    "Avg_O3",
    "Total_Records"
]

# Verify pollutant units with the original dataset documentation.

# ==================================================
# 3. PASTEL STYLING
# ==================================================

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
    background: rgba(255,255,255,0.85);
    border: 1px solid #E8E8F0;
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(130,140,160,0.08);
}

div[data-testid="stMetricLabel"] {
    color: #667085;
}

div[data-testid="stMetricValue"] {
    color: #344054;
}

div[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.75);
    border-radius: 22px;
    padding: 12px;
    border: 1px solid #E8E8F0;
}

.hero-card {
    background: linear-gradient(
        110deg,
        #DDF5E9,
        #EDE5FF
    );
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

# ==================================================
# 4. HEADER
# ==================================================

st.markdown("""
<div class="hero-card">
    <div class="hero-title">🌿 AirBloom</div>
    <div class="hero-subtitle">
        Breathe better with beautiful air quality insights.
        Streaming analytics powered by Apache Kafka & Spark.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "🌸 Historical Indian air quality readings replayed "
    "as a simulated live data stream."
)

# ==================================================
# 5. AQI CLASSIFICATION
# ==================================================

def get_aqi_status(aqi):

    if pd.isna(aqi):
        return "Unknown", "#667085", "#F2F4F7"

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


# ==================================================
# 6. POLLUTION ALERTS
# ==================================================

def get_pollution_alert(aqi):

    if aqi <= 50:
        return (
            "success",
            "Good Air Quality",
            "The average AQI is in the Good category."
        )

    elif aqi <= 100:
        return (
            "success",
            "Satisfactory Air Quality",
            "The average AQI is satisfactory."
        )

    elif aqi <= 200:
        return (
            "info",
            "Moderate Pollution",
            "Sensitive individuals should consider limiting "
            "prolonged outdoor activities."
        )

    elif aqi <= 300:
        return (
            "warning",
            "Poor Air Quality Alert",
            "Consider reducing prolonged outdoor activities."
        )

    elif aqi <= 400:
        return (
            "warning",
            "Very Poor Air Quality Alert",
            "Avoid prolonged outdoor exposure, especially "
            "for sensitive groups."
        )

    else:
        return (
            "error",
            "Severe Pollution Alert",
            "Avoid prolonged outdoor exposure and "
            "take additional precautions."
        )


# ==================================================
# 7. HEALTH RECOMMENDATIONS
# ==================================================

def get_health_recommendations(aqi):

    if aqi <= 50:
        return [
            "Normal outdoor activities are generally suitable.",
            "Continue maintaining healthy indoor air quality."
        ]

    elif aqi <= 100:
        return [
            "Most people can continue normal outdoor activities.",
            "People with respiratory sensitivities should monitor symptoms."
        ]

    elif aqi <= 200:
        return [
            "Sensitive individuals should consider reducing prolonged outdoor activities.",
            "Monitor air quality before extended outdoor exercise.",
            "Keep indoor spaces well maintained."
        ]

    elif aqi <= 300:
        return [
            "Reduce prolonged outdoor activities.",
            "Children, older adults and people with respiratory conditions should take extra precautions.",
            "Keep indoor air as clean as possible."
        ]

    elif aqi <= 400:
        return [
            "Avoid prolonged outdoor activities where possible.",
            "Sensitive individuals should minimize outdoor exposure.",
            "Keep windows closed when outdoor pollution is high."
        ]

    else:
        return [
            "Avoid unnecessary outdoor exposure.",
            "Consider staying indoors with suitable air filtration.",
            "Follow local public health advisories during actual severe pollution events."
        ]


# ==================================================
# 8. HELPER FUNCTIONS
# ==================================================

def format_pollutant(value, unit):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f} {unit}"


def prepare_numeric_data(df):

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:
            df[column] = float("nan")

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def style_plot(fig):

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#344054"
    )

    return fig


# ==================================================
# 9. POLLUTANT METRIC CARDS
# ==================================================

def show_pollutant_metrics(record):

    st.markdown("### 🧪 Harmful Pollutant Monitoring")

    names = list(POLLUTANTS.keys())

    for start in range(0, len(names), 3):

        cols = st.columns(3)

        for i, name in enumerate(names[start:start + 3]):

            config = POLLUTANTS[name]

            value = record.get(
                config["column"],
                float("nan")
            )

            cols[i].metric(
                f'{config["icon"]} {name}',
                format_pollutant(
                    value,
                    config["unit"]
                )
            )

    st.caption(
        "Values are averages of available measurements. "
        "Missing measurements are displayed as N/A."
    )


# ==================================================
# 10. AQI CATEGORY CARD
# FIXED: HTML NOW RENDERS CORRECTLY
# ==================================================

def show_aqi_category(aqi, historical=False):

    category, color, background = get_aqi_status(aqi)

    title = (
        "HISTORICAL AIR QUALITY CATEGORY"
        if historical
        else "AVERAGE AIR QUALITY CATEGORY"
    )

    description = (
        "Based on Spark-calculated historical average AQI."
        if historical
        else "Based on streamed historical measurements."
    )

    # HTML must start at the beginning of the line.
    # Indented HTML can appear as a code block in Streamlit.

    html = f"""
<div class="status-card" style="background:{background};">
    <div class="status-title">
        {title}
    </div>
    <div class="status-value" style="color:{color};">
        ● {category}
    </div>
    <div style="color:#667085;margin-top:8px;">
        {description}
    </div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ==================================================
# 11. ALERT DISPLAY
# ==================================================

def show_alert(aqi):

    alert_type, title, message = get_pollution_alert(aqi)

    text = f"**{title}** — {message}"

    if alert_type == "success":
        st.success(text)

    elif alert_type == "info":
        st.info(text)

    elif alert_type == "warning":
        st.warning(text)

    else:
        st.error(text)


# ==================================================
# 12. STREAMING STATUS
# ==================================================

def get_streaming_status(history_df):

    if history_df is None or history_df.empty:
        return "WAITING FOR DATA", "No history available", "off"

    timestamps = pd.to_datetime(
        history_df["Timestamp"],
        utc=True,
        errors="coerce"
    ).dropna()

    if timestamps.empty:
        return "WAITING FOR DATA", "No valid timestamps", "off"

    latest_timestamp = timestamps.max()

    now = pd.Timestamp.now(tz="UTC")

    elapsed_seconds = max(
        0,
        (now - latest_timestamp).total_seconds()
    )

    if elapsed_seconds <= 30:
        status = "LIVE"
        status_type = "live"

    elif elapsed_seconds <= 60:
        status = "DELAYED"
        status_type = "delayed"

    else:
        status = "OFFLINE / STALE"
        status_type = "off"

    if elapsed_seconds < 60:
        last_update = f"{int(elapsed_seconds)} seconds ago"

    elif elapsed_seconds < 3600:
        last_update = (
            f"{int(elapsed_seconds // 60)} minutes ago"
        )

    else:
        last_update = (
            f"{int(elapsed_seconds // 3600)} hours ago"
        )

    return status, last_update, status_type


# ==================================================
# 13. LOAD SPARK BATCH DATA
# ==================================================

@st.cache_data(
    show_spinner="Loading Spark processed historical data..."
)
def load_spark_batch_data(
    yearly_path,
    monthly_path,
    daily_path,
    yearly_mtime,
    monthly_mtime,
    daily_mtime
):

    yearly_df = pd.read_csv(yearly_path)
    monthly_df = pd.read_csv(monthly_path)
    daily_df = pd.read_csv(daily_path)

    for df in [yearly_df, monthly_df, daily_df]:
        prepare_numeric_data(df)

    yearly_df["Year"] = pd.to_numeric(
        yearly_df["Year"],
        errors="coerce"
    )

    monthly_df["Year"] = pd.to_numeric(
        monthly_df["Year"],
        errors="coerce"
    )

    monthly_df["Month"] = pd.to_numeric(
        monthly_df["Month"],
        errors="coerce"
    )

    daily_df["Date"] = pd.to_datetime(
        daily_df["Date"],
        errors="coerce"
    )

    daily_df["Year"] = daily_df["Date"].dt.year
    daily_df["Month"] = daily_df["Date"].dt.month

    return yearly_df, monthly_df, daily_df


# ==================================================
# 14. AIR QUALITY TIME MACHINE
# ==================================================

def show_time_machine():

    st.markdown("---")
    st.markdown("## ⏳ AirBloom Time Machine")

    st.markdown(
        "Explore historical pollution patterns using "
        "**Apache Spark Batch Processing** analytics."
    )

    required_files = [
        YEARLY_FILE,
        MONTHLY_FILE,
        DAILY_FILE
    ]

    missing_files = [
        file.name
        for file in required_files
        if not file.exists()
    ]

    if missing_files:

        st.warning(
            "Spark Batch Processing output files are missing."
        )

        st.code("\n".join(missing_files))

        st.info(
            "Run spark_batch.py to generate the "
            "daily, monthly and yearly CSV files."
        )

        return

    try:

        yearly_df, monthly_df, daily_df = (
            load_spark_batch_data(
                str(YEARLY_FILE),
                str(MONTHLY_FILE),
                str(DAILY_FILE),
                YEARLY_FILE.stat().st_mtime_ns,
                MONTHLY_FILE.stat().st_mtime_ns,
                DAILY_FILE.stat().st_mtime_ns
            )
        )

    except (
        OSError,
        ValueError,
        KeyError,
        pd.errors.EmptyDataError
    ) as error:

        st.error(
            f"Unable to load Spark batch data: {error}"
        )

        return

    if (
        yearly_df.empty
        or monthly_df.empty
        or daily_df.empty
    ):

        st.info("Historical analytics files are empty.")
        return

    # ----------------------------------------------
    # SELECT CITY, YEAR AND MONTH
    # ----------------------------------------------

    city_col, year_col, month_col = st.columns(3)

    available_cities = sorted(
        yearly_df["City"].dropna().unique().tolist()
    )

    if not available_cities:
        st.info("No historical cities available.")
        return

    with city_col:

        historical_city = st.selectbox(
            "🏙️ Choose historical city",
            available_cities,
            key="historical_city"
        )

    city_yearly = yearly_df[
        yearly_df["City"] == historical_city
    ].copy()

    city_monthly = monthly_df[
        monthly_df["City"] == historical_city
    ].copy()

    city_daily = daily_df[
        daily_df["City"] == historical_city
    ].copy()

    available_years = sorted(
        city_yearly["Year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if not available_years:
        st.info("No historical years available.")
        return

    with year_col:

        selected_year = st.selectbox(
            "📅 Select historical year",
            available_years,
            index=len(available_years) - 1,
            key="historical_year"
        )

    year_monthly = city_monthly[
        city_monthly["Year"] == selected_year
    ].copy()

    year_daily = city_daily[
        city_daily["Year"] == selected_year
    ].copy()

    available_months = sorted(
        year_monthly["Month"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    with month_col:

        selected_month = st.selectbox(
            "🗓️ Select month",
            [0] + available_months,
            format_func=lambda m: (
                "Entire Year"
                if m == 0
                else calendar.month_name[m]
            ),
            key="historical_month"
        )

    # ----------------------------------------------
    # SELECT HISTORICAL PERIOD
    # ----------------------------------------------

    if selected_month == 0:

        summary_df = city_yearly[
            city_yearly["Year"] == selected_year
        ]

        filtered_daily = year_daily.copy()

        period_label = str(selected_year)

    else:

        summary_df = year_monthly[
            year_monthly["Month"] == selected_month
        ]

        filtered_daily = year_daily[
            year_daily["Month"] == selected_month
        ].copy()

        period_label = (
            f"{calendar.month_name[selected_month]} "
            f"{selected_year}"
        )

    if summary_df.empty:

        st.info("No Spark analytics for this period.")
        return

    summary = summary_df.iloc[0]

    avg_aqi = summary["Avg_AQI"]

    if pd.isna(avg_aqi):

        st.info(
            "No valid AQI measurements for this period."
        )

        return

    # ----------------------------------------------
    # HISTORICAL OVERVIEW
    # ----------------------------------------------

    st.markdown(
        f"### 🌸 {historical_city} — {period_label}"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "🌍 Historical Average AQI",
        f"{avg_aqi:.2f}"
    )

    total_records = summary["Total_Records"]

    col2.metric(
        "📊 AQI Measurements",
        (
            int(total_records)
            if pd.notna(total_records)
            else 0
        )
    )

    # ----------------------------------------------
    # SIX POLLUTANTS
    # ----------------------------------------------

    show_pollutant_metrics(summary)

    # Fixed category card
    show_aqi_category(
        avg_aqi,
        historical=True
    )

    # ----------------------------------------------
    # HISTORICAL AQI TREND
    # ----------------------------------------------

    st.markdown("### 📈 Historical Pollution Trend")

    daily_trend = filtered_daily.dropna(
        subset=["Date", "Avg_AQI"]
    ).sort_values("Date")

    if not daily_trend.empty:

        fig_trend = px.line(
            daily_trend,
            x="Date",
            y="Avg_AQI",
            markers=(len(daily_trend) <= 45),
            title=(
                f"Daily Average AQI — "
                f"{historical_city}, {period_label}"
            ),
            labels={
                "Date": "Historical Date",
                "Avg_AQI": "Average AQI"
            }
        )

        fig_trend.update_traces(
            line_color="#9B8AD0",
            line_width=3
        )

        st.plotly_chart(
            style_plot(fig_trend),
            use_container_width=True
        )

    else:

        st.info("No daily AQI trend available.")

    # ----------------------------------------------
    # HISTORICAL POLLUTANT TREND
    # ----------------------------------------------

    st.markdown("### 🧪 Historical Pollutant Trends")

    selected_pollutant = st.selectbox(
        "Select pollutant to analyze",
        list(POLLUTANTS.keys()),
        key="historical_pollutant"
    )

    config = POLLUTANTS[selected_pollutant]

    pollutant_column = config["column"]

    pollutant_trend = filtered_daily.dropna(
        subset=["Date", pollutant_column]
    ).sort_values("Date")

    if not pollutant_trend.empty:

        fig_pollutant = px.line(
            pollutant_trend,
            x="Date",
            y=pollutant_column,
            markers=(len(pollutant_trend) <= 45),
            title=(
                f"Daily {selected_pollutant} Trend — "
                f"{historical_city}, {period_label}"
            ),
            labels={
                "Date": "Historical Date",
                pollutant_column: (
                    f"Average concentration "
                    f"({config['unit']})"
                )
            }
        )

        fig_pollutant.update_traces(
            line_color=config["color"],
            line_width=3
        )

        st.plotly_chart(
            style_plot(fig_pollutant),
            use_container_width=True
        )

    else:

        st.info(
            f"No valid {selected_pollutant} "
            "measurements for this period."
        )

    # ----------------------------------------------
    # MONTHLY AQI PATTERN
    # ----------------------------------------------

    st.markdown("### 🌼 Monthly Pollution Pattern")

    monthly_trend = year_monthly.dropna(
        subset=["Month", "Avg_AQI"]
    ).copy()

    monthly_trend = monthly_trend.sort_values("Month")

    if not monthly_trend.empty:

        monthly_trend["Month Name"] = (
            monthly_trend["Month"]
            .astype(int)
            .apply(lambda m: calendar.month_name[m])
        )

        fig_monthly = px.bar(
            monthly_trend,
            x="Month Name",
            y="Avg_AQI",
            color="Avg_AQI",
            color_continuous_scale=[
                "#9EDBC5",
                "#D8C5F2",
                "#F0B4B8"
            ],
            title=(
                f"Monthly Average AQI — "
                f"{historical_city}, {selected_year}"
            ),
            labels={
                "Month Name": "Month",
                "Avg_AQI": "Average AQI"
            }
        )

        fig_monthly.update_layout(
            coloraxis_showscale=False
        )

        st.plotly_chart(
            style_plot(fig_monthly),
            use_container_width=True
        )

    else:

        st.info("No monthly AQI trend available.")

    # ----------------------------------------------
    # YEAR-TO-YEAR COMPARISON
    # ----------------------------------------------

    st.markdown("### 🔍 Compare Historical Years")

    comparison_years = sorted(
        city_yearly["Year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if len(comparison_years) >= 2:

        first_col, second_col = st.columns(2)

        with first_col:

            year1 = st.selectbox(
                "First year",
                comparison_years,
                index=0,
                key="compare_year_1"
            )

        with second_col:

            year2 = st.selectbox(
                "Second year",
                comparison_years,
                index=len(comparison_years) - 1,
                key="compare_year_2"
            )

        comparison_summary = city_yearly[
            city_yearly["Year"].isin([year1, year2])
        ].dropna(subset=["Avg_AQI"]).copy()

        comparison_summary["Year Label"] = (
            comparison_summary["Year"]
            .astype(int)
            .astype(str)
        )

        if not comparison_summary.empty:

            fig_comparison = px.bar(
                comparison_summary,
                x="Year Label",
                y="Avg_AQI",
                color="Year Label",
                color_discrete_sequence=[
                    "#89CDB8",
                    "#B8A5E8"
                ],
                title=(
                    f"Historical AQI Comparison — "
                    f"{historical_city}"
                ),
                labels={
                    "Year Label": "Year",
                    "Avg_AQI": "Average AQI"
                }
            )

            fig_comparison.update_layout(
                showlegend=False
            )

            st.plotly_chart(
                style_plot(fig_comparison),
                use_container_width=True
            )

        if year1 != year2:

            averages = comparison_summary.set_index(
                "Year"
            )["Avg_AQI"]

            if (
                year1 in averages.index
                and year2 in averages.index
            ):

                difference = (
                    averages[year2] - averages[year1]
                )

                if difference > 0:

                    st.warning(
                        f"📈 Average AQI increased by "
                        f"{difference:.2f} points "
                        f"from {year1} to {year2}."
                    )

                elif difference < 0:

                    st.success(
                        f"📉 Average AQI decreased by "
                        f"{abs(difference):.2f} points "
                        f"from {year1} to {year2}."
                    )

                else:

                    st.info(
                        "Average AQI was equal "
                        "in both selected years."
                    )

        else:

            st.info(
                "No valid AQI data for the selected years."
            )

        st.caption(
            "Yearly averages use available historical "
            "measurements. Different years may have "
            "different data coverage."
        )

    else:

        st.info(
            "At least two years of data are required "
            "for year-to-year comparison."
        )

    # ----------------------------------------------
    # SPARK PROCESSED HISTORICAL TABLE
    # ----------------------------------------------

    st.markdown("### 📂 Spark Processed Historical Data")

    display_columns = [
        "Date",
        "Avg_AQI",
        "Avg_PM25",
        "Avg_PM10",
        "Avg_NO2",
        "Avg_SO2",
        "Avg_CO",
        "Avg_O3",
        "Total_Records"
    ]

    display_df = filtered_daily[
        display_columns
    ].copy()

    st.dataframe(
        display_df.sort_values("Date"),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "📚 Historical averages are calculated using "
        "Apache Spark Batch Processing. Pandas is used "
        "to load, filter and visualize aggregated CSVs. "
        "These are historical statistics, not current "
        "air quality conditions."
    )


# ==================================================
# 15. LIVE STREAMING DASHBOARD
# ==================================================

@st.fragment(run_every="5s")
def show_dashboard():

    if not DATA_FILE.exists():

        st.warning("Waiting for Spark analytics...")
        return

    try:

        df = pd.read_csv(DATA_FILE)

    except (
        pd.errors.EmptyDataError,
        OSError
    ):

        st.warning("Waiting for updated data...")
        return

    required_columns = [
        "City",
        "Avg_AQI",
        "Avg_PM25",
        "Avg_PM10",
        "Total_Records"
    ]

    if df.empty or not all(
        column in df.columns
        for column in required_columns
    ):

        st.info(
            "Waiting for complete Spark analytics..."
        )

        return

    df = prepare_numeric_data(df)

    df = df.dropna(
        subset=["City", "Avg_AQI"]
    )

    if df.empty:

        st.info("Waiting for valid AQI readings...")
        return

    cities = sorted(
        df["City"].unique().tolist()
    )

    # ----------------------------------------------
    # LOAD STREAMING HISTORY
    # ----------------------------------------------

    history_df = None

    if HISTORY_FILE.exists():

        try:

            history_df = pd.read_csv(
                HISTORY_FILE
            )

            required_history = [
                "Timestamp",
                "City",
                "Avg_AQI"
            ]

            if not all(
                column in history_df.columns
                for column in required_history
            ):

                history_df = None

        except (
            pd.errors.EmptyDataError,
            OSError,
            ValueError
        ):

            history_df = None

    # ----------------------------------------------
    # STREAMING STATUS
    # ----------------------------------------------

    st.markdown("### 📡 Live Streaming Status")

    stream_status, last_update, status_type = (
        get_streaming_status(history_df)
    )

    status_col, update_col = st.columns(2)

    with status_col:

        if status_type == "live":

            st.success(
                "🟢 **LIVE — Fresh Analytics Arriving**"
            )

        elif status_type == "delayed":

            st.warning(
                "🟡 **DELAYED — Waiting for New Data**"
            )

        elif stream_status == "WAITING FOR DATA":

            st.info("⚪ **WAITING FOR DATA**")

        else:

            st.error(
                "🔴 **OFFLINE / STALE — No Recent Updates**"
            )

    with update_col:

        st.metric(
            "🕒 Last Analytics Update",
            last_update
        )

    st.caption(
        "Status is estimated from the latest Spark "
        "history timestamp, not direct Kafka or Spark "
        "service health."
    )

    # ----------------------------------------------
    # SELECT CITY
    # ----------------------------------------------

    selected_city = st.selectbox(
        "📍 Choose a city",
        cities,
        key="selected_city"
    )

    city_data = df[
        df["City"] == selected_city
    ].iloc[0]

    aqi = float(
        city_data["Avg_AQI"]
    )

    status, color, background = get_aqi_status(aqi)

    # ----------------------------------------------
    # AIR QUALITY OVERVIEW
    # ----------------------------------------------

    st.markdown(
        f"### ✨ Air Quality Overview — {selected_city}"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "🌍 Average AQI",
        f"{aqi:.2f}"
    )

    total_records = city_data["Total_Records"]

    col2.metric(
        "📊 Records Processed",
        (
            int(total_records)
            if pd.notna(total_records)
            else 0
        )
    )

    # ----------------------------------------------
    # ALL SIX POLLUTANTS
    # ----------------------------------------------

    show_pollutant_metrics(city_data)

    # ----------------------------------------------
    # FIXED AQI CATEGORY CARD
    # ----------------------------------------------

    show_aqi_category(aqi)

    # ----------------------------------------------
    # POLLUTION ALERTS
    # ----------------------------------------------

    st.markdown("### 🚨 Pollution Alerts")

    show_alert(aqi)

    st.caption(
        "Alerts are based on replayed historical data, "
        "not current real-world conditions."
    )

    # ----------------------------------------------
    # HEALTH RECOMMENDATIONS
    # ----------------------------------------------

    st.markdown("### 💚 Health Recommendations")

    with st.container(border=True):

        st.markdown(
            f"**Suggested precautions for {status} AQI**"
        )

        for recommendation in get_health_recommendations(aqi):

            st.markdown(
                f"✓ {recommendation}"
            )

        st.caption(
            "General educational recommendations based "
            "on simulated historical readings."
        )

    # ----------------------------------------------
    # CITY POLLUTION RANKING
    # ----------------------------------------------

    st.markdown("### 🏆 City Pollution Ranking")

    ranking_df = df[
        ["City", "Avg_AQI", "Total_Records"]
    ].copy()

    ranking_df = ranking_df.sort_values(
        "Avg_AQI",
        ascending=False
    ).reset_index(drop=True)

    ranking_df["Rank"] = ranking_df.index + 1

    ranking_df["AQI Category"] = (
        ranking_df["Avg_AQI"]
        .apply(lambda x: get_aqi_status(x)[0])
    )

    ranking_df = ranking_df[
        [
            "Rank",
            "City",
            "Avg_AQI",
            "AQI Category",
            "Total_Records"
        ]
    ]

    ranking_df = ranking_df.rename(
        columns={
            "Avg_AQI": "Average AQI",
            "Total_Records": "Records Processed"
        }
    )

    st.dataframe(
        ranking_df,
        use_container_width=True,
        hide_index=True
    )

    if len(ranking_df) >= 2:

        most_polluted = ranking_df.iloc[0]
        least_polluted = ranking_df.iloc[-1]

        most_col, least_col = st.columns(2)

        with most_col:

            st.warning(
                f"🔴 **Most Polluted:** "
                f"{most_polluted['City']} "
                f"(AQI: {most_polluted['Average AQI']:.2f})"
            )

        with least_col:

            st.success(
                f"🟢 **Least Polluted:** "
                f"{least_polluted['City']} "
                f"(AQI: {least_polluted['Average AQI']:.2f})"
            )

    st.caption(
        "Ranking uses cumulative average AQI "
        "from the simulated stream."
    )

    # ----------------------------------------------
    # AIR QUALITY INSIGHTS
    # ----------------------------------------------

    st.markdown("### 📊 Air Quality Insights")

    left, right = st.columns(2)

    # ----------------------------------------------
    # POLLUTANT COMPARISON
    # ----------------------------------------------

    with left:

        selected_pollutant = st.selectbox(
            "Select pollutant for city comparison",
            list(POLLUTANTS.keys()),
            key="live_pollutant"
        )

        config = POLLUTANTS[selected_pollutant]

        pollutant_column = config["column"]

        pollutant_df = df[
            ["City", pollutant_column]
        ].dropna().copy()

        if not pollutant_df.empty:

            fig1 = px.bar(
                pollutant_df.sort_values(
                    pollutant_column
                ),
                x="City",
                y=pollutant_column,
                color="City",
                title=(
                    f"City-wise {selected_pollutant} Comparison"
                ),
                labels={
                    pollutant_column: (
                        f"Average concentration "
                        f"({config['unit']})"
                    )
                },
                color_discrete_sequence=[
                    "#B8A5E8",
                    "#89CDB8",
                    "#F2BD8E",
                    "#E6A6C7",
                    "#A8C4E8"
                ]
            )

            fig1.update_layout(
                showlegend=False
            )

            st.plotly_chart(
                style_plot(fig1),
                use_container_width=True
            )

        else:

            st.info(
                f"No valid {selected_pollutant} "
                "measurements available."
            )

    # ----------------------------------------------
    # CITY-WISE AQI COMPARISON
    # ----------------------------------------------

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
            title="City-wise AQI Comparison",
            labels={
                "Avg_AQI": "Average AQI"
            }
        )

        fig2.update_layout(
            coloraxis_showscale=False
        )

        st.plotly_chart(
            style_plot(fig2),
            use_container_width=True
        )

    # ----------------------------------------------
    # SELECTED CITY POLLUTANT SUMMARY
    # ----------------------------------------------

    st.markdown("### 🌿 Selected City Pollutant Summary")

    pollutant_rows = []

    for name, config in POLLUTANTS.items():

        value = city_data[config["column"]]

        pollutant_rows.append({
            "Pollutant": name,
            "Average Concentration": (
                round(float(value), 2)
                if pd.notna(value)
                else None
            ),
            "Unit": config["unit"]
        })

    pollutant_summary = pd.DataFrame(
        pollutant_rows
    )

    st.dataframe(
        pollutant_summary,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # LIVE AQI TRENDS
    # ----------------------------------------------

    st.markdown("### 📈 Live AQI Trends")

    if history_df is not None and not history_df.empty:

        try:

            history_df["Timestamp"] = pd.to_datetime(
                history_df["Timestamp"],
                utc=True,
                errors="coerce"
            )

            history_df["Avg_AQI"] = pd.to_numeric(
                history_df["Avg_AQI"],
                errors="coerce"
            )

            history_df = history_df.dropna(
                subset=["Timestamp", "Avg_AQI"]
            )

            if not history_df.empty:

                latest_time = (
                    history_df["Timestamp"].max()
                )

                recent_history = history_df[
                    history_df["Timestamp"]
                    >= latest_time - pd.Timedelta(
                        minutes=30
                    )
                ]

                city_history = recent_history[
                    recent_history["City"] == selected_city
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
                            "Timestamp": (
                                "Streaming Time (UTC)"
                            ),
                            "Avg_AQI": "Average AQI"
                        }
                    )

                    fig3.update_traces(
                        line_color="#9B8AD0",
                        line_width=3
                    )

                    st.plotly_chart(
                        style_plot(fig3),
                        use_container_width=True
                    )

                    st.caption(
                        "The X-axis shows streaming/processing "
                        "time (UTC), not original measurement dates."
                    )

                else:

                    st.info(
                        "Waiting for AQI history for this city."
                    )

            else:

                st.info(
                    "Waiting for valid AQI history..."
                )

        except (
            ValueError,
            KeyError,
            TypeError
        ):

            st.info(
                "Waiting for valid AQI history..."
            )

    else:

        st.info(
            "AQI history is not available yet."
        )

    # ----------------------------------------------
    # PROCESSED DATA TABLE
    # ----------------------------------------------

    st.markdown("### 🌷 City Air Quality Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "🔄 Streaming dashboard refreshes every 5 seconds."
    )


# ==================================================
# 16. DASHBOARD NAVIGATION
# ==================================================

dashboard_tab, time_machine_tab = st.tabs(
    [
        "📡 Live Dashboard",
        "⏳ Air Quality Time Machine"
    ]
)

with dashboard_tab:
    show_dashboard()

with time_machine_tab:
    show_time_machine()
