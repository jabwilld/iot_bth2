# KỊCH BẢN DEMO THỰC HÀNH BÀI 2 IOT (5-10 PHÚT)

---

### 🕒 0:00 – 1:00 | Giới thiệu Bài toán & Kiến trúc Hệ thống
- **Hành động:** Mở slide/sơ đồ kiến trúc trong README.md hoặc Báo cáo Word.
- **Lời nói:** 
  > *"Em xin chào Thầy/Cô. Sau đây em xin demo Bài thực hành số 2 môn IoT và Ứng dụng. Bài toán của em bao gồm pipeline 4 tầng: Tầng mô phỏng cảm biến qua MQTT, Tầng thu thập Collector, Tầng lưu trữ chuỗi thời gian InfluxDB 2.x, Tầng tiền xử lý dữ liệu tự động và Tầng trực quan hóa Dashboard bằng Streamlit."*

---

### 🕒 1:00 – 2:00 | Khởi động MQTT Broker & Terminal Simulator
- **Hành động:** 
  1. Mở Terminal 1: Kiểm tra Mosquitto Broker đang chạy (`netstat -ano | findstr 1883`).
  2. Mở Terminal 2: Chạy `.\.venv\Scripts\python.exe simulator.py`.
- **Lời nói:** 
  > *"Đầu tiên, Mosquitto MQTT Broker đang chạy local ở port 1883. Simulator mô phỏng cảm biến ESP32 đọc thông số Nhiệt độ, Độ ẩm, Ánh sáng, đóng gói JSON cùng UTC Timestamp và publish liên tục 1 giây/lần lên topic `sensor/dht22`."*

---

### 🕒 2:00 – 3:00 | Khởi động Collector & Chứng minh Latency real-time
- **Hành động:** 
  - Mở Terminal 3: Chạy `.\.venv\Scripts\python.exe collector.py`.
- **Lời nói:** 
  > *"Collector kết nối subscribe topic `sensor/dht22`. Khi có message, Collector kiểm tra tính hợp lệ JSON (Schema validation), tính toán độ trễ End-to-End Latency ngay thời điểm nhận (trung bình ~0.44 ms) và ghi trực tiếp điểm dữ liệu thô vào InfluxDB bucket `sensor_raw`."*

---

### 🕒 3:00 – 4:00 | Chứng minh Dữ liệu thô trong InfluxDB Web UI
- **Hành động:** Mở trình duyệt web tại `http://localhost:8086`, chọn Data Explorer -> Bucket `sensor_raw` -> Measurement `environment_raw` -> Nút Submit.
- **Lời nói:** 
  > *"Đây là giao diện quản trị InfluxDB. Dữ liệu thô đang được bơm liên tục vào measurement `environment_raw`. Trong dữ liệu này có xuất hiện các điểm khuyết (Missing value) và các điểm bất thường do nhiễu cảm biến (Outliers)."*

---

### 4:00 – 5:00 | Chạy Script Tiền xử lý dữ liệu (processor.py)
- **Hành động:** Mở Terminal 4: Chạy `.\.venv\Scripts\python.exe processor.py`.
- **Lời nói:** 
  > *"Bây giờ em chạy script tiền xử lý `processor.py`. Chương trình sẽ thực hiện: 
  > 1. Lọc Outlier bất thường bằng thuật toán IQR (Interquartile Range).
  > 2. Nội suy điểm thiếu (Interpolation).
  > 3. Resampling theo cửa sổ thời gian 10 giây.
  > 4. Trích xuất đặc trưng Rolling Mean & Delta.
  > 5. Chuẩn hóa MinMaxScaler về dải [0, 1] và ghi vào bucket `sensor_processed`."*

---

### 🕒 5:00 – 7:00 | Chứng minh Dữ liệu Processed trong InfluxDB
- **Hành động:** Trên InfluxDB Web UI (`http://localhost:8086`), chuyển sang xem Bucket `sensor_processed` -> Measurement `environment_processed`.
- **Lời nói:** 
  > *"Dữ liệu sau khi xử lý đã được ghi thành công vào bucket `sensor_processed`. Số bản ghi được gom nhóm nén từ 190 bản ghi thô xuống 68 bản ghi sạch."*

---

### 🕒 7:00 – 9:00 | Mở Dashboard Streamlit
- **Hành động:** 
  1. Chạy `.\.venv\Scripts\streamlit.exe run dashboard.py`.
  2. Trình duyệt mở `http://localhost:8501`.
  3. Thao tác chuyển giữa **1. Real-time Monitoring** và **2. Processed Data Analysis**.
- **Lời nói:** 
  > *"Giao diện Dashboard Streamlit cho phép giám sát real-time chỉ số nhiệt độ, độ ẩm, ánh sáng và độ trễ latency. Khi chuyển sang tab Processed Analysis, ta thấy biểu đồ so sánh đường dữ liệu làm mịn Rolling Mean và biểu đồ chuẩn hóa MinMax."*

---

### 🕒 9:00 – 10:00 | Nêu Kết quả & Kết luận
- **Hành động:** Mở Báo cáo Word hoặc slide kết quả.
- **Lời nói:** 
  > *"Tổng kết hệ thống: Thu thập 190 bản ghi thô, độ trễ trung bình siêu thấp 0.444 ms, xử lý thành công 4 bản ghi thiếu độ ẩm, lọc 3 outlier nhiệt độ và nén thành 68 bản ghi processed sạch. Em đã hoàn thiện toàn bộ yêu cầu đề bài. Em xin cảm ơn Thầy/Cô!"*
