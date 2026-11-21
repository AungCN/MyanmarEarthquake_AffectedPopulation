import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from geopy.distance import geodesic
from datetime import datetime
from streamlit_folium import folium_static
import requests
import time
import io


# 🔹 **Fetch Earthquake Data from USGS API**
def fetch_earthquake_data(start_date, end_date, min_magnitude=4.0):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    params = {
        "format": "csv",
        "starttime": start_date.strftime("%Y-%m-%d"),
        "endtime": end_date.strftime("%Y-%m-%d"),
        "minmagnitude": min_magnitude,
        "maxmagnitude": 10.0,
        "orderby": "time",
    }

    st.info(f"Fetching earthquake data from {start_date} to {end_date}...")

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            st.error(f"❌ Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return None


# 🔹 **Load Population Data (Local CSV)**
@st.cache_data
def load_population_data():
    df_pop_mm = pd.read_csv("MyanmarPop_2014_Township.csv")
    df_pop_mm = df_pop_mm.loc[:, ~df_pop_mm.columns.str.startswith('Unnamed')]
    return df_pop_mm


df_pop_mm = load_population_data()


# 🔹 **Estimate Affected Population**
def estimate_affected_population(eq_lat, eq_lon, eq_mag):
    affected_pop = 0
    for _, row in df_pop_mm.iterrows():
        region_lat = row["lat"]
        region_lon = row["lon"]
        total_pop = row["hh_total"]

        if pd.isna(region_lat) or pd.isna(region_lon) or pd.isna(total_pop):
            continue

        distance_km = geodesic((eq_lat, eq_lon), (region_lat, region_lon)).km
        max_radius = eq_mag * 10

        if distance_km <= max_radius:
            weight = np.exp(-distance_km / (max_radius / 2))
            magnitude_factor = (eq_mag / 7.0) ** 2
            affected_pop += total_pop * weight * magnitude_factor

    return int(affected_pop)


# 🔹 **Plot Earthquake Map**
# 🔹 **Plot Earthquake Map with Shaded Affected Areas**
def plot_earthquake_map(df_eq):
    if df_eq is None or df_eq.empty:
        st.warning("⚠️ No earthquakes found in the selected time range.")
        return None, None

    df_eq["Estimated_Affected_Pop"] = df_eq.apply(
        lambda row: estimate_affected_population(row["latitude"], row["longitude"], row["mag"]), axis=1
    )

    myanmar_map = folium.Map(location=[21.0, 96.0], zoom_start=6)

    # Add Population Heatmap
    heat_data = [[row["lat"], row["lon"], row["hh_total"]] for _, row in df_pop_mm.iterrows()]
    if heat_data:
        HeatMap(heat_data, min_opacity=0.4, radius=20, blur=10, max_zoom=1).add_to(myanmar_map)

    # Define color scale for affected population intensity
    def get_color(affected_population):
        if affected_population > 500000:
            return "#800026"  # Dark Red
        elif affected_population > 100000:
            return "#BD0026"  # Red
        elif affected_population > 50000:
            return "#E31A1C"  # Light Red
        elif affected_population > 10000:
            return "#FC4E2A"  # Orange
        elif affected_population > 1000:
            return "#FD8D3C"  # Yellow-Orange
        else:
            return "#FEB24C"  # Light Yellow

    # Add Earthquake Circles with Shading
    for _, row in df_eq.iterrows():
        weighted_population = row["Estimated_Affected_Pop"]
        max_radius = row["mag"] * 10  # Dynamic radius based on magnitude

        folium.Circle(
            location=[row["latitude"], row["longitude"]],
            radius=max_radius * 1000,  # Convert km to meters
            color=get_color(weighted_population),
            fill=True,
            fill_color=get_color(weighted_population),
            fill_opacity=0.5,
            popup=(
                f"<b>Date:</b> {row['time']}<br>"
                f"<b>Magnitude:</b> {row['mag']}<br>"
                f"<b>Estimated Affected Population:</b> {int(weighted_population):,}"
            ),
        ).add_to(myanmar_map)

    folium_static(myanmar_map)
    return df_eq, myanmar_map

# 🔹 **Streamlit UI**
st.title("🌍 Myanmar Earthquake Impact Analysis (USGS API)")
st.sidebar.header("📌 Filter Earthquake Data")

# **Set default date range to today**
today_date = datetime.today().date()
start_date = st.sidebar.date_input("📅 Start Date", today_date)
end_date = st.sidebar.date_input("📅 End Date", today_date)

# Validate date selection
if start_date > end_date:
    st.error("❌ Start date cannot be after end date!")
else:
    df_eq = fetch_earthquake_data(start_date, end_date)

    if df_eq is not None and not df_eq.empty:
        # Convert 'time' column to datetime
        df_eq["time"] = pd.to_datetime(df_eq["time"], errors="coerce")
        df_eq["latitude"] = pd.to_numeric(df_eq["latitude"], errors="coerce")
        df_eq["longitude"] = pd.to_numeric(df_eq["longitude"], errors="coerce")
        df_eq["mag"] = pd.to_numeric(df_eq["mag"], errors="coerce")

        # Generate map based on fetched data
        filtered_data, _ = plot_earthquake_map(df_eq)

        # CSV Export Button
        if filtered_data is not None and not filtered_data.empty:
            csv = filtered_data.to_csv(index=False).encode("utf-8")
            filename = f"earthquake_data_{start_date}_to_{end_date}.csv"

            st.download_button(
                label="📥 Download Earthquake Data as CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
            )
