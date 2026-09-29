# BỘ 20 CÂU HỎI VÀ CÂU TRẢ LỜI BẢO VỆ BÀI THỰC HÀNH SỐ 2 IOT

---

### Q1: Giao thức MQTT là gì? Tại sao lại dùng MQTT trong IoT?
**Trả lời:** MQTT (Message Queuing Telemetry Transport) là giao thức truyền tin dạng Publish/Subscribe hoạt động trên nền TCP/IP. Nó có băng thông cực nhẹ, tiêu tốn ít năng lượng, chịu được kết nối chập chờn, rất phù hợp cho thiết bị nhúng hạn chế tài nguyên.

### Q2: Mô hình Publisher và Subscriber hoạt động thế nào trong bài làm?
**Trả lời:** `simulator.py` đóng vai trò là **Publisher** gửi dữ liệu cảm biến JSON lên Broker. `collector.py` đóng vai trò là **Subscriber** đăng ký lắng nghe dữ liệu từ Broker để lưu vào InfluxDB.

### Q3: MQTT Broker có vai trò gì trong hệ thống này?
**Trả lời:** Mosquitto Broker làm trung tâm điều phối message. Publisher không gửi trực tiếp cho Subscriber mà gửi lên Broker; Broker dựa vào Topic để phân phối gói tin tới Subscriber tương ứng.

### Q4: Topic trong MQTT là gì? Topic trong bài của bạn là gì?
**Trả lời:** Topic là chuỗi ký tự phân loại kênh tin nhắn. Topic trong bài làm là `sensor/dht22`.

### Q5: Tại sao lại đóng gói dữ liệu dạng JSON?
**Trả lời:** JSON đơn giản, dễ đọc, chuẩn hóa cao, hỗ trợ nhiều kiểu dữ liệu (chuỗi, số, null) và tương thích hoàn hảo với các thư viện xử lý Python.

### Q6: Script `collector.py` làm nhiệm vụ gì?
**Trả lời:** `collector.py` subscribe topic MQTT, validate dữ liệu đầu vào (kiểm tra key bắt buộc), tính toán độ trễ Latency và ghi dữ liệu thô vào InfluxDB bucket `sensor_raw`.

### Q7: Tại sao lại lựa chọn InfluxDB thay vì MySQL hay MongoDB?
**Trả lời:** InfluxDB là cơ sở dữ liệu chuỗi thời gian (Time-Series Database) chuyên dụng. Nó tối ưu ghi dữ liệu tốc độ cao theo mốc thời gian (Timestamp), nén dữ liệu tốt và hỗ trợ truy vấn cửa sổ thời gian (Resampling) nhanh hơn RDBMS truyền thống.

### Q8: Schema trong InfluxDB gồm Measurement, Tag và Field khác nhau thế nào?
**Trả lời:** 
- **Measurement:** Tương đương bảng (ví dụ: `environment_raw`).
- **Tag:** Chuỗi ký tự được đánh chỉ mục (Index) để tìm kiếm nhanh (ví dụ: `device_id`).
- **Field:** Giá trị số liệu đo đạc thực tế không đánh chỉ mục (ví dụ: `temperature`, `humidity`, `light`, `latency_ms`).

### Q9: Missing Value là gì? Hệ thống xử lý missing value bằng cách nào?
**Trả lời:** Missing Value là các mốc thời gian bị mất/khuyết dữ liệu cảm biến (`None`/`NaN`). Script `processor.py` xử lý bằng phương pháp nội suy theo thời gian (`interpolate(method='time')`) kết hợp `bfill/ffill`.

### Q10: Phương pháp IQR (Interquartile Range) là gì? Dùng để làm gì?
**Trả lời:** IQR = Q3 - Q1 (Khoảng tứ phân vị giữa phần trăm 75% và 25%). Dùng để xác định các điểm Outlier (nhiễu bất thường). Những giá trị nằm ngoài khoảng `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` được coi là nhiễu và gán về `NaN` để xử lý.

### Q11: Tại sao phải xử lý Outliers?
**Trả lời:** Outliers làm méo lệch các chỉ số thống kê (như trung bình), gây ra báo động giả hoặc làm sai lệch kết quả mô hình dự báo sau này.

### Q12: Resampling theo cửa sổ 10 giây (10s window) để làm gì?
**Trả lời:** Giúp giảm tần suất dữ liệu, nén dung lượng lưu trữ (nén từ 190 bản ghi thô xuống 68 bản ghi) và làm mịn chuỗi thời gian mà không mất đi xu hướng chính.

### Q13: Rolling Mean là gì? Delta là gì?
**Trả lời:** 
- **Rolling Mean (Trung bình trượt):** Tính trung bình theo cửa sổ cuộn (30s) để làm mịn biến động dữ liệu.
- **Delta:** Tính độ chênh lệch giữa bản ghi hiện tại và bản ghi liền trước (`df.diff()`) để xem tốc độ biến đổi.

### Q14: MinMaxScaler làm gì? Tại sao phải chuẩn hóa dải [0, 1]?
**Trả lời:** Biến đổi dữ liệu nhiệt độ (20-30°C), độ ẩm (60-70%), ánh sáng (500-600 Lux) về cùng quy mô `[0, 1]` để có thể biểu diễn và so sánh trực quan trên cùng 1 biểu đồ.

### Q15: Độ trễ End-to-End Latency được tính như thế nào?
**Trả lời:** `Latency = Timestamp_nhận_tại_Collector - Timestamp_tạo_tại_Simulator`.

### Q16: Tại sao độ trễ Latency trong thực nghiệm lại rất thấp (trung bình 0.444 ms)?
**Trả lời:** Do MQTT Broker Mosquitto và các script đều chạy trên môi trường Windows Localhost (loopback network `127.0.0.1`), loại bỏ hoàn toàn độ trễ đường truyền Internet.

### Q17: Dashboard Streamlit lấy dữ liệu từ đâu?
**Trả lời:** Đọc trực tiếp từ InfluxDB bằng Flux Query qua thư viện `influxdb-client`.

### Q18: Dữ liệu Raw và Processed trên Dashboard khác nhau như thế nào?
**Trả lời:** Raw Data là dữ liệu thô ban đầu (chứa nhiễu IQR và điểm thiếu missing). Processed Data là dữ liệu đã qua lọc sạch nhiễu, làm mịn rolling mean và chuẩn hóa scale [0, 1].

### Q19: Nếu MQTT Broker bị mất kết nối thì hệ thống xử lý thế nào?
**Trả lời:** Thư viện `paho-mqtt` tích hợp cơ chế tự động kết nối lại (Auto-reconnect). Trong script có khối `try...except` để log lỗi và không làm nghẽn ứng dụng.

### Q20: Nếu InfluxDB ngừng hoạt động thì Collector có bị crash không?
**Trả lời:** Không, script `collector.py` bao bọc lệnh ghi `write_api.write()` trong khối `try...except`, ghi log báo lỗi InfluxDB ngắt kết nối và tiếp tục duy trì loop nhận MQTT.
