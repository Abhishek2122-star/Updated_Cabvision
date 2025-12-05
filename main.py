import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ======================================================
# APP TITLE
# ======================================================
st.set_page_config(page_title="NYC Taxi Data Analysis", layout="wide")
st.title("🚕 CABVISION : A WEB APP FOR EXPLORING TAXI TRENDS")
st.markdown("Explore NYC Taxi trips with advanced analytics, maps, charts, and filters.")

# ======================================================
# FILE UPLOADER
# ======================================================
st.sidebar.header("📂 Upload NYC Taxi Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Convert date columns
    date_cols = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Additional time features
    if "tpep_pickup_datetime" in df.columns:
        df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
        df["pickup_day"] = df["tpep_pickup_datetime"].dt.day_name()
        df["pickup_month"] = df["tpep_pickup_datetime"].dt.month_name()

    # ======================================================
    # SIDEBAR FILTERS
    # ======================================================
    st.sidebar.header("🔍 Filters")

    # Passenger Count Filter
    if "passenger_count" in df.columns:
        passenger_filter = st.sidebar.multiselect(
            "Passenger Count",
            sorted(df["passenger_count"].dropna().unique()),
            default=sorted(df["passenger_count"].dropna().unique())
        )
        df = df[df["passenger_count"].isin(passenger_filter)]

    # Trip Distance Filter
    if "trip_distance" in df.columns:
        min_dist, max_dist = float(df["trip_distance"].min()), float(df["trip_distance"].max())
        trip_dist = st.sidebar.slider("Trip Distance Range", min_dist, max_dist, (min_dist, max_dist))
        df = df[(df["trip_distance"] >= trip_dist[0]) & (df["trip_distance"] <= trip_dist[1])]

    # Vendor Filter
    if "VendorID" in df.columns:
        vendor_filter = st.sidebar.multiselect(
            "Vendor ID",
            sorted(df["VendorID"].unique()),
            default=sorted(df["VendorID"].unique())
        )
        df = df[df["VendorID"].isin(vendor_filter)]

    st.success("Dataset Loaded Successfully!")

    # ======================================================
    # DATA PREVIEW
    # ======================================================
    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(10))

    # ======================================================
    # METRICS CARDS
    # ======================================================
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Trips", len(df))
    col2.metric("Total Revenue ($)", round(df["fare_amount"].sum(), 2) if "fare_amount" in df else 0)
    col3.metric("Average Trip Distance (mi)", round(df["trip_distance"].mean(), 2))

    # Safe speed calculation
    try:
        avg_speed = (df["trip_distance"] /
        ((df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 3600)).mean()
        col4.metric("Average Speed (mph)", round(avg_speed, 2))
    except:
        col4.metric("Average Speed (mph)", "N/A")

    # ======================================================
    # VISUALIZATIONS
    # ======================================================
    st.subheader("📈 Trip Distance & Fare Analysis")
    colA, colB = st.columns(2)

    # Trip Distance
    with colA:
        if "trip_distance" in df.columns:
            fig = px.histogram(df, x="trip_distance", nbins=50, title="Trip Distance Distribution")
            st.plotly_chart(fig, use_container_width=True)

    # Fare Amount
    with colB:
        if "fare_amount" in df.columns:
            fig2 = px.histogram(df, x="fare_amount", nbins=50, title="Fare Amount Distribution")
            st.plotly_chart(fig2, use_container_width=True)

    # Time-series (hour, day, month)
    if "pickup_hour" in df:
        st.subheader("⏱ Trips by Hour of Day")
        hourly_fig = px.bar(df["pickup_hour"].value_counts().sort_index(), title="Trips per Hour")
        st.plotly_chart(hourly_fig, use_container_width=True)

    if "pickup_day" in df:
        st.subheader("📅 Trips by Day of Week")
        day_fig = px.bar(df["pickup_day"].value_counts(), title="Trips per Day")
        st.plotly_chart(day_fig, use_container_width=True)

    if "pickup_month" in df:
        st.subheader("📆 Trips by Month")
        month_fig = px.bar(df["pickup_month"].value_counts(), title="Trips per Month")
        st.plotly_chart(month_fig, use_container_width=True)

    # Map visualization
    if "pickup_latitude" in df.columns and "pickup_longitude" in df.columns:
        st.subheader("🗺 Pickup Locations Map")
        st.map(df[["pickup_latitude", "pickup_longitude"]].dropna().head(20000))

    if "dropoff_latitude" in df.columns and "dropoff_longitude" in df.columns:
        st.subheader("🗺 Dropoff Locations Map")
        st.map(df[["dropoff_latitude", "dropoff_longitude"]].dropna().head(20000))

    # Tip Analysis
    if "tip_amount" in df.columns:
        st.subheader("💵 Tip Analysis")
        tip_fig = px.box(df, y="tip_amount", title="Tip Amount Distribution")
        st.plotly_chart(tip_fig, use_container_width=True)

    # Vendor Comparison
    if "VendorID" in df.columns:
        st.subheader("🏢 Vendor Comparison")
        vendor_fig = px.pie(df, names="VendorID", title="Trips by Vendor")
        st.plotly_chart(vendor_fig, use_container_width=True)

    # Correlation Heatmap
    st.subheader("🔥 Correlation Heatmap")
    numeric_df = df.select_dtypes(include=[np.number])
    heat_fig = px.imshow(numeric_df.corr(), text_auto=True, title="Correlation Between Features")
    st.plotly_chart(heat_fig, use_container_width=True)

else:
    st.info("⬆ Upload a NYC Taxi CSV file to start analysis.")
