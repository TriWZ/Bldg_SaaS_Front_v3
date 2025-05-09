
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Triphorium Energy Dashboard", layout="wide")

API_UPLOAD = "https://bldgsaas-back-v1.onrender.com/energy/upload"
API_ENERGY = "https://bldgsaas-back-v1.onrender.com/energy/data"

st.title("Triphorium Energy Dashboard")

# Sidebar building info
st.sidebar.header("Building Info")
address = st.sidebar.text_input("Address", "New York, NY")
area = st.sidebar.number_input("Floor Area (sqft)", value=100000)
climate_zone = "4A - Mixed-Humid" if "NY" in address else "Unknown"
st.markdown(f"**Climate Zone**: {climate_zone}")

# Upload and display CSV
st.subheader("Upload your building energy CSV")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head(), use_container_width=True)

    if st.button("Upload to Backend"):
        try:
            res = requests.post(API_UPLOAD, files={"file": uploaded_file.getvalue()})
            if res.status_code == 200:
                st.success("✅ Upload successful!")
            else:
                st.error(f"❌ Upload failed: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        st.subheader("📈 Monthly Energy Usage Trends")
        fig = px.line(df, x="timestamp", y=["electricity_kwh", "gas_m3", "water_tons", "co2_tons"],
                      labels={"value": "Usage", "variable": "Utility"}, title="Utility Usage Over Time")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🧊 Utility Use Composition")
        latest = df.iloc[-1]
        pie_df = pd.DataFrame({
            "Utility": ["Electricity", "Gas", "Water", "CO2"],
            "Value": [latest["electricity_kwh"], latest["gas_m3"], latest["water_tons"], latest["co2_tons"]]
        })
        fig2 = px.pie(pie_df, names="Utility", values="Value", title="Latest Month Utility Proportion")
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Could not render chart: {e}")

# ROI & impact
st.subheader("💰 Financial Impact Summary")
investment = st.number_input("Investment Cost ($)", value=30000)
electricity_price = st.number_input("Electricity Price ($/kWh)", value=0.18)
try:
    saving_kwh = df["electricity_kwh"].mean() * 0.2
    saving = saving_kwh * electricity_price
    roi = saving / investment * 100
    payback = investment / saving
    st.metric("Annual Saving ($)", f"{saving:.2f}")
    st.metric("ROI (%)", f"{roi:.2f}")
    st.metric("Payback Period (yrs)", f"{payback:.2f}")
except:
    st.info("Upload data to estimate ROI.")

st.subheader("🏆 CO₂ Benchmark Grade")
try:
    co2 = df["co2_tons"].mean() * 12
    if co2 < 400:
        grade = "A"
    elif co2 < 600:
        grade = "B"
    elif co2 < 800:
        grade = "C"
    else:
        grade = "D"
    st.success(f"Annual CO₂: {co2:.0f} tons → Grade {grade}")
except:
    st.warning("No CO₂ data available.")

st.subheader("🧠 Energy Efficiency Recommendations")
st.markdown("""
- Tune HVAC operations with occupancy sensors
- Replace outdated lighting with LEDs
- Install building automation system (BAS)
- Regularly track & compare utility performance
- Upgrade to high-efficiency pumps & fans
""")
