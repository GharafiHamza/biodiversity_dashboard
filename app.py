import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import math
import streamlit as st
import plotly.graph_objs as go
from collections import deque
import time

# Define zones along the UAE coastline
zones = [
    "Zone 1 - Abu Dhabi",
    "Zone 2 - Dubai",
    "Zone 3 - Sharjah",
    "Zone 4 - Ajman",
    "Zone 5 - Umm Al Quwain",
    "Zone 6 - Ras Al Khaimah",
    "Zone 7 - Fujairah"
]

# Define fish species
species_names = [
    "Atlantic Salmon", "Pacific Salmon", "Rainbow Trout", 
    "Brook Trout", "Brown Trout", "Northern Pike", 
    "Largemouth Bass", "Smallmouth Bass", "Walleye", "Bluegill"
]

# Define environmental variables
environmental_vars = [
    "Temperature", "Salinity", "pH", "O2 Dissolved", 
    "Turbidity", "Chlorophyll-a", "CDOM", "Phycoreythrin", "Uranine"
]

# Define species colors
species_colors = [
    "#FF6347", "#FF4500", "#FFD700", 
    "#ADFF2F", "#7FFF00", "#00FA9A", 
    "#1E90FF", "#4682B4", "#6A5ACD", "#8A2BE2"
]

# Generate initial data for the last year
start_date = datetime.now() - timedelta(days=365)
date_range = pd.date_range(start_date, periods=365)

# Function to generate random environmental variable data
def generate_environmental_data():
    return {
        "Temperature": round(random.uniform(15, 35), 2),
        "Salinity": round(random.uniform(30, 40), 2),
        "pH": round(random.uniform(7.5, 8.5), 2),
        "O2 Dissolved": round(random.uniform(5, 10), 2),
        "Turbidity": round(random.uniform(1, 10), 2),
        "Chlorophyll-a": round(random.uniform(0.1, 10), 2),
        "CDOM": round(random.uniform(0.1, 5), 2),
        "Phycoreythrin": round(random.uniform(0.1, 5), 2),
        "Uranine": round(random.uniform(0.1, 5), 2)
    }

# Initialize data storage
data = []

# Generate data for each day, each zone
for date in date_range:
    for zone in zones:
        species_counts = [random.randint(0, 100) for _ in species_names]
        env_data = generate_environmental_data()
        row = {
            "Date": date,
            "Zone": zone,
            "SpeciesCounts": species_counts,
            **env_data
        }
        data.append(row)

# Convert to DataFrame
df = pd.DataFrame(data)

# Initialize recent data deque to hold recent data for updating visualizations
recent_data = deque(maxlen=365 * len(zones))
recent_data.extend(data)

# Define function to calculate biodiversity indices
def calculate_indices(species_counts):
    S = len(species_counts)
    total_individuals = sum(species_counts)
    proportions = [count / total_individuals for count in species_counts]
    simpson = 1 - sum(p ** 2 for p in proportions)
    shannon = -sum(p * math.log(p) for p in proportions if p > 0)
    pielou = shannon / math.log(S)
    return simpson, shannon, pielou

# Initialize Streamlit app
st.title("Dynamic Biodiversity and Environmental Data Visualization")

selected_zone = st.selectbox("Select Zone", zones)

# Function to update data
def update_data():
    global recent_data
    new_date = datetime.now()
    new_data = []
    for zone in zones:
        species_counts = [random.randint(0, 100) for _ in species_names]
        env_data = generate_environmental_data()
        row = {
            "Date": new_date,
            "Zone": zone,
            "SpeciesCounts": species_counts,
            **env_data
        }
        new_data.append(row)
    recent_data.extend(new_data)

# Update data every 3 seconds
update_interval = 3

# Placeholder for dynamic content
placeholder = st.empty()

while True:
    update_data()

    # Filter data for the selected zone
    zone_data = [d for d in recent_data if d['Zone'] == selected_zone]
    zone_df = pd.DataFrame(zone_data)

    # Plot species counts as a donut chart
    latest_data = zone_df.iloc[-1]
    species_counts = latest_data['SpeciesCounts']
    fig_donut = go.Figure(data=[go.Pie(
        labels=species_names,
        values=species_counts,
        hole=.4,
        marker=dict(colors=species_colors)
    )])
    fig_donut.update_layout(title_text="Species Counts Donut Chart")

    # Calculate biodiversity indices
    indices_data = []
    for i, row in zone_df.iterrows():
        simpson, shannon, pielou = calculate_indices(row['SpeciesCounts'])
        indices_data.append({
            "Date": row['Date'],
            "Simpson": simpson,
            "Shannon": shannon,
            "Pielou": pielou
        })
    indices_df = pd.DataFrame(indices_data)

    # Plot biodiversity indices over time
    fig_biodiversity = go.Figure()
    fig_biodiversity.add_trace(go.Scatter(x=indices_df['Date'], y=indices_df['Simpson'], mode='lines', name='Simpson Index'))
    fig_biodiversity.add_trace(go.Scatter(x=indices_df['Date'], y=indices_df['Shannon'], mode='lines', name='Shannon Index'))
    fig_biodiversity.add_trace(go.Scatter(x=indices_df['Date'], y=indices_df['Pielou'], mode='lines', name='Pielou Index'))
    fig_biodiversity.update_layout(title_text="Biodiversity Indices Over Time")

    # Plot environmental variables over time
    fig_env_vars = go.Figure()
    for var in environmental_vars:
        fig_env_vars.add_trace(go.Scatter(x=zone_df['Date'], y=zone_df[var], mode='lines', name=var))
    fig_env_vars.update_layout(title_text="Environmental Variables Over Time")

    # Render the updated plots
    with placeholder.container():
        st.plotly_chart(fig_donut)
        st.plotly_chart(fig_biodiversity)
        st.plotly_chart(fig_env_vars)

    # Wait for the next update interval
    time.sleep(update_interval)
