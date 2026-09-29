# CHECKLIST NỘP BÀI THỰC HÀNH SỐ 2 IOT

---

## 📋 Danh mục Kiểm tra Mã nguồn & Tài liệu

- [x] **Source code Python hoàn chỉnh:**
  - [x] `simulator.py` (Mô phỏng cảm biến ESP32, Publish JSON)
  - [x] `collector.py` (Subscribe MQTT, Validate JSON, tính Latency, ghi InfluxDB)
  - [x] `processor.py` (Lọc IQR Outliers, Interpolation, Resampling 10s, MinMaxScaler)
  - [x] `dashboard.py` (Streamlit Web UI Real-time & Processed Data)
- [x] **File Cấu hình & Quản lý Thư viện:**
  - [x] `requirements.txt` (Khai báo đủ paho-mqtt, influxdb-client, pandas, streamlit,...)
  - [x] `.env.example` (File biến môi trường mẫu)
  - [x] `.gitignore` (Đã chặn commit `.venv`, `.env`, cache Python)
  - [x] `README.md` (Hướng dẫn cài đặt & khởi chạy từ A-Z)
- [x] **Tài liệu & Báo cáo:**
  - [x] `report/Bao_cao_BTH2_IoT.docx` (Báo cáo Word chuẩn 4-6 trang)
  - [x] `docs/DEMO.md` (Kịch bản demo 5-10 phút chi tiết)
  - [x] `docs/QA.md` (Bộ 20 câu hỏi & đáp bảo vệ đồ án)
- [x] **Vận hành Hệ thống Thực tế:**
  - [x] MQTT Mosquitto Broker chạy ổn định tại port 1883
  - [x] InfluxDB 2.x Server chạy ổn định tại port 8086 (Bucket `sensor_raw` & `sensor_processed`)
  - [x] Pipeline End-to-End hoạt động trôi chảy (Simulator -> Collector -> InfluxDB -> Processor -> Dashboard)
  - [x] Streamlit Dashboard hiển thị mượt mà tại `http://localhost:8501`
- [x] **Quản lý Mã nguồn Git:**
  - [x] Đã khởi tạo Git Repository (`main` branch)
  - [x] Đã tạo commit mã nguồn sạch (Không dính `.env` token thật hoặc `.venv`)
