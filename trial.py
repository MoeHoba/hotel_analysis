#import libraries
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
df = pd.read_csv("hotels.csv")

st.image("download.jpg", caption="🏞️ Hotel Booking Experience")
# Step 1: Load the dataset
df = pd.read_csv('hotels.csv')

# Step 2: Drop personal identifiable information (PII)
pii_columns = ['name', 'email', 'phone-number', 'credit_card']
df.drop(columns=[col for col in pii_columns if col in df.columns], inplace=True)

# Step 3: Handle missing values
# Option 1: Drop rows with too many missing values (e.g., all guests are NaN)
df.dropna(subset=['adults', 'children', 'babies'], how='all', inplace=True)

# Fill missing numerical values with 0
numerical_cols = ['children', 'agent', 'company']
for col in numerical_cols:
    if col in df.columns:
        df[col].fillna(0, inplace=True)

# Fill other missing values with a placeholder
df.fillna('Unknown', inplace=True)

# Step 4: Convert date-related columns to correct types
df['reservation_status_date'] = pd.to_datetime(df['reservation_status_date'], errors='coerce')

# Step 5: Remove duplicates if any
df.drop_duplicates(inplace=True)

# Step 6: Save cleaned file
df.to_csv('cleaned_hotels.csv', index=False)

print("Data cleaned and saved to 'cleaned_hotels.csv'")


# Load cleaned data
df = pd.read_csv("cleaned_hotels.csv")

st.set_page_config(page_title="Hotel Booking Dashboard", layout="wide")

st.title("🏨 Hotel Booking Dashboard")

# Sidebar Filters
st.sidebar.header("🔎 Filters")
hotel_type = st.sidebar.selectbox("Select Hotel Type", df['hotel'].unique())
year = st.sidebar.selectbox("Select Arrival Year", sorted(df['arrival_date_year'].unique()))
cancel_status = st.sidebar.selectbox("Select Cancellation Status", ['All', 'Canceled', 'Not Canceled'])

# Apply Filters
filtered_df = df[(df['hotel'] == hotel_type) & (df['arrival_date_year'] == year)]

if cancel_status == 'Canceled':
    filtered_df = filtered_df[filtered_df['is_canceled'] == 1]
elif cancel_status == 'Not Canceled':
    filtered_df = filtered_df[filtered_df['is_canceled'] == 0]

# KPIs
total_bookings = len(filtered_df)
cancellation_rate = round(filtered_df['is_canceled'].mean() * 100, 2) if not filtered_df.empty else 0
avg_adr = round(filtered_df['adr'].mean(), 2) if not filtered_df.empty else 0
avg_lead_time = round(filtered_df['lead_time'].mean(), 2) if not filtered_df.empty else 0

# KPI Columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("📦 Total Bookings", total_bookings)
kpi2.metric("❌ Cancellation Rate", f"{cancellation_rate}%")
kpi3.metric("💰 Avg ADR", f"${avg_adr}")
kpi4.metric("⏱️ Avg Lead Time", f"{avg_lead_time} days")

st.markdown("---")

# Chart 1: Cancellation Rate by Hotel Type
fig1 = px.histogram(
    df[df['arrival_date_year'] == year],
    x='hotel', color='is_canceled',
    barmode='group',
    labels={'is_canceled': 'Canceled'},
    title='Cancellation Count by Hotel Type'
)
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Lead Time Distribution (Canceled vs Not)
fig2 = px.histogram(
    filtered_df, x='lead_time', color='is_canceled',
    nbins=30,
    title='Lead Time Distribution (Canceled vs Not)',
    labels={'is_canceled': 'Canceled'}
)
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: ADR vs Cancellation
fig3 = px.box(
    filtered_df, x='is_canceled', y='adr',
    title='ADR vs Cancellation',
    labels={'is_canceled': 'Canceled (1) / Not (0)', 'adr': 'Average Daily Rate'}
)
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Top Countries by Bookings
top_countries = filtered_df['country'].value_counts().nlargest(10).reset_index()
top_countries.columns = ['country', 'count']
fig4 = px.bar(
    top_countries, x='country', y='count',
    title='Top 10 Countries by Bookings',
    labels={'count': 'Bookings'}
)
st.plotly_chart(fig4, use_container_width=True)
