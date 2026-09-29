"""
dashboard.py - Dashboard Giám sát Realtime & Tiền xử lý dữ liệu IoT (Streamlit)
"""
import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

load_dotenv()

st.set_page_config(
    page_title="IoT Data Monitoring - BTH2",
    page_icon="📊",
    layout="wide"
)

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "ptit_iot")
INFLUX_BUCKET_RAW = os.getenv("INFLUXDB_BUCKET_RAW", "sensor_raw")

@st.cache_resource
def get_influx_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def load_data(measurement_name):
    client = get_influx_client()
    query_api = client.query_api()
    query = f'''
    from(bucket: "{INFLUX_BUCKET_RAW}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "{measurement_name}")
      |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    try:
        df = query_api.query_data_frame(query)
        if isinstance(df, list):
            df = pd.concat(df)
        if not df.empty:
            df['_time'] = pd.to_datetime(df['_time'])
            df = df.set_index('_time').sort_index()
        return df
    except Exception as e:
        st.error(f"Lỗi truy vấn InfluxDB: {e}")
        return pd.DataFrame()

# Giao diện chính
st.title("🌐 BÀI THỰC HÀNH SỐ 2: GIÁM SÁT & TIỀN XỬ LÝ DỮ LIỆU IOT")
st.markdown("---")

# Thanh điều hướng Sidebar
st.sidebar.header("⚙️ Tùy chọn Giám sát")
view_mode = st.sidebar.radio("Chọn Chế độ xem:", ["1. Real-time Monitoring", "2. Processed Data Analysis"])

if st.sidebar.button("🔄 Làm mới dữ liệu"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Hệ thống: Mosquitto MQTT + InfluxDB 2.x + Streamlit Dashboard")

if view_mode == "1. Real-time Monitoring":
    st.header("⚡ Dữ liệu Cảm biến Thời gian thực (Raw Data)")
    
    df_raw = load_data("environment_raw")
    
    if df_raw.empty:
        st.warning("⚠️ Chưa có dữ liệu thô. Hãy đảm bảo `collector.py` và `simulator.py` đang chạy.")
    else:
        latest = df_raw.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nhiệt độ (°C)", f"{latest.get('temperature', 0):.1f} °C")
        col2.metric("Độ ẩm (%)", f"{latest.get('humidity', 0):.1f} %" if pd.notna(latest.get('humidity')) else "N/A")
        col3.metric("Ánh sáng (Lux)", f"{latest.get('light', 0):.1f} Lux")
        col4.metric("Độ trễ Latency", f"{latest.get('latency_ms', 0):.2f} ms")

        st.subheader("📈 Biểu đồ biến thiên dữ liệu thô (Raw Time-Series)")
        
        fig = go.Figure()
        if 'temperature' in df_raw.columns:
            fig.add_trace(go.Scatter(x=df_raw.index, y=df_raw['temperature'], mode='lines+markers', name='Nhiệt độ (°C)'))
        if 'humidity' in df_raw.columns:
            fig.add_trace(go.Scatter(x=df_raw.index, y=df_raw['humidity'], mode='lines+markers', name='Độ ẩm (%)'))
        if 'light' in df_raw.columns:
            fig.add_trace(go.Scatter(x=df_raw.index, y=df_raw['light'], mode='lines', name='Ánh sáng (Lux)'))
        
        fig.update_layout(title="Biến thiên thông số cảm biến theo thời gian", xaxis_title="Thời gian", yaxis_title="Giá trị", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 10 Bản ghi thô gần nhất")
        st.dataframe(df_raw.tail(10)[['device_id', 'temperature', 'humidity', 'light', 'latency_ms']])

elif view_mode == "2. Processed Data Analysis":
    st.header("🧹 Dữ liệu sau Tiền xử lý (Processed Data)")
    
    df_proc = load_data("environment_processed")
    
    if df_proc.empty:
        st.warning("⚠️ Chưa có dữ liệu đã tiền xử lý. Hãy chạy `processor.py` để tạo dữ liệu sạch.")
    else:
        st.success(f"✅ Đã tải {len(df_proc)} bản ghi đã qua xử lý (Lọc Outlier IQR, Điền Missing, Resampling, Standard Scaler).")

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 So sánh Dữ liệu Gốc & Smooth (Rolling Mean)")
            fig_roll = go.Figure()
            if 'temperature' in df_proc.columns:
                fig_roll.add_trace(go.Scatter(x=df_proc.index, y=df_proc['temperature'], mode='lines', name='Temp Sạch'))
            if 'temperature_rolling_mean' in df_proc.columns:
                fig_roll.add_trace(go.Scatter(x=df_proc.index, y=df_proc['temperature_rolling_mean'], mode='lines', name='Temp Rolling Mean (30s)'))
            fig_roll.update_layout(title="Làm mịn Nhiệt độ (Rolling Mean)", template="plotly_white")
            st.plotly_chart(fig_roll, use_container_width=True)

        with col2:
            st.subheader("📏 Dữ liệu đã Chuẩn hóa (MinMaxScaler [0, 1])")
            fig_scale = go.Figure()
            if 'temperature_scaled' in df_proc.columns:
                fig_scale.add_trace(go.Scatter(x=df_proc.index, y=df_proc['temperature_scaled'], name='Temp Scaled'))
            if 'humidity_scaled' in df_proc.columns:
                fig_scale.add_trace(go.Scatter(x=df_proc.index, y=df_proc['humidity_scaled'], name='Hum Scaled'))
            if 'light_scaled' in df_proc.columns:
                fig_scale.add_trace(go.Scatter(x=df_proc.index, y=df_proc['light_scaled'], name='Light Scaled'))
            fig_scale.update_layout(title="Chuẩn hóa MinMax [0, 1]", template="plotly_white")
            st.plotly_chart(fig_scale, use_container_width=True)

        st.subheader("📋 Bảng dữ liệu đặc trưng đã trích xuất")
        st.dataframe(df_proc.tail(10))
