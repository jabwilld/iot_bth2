# BÀI THỰC HÀNH SỐ 2: THU THẬP, LƯU TRỮ VÀ TIỀN XỬ LÝ DỮ LIỆU IOT
**Học phần:** IoT và Ứng dụng (INT14149) - PTIT

---

## 1. Giới thiệu Bài toán
Hệ thống thu thập dữ liệu cảm biến thời gian thực thông qua giao thức **MQTT**, lưu trữ chuỗi thời gian vào **InfluxDB 2.x**, tiến hành **tiền xử lý dữ liệu thô** (làm sạch, lọc outlier IQR, nội suy missing value, resampling 10s, trích xuất đặc trưng và chuẩn hóa MinMax) và hiển thị trực quan hóa trên **Dashboard Streamlit**.

---

## 2. Kiến trúc Hệ thống

```text
Python Simulator (ESP32 Cảm biến mô phỏng)
      ↓ Publish JSON (Topic: sensor/dht22)
MQTT Mosquitto Broker (Port 1883)
      ↓ Subscribe & Validate JSON
collector.py (Tính End-to-End Latency)
      ↓ Write Raw Points
InfluxDB Raw Bucket (sensor_raw)
      ↓ Read Raw Data
processor.py (IQR, Interpolation, Resampling 10s, MinMaxScaler)
      ↓ Write Clean Points
InfluxDB Processed Bucket (sensor_processed)
      ↓ Query & Display
dashboard.py (Streamlit Web UI - Real-time & Processed)
```

---

## 3. Yêu cầu Môi trường
- **Hệ điều hành:** Windows 10/11
- **Ngôn ngữ:** Python 3.10+
- **MQTT Broker:** Eclipse Mosquitto (Port 1883)
- **Database:** InfluxDB 2.x (Port 8086)
- **Công cụ hỗ trợ:** VS Code, Git

---

## 4. Cấu trúc Project

```text
iot_bth2/
├── .env.example          # File cấu hình biến môi trường mẫu
├── .gitignore            # Cấu hình bỏ qua file tạm, .venv, .env
├── requirements.txt      # Danh sách thư viện Python
├── simulator.py          # Mô phỏng thiết bị cảm biến IoT (MQTT Publisher)
├── collector.py          # Thu thập dữ liệu, validate, tính latency & ghi DB (MQTT Subscriber)
├── processor.py          # Tiền xử lý dữ liệu (Clean, IQR, Resample, Scaler)
└── dashboard.py          # Streamlit Dashboard giám sát Realtime & Processed Data
```

---

## 5. Hướng dẫn Cài đặt & Khởi chạy

### Bước 1: Chuẩn bị Virtual Environment & Cài Python Packages
```powershell
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt trên Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

### Bước 2: Khởi động Mosquitto MQTT Broker (Port 1883)
```powershell
net start mosquitto
```
*(Hoặc chạy tập tin `mosquitto.exe -v`)*

### Bước 3: Khởi động InfluxDB 2.x (Port 8086)
```powershell
# Chạy InfluxDB server
C:\influxdb\influxd.exe
```
Mở trình duyệt truy cập `http://localhost:8086`, tạo Organization `ptit_iot` và Bucket `sensor_raw`, `sensor_processed`. Copy chuỗi **API Token**.

### Bước 4: Cấu hình File `.env`
Tạo file `.env` từ file mẫu `.env.example`:
```ini
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=sensor/dht22

INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_actual_influx_api_token_here
INFLUXDB_ORG=ptit_iot
INFLUXDB_BUCKET_RAW=sensor_raw
INFLUXDB_BUCKET_PROCESSED=sensor_processed
```

### Bước 5: Thực thi Pipeline theo thứ tự 4 Terminal

- **Terminal 1 - Chạy Collector (Subscribe & Write Raw DB):**
  ```powershell
  .\.venv\Scripts\python.exe collector.py
  ```

- **Terminal 2 - Chạy Simulator (Publish JSON Data):**
  ```powershell
  .\.venv\Scripts\python.exe simulator.py
  ```

- **Terminal 3 - Chạy Processor (Tiền xử lý & Write Processed DB):**
  ```powershell
  .\.venv\Scripts\python.exe processor.py
  ```

- **Terminal 4 - Bật Streamlit Dashboard:**
  ```powershell
  .\.venv\Scripts\streamlit.exe run dashboard.py
  ```
  *Truy cập Web UI tại:* `http://localhost:8501`

---

## 6. Kết quả Thực nghiệm Thực tế

Đo đạc thực tế 100% từ hệ thống (trích xuất trực tiếp từ InfluxDB Database):

| Chỉ số thực nghiệm | Kết quả đo đạc |
| :--- | :--- |
| **Tổng số bản ghi thô (Raw Records)** | **190 bản ghi** |
| **Độ trễ End-to-End Latency trung bình** | **0.444 ms** |
| **Độ trễ nhỏ nhất (Min Latency)** | **0.000 ms** |
| **Độ trễ lớn nhất (Max Latency)** | **1.456 ms** |
| **Số bản ghi bị thiếu độ ẩm (Missing Value)** | **4 bản ghi** |
| **Số bản ghi nhiễu bất thường (Temperature IQR Outliers)** | **3 bản ghi** |
| **Cửa sổ Resampling (Resampling Window)** | **10 giây** |
| **Số bản ghi sau tiền xử lý (Processed Records)** | **68 bản ghi** |
