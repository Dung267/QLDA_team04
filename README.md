# Hệ thống Quản lý Hạ tầng Đô thị

## Giới thiệu

Dự án Django đầy đủ tính năng cho quản lý hạ tầng đô thị bao gồm:

- **Quản lý tài khoản**: Đăng ký, đăng nhập, OTP 2FA, phân quyền vai trò
- **Hạ tầng đường bộ**: Tuyến đường, ổ gà, đèn giao thông, lịch sử sửa chữa  
- **Bảo trì & Phản ánh**: Gửi phản ánh, phân công, theo dõi tiến độ
- **Ngập lụt & Thiên tai**: Cảnh báo thời gian thực qua WebSocket
- **Chatbot hỗ trợ**: Trả lời tự động dựa trên FAQ
- **Đăng kiểm phương tiện**: Đặt lịch, kiểm tra, cấp chứng nhận
- **Giấy phép thi công**: Nộp hồ sơ online, phê duyệt điện tử
- **Nhân sự**: Quản lý nhân viên, phân công, nghỉ phép, đào tạo
- **Hợp đồng & Đấu thầu**: Quản lý toàn bộ vòng đời hợp đồng
- **Vật tư**: Kho vật tư, nhập/xuất, dự báo nhu cầu
- **Thống kê & Báo cáo**: Xuất Excel/PDF, biểu đồ phân tích
- **Bản đồ tương tác**: Leaflet.js với các lớp dữ liệu hạ tầng
- **Backup**: Sao lưu/khôi phục tự động
- **Tích hợp API**: OAuth, SMS gateway, webhook

## Cài đặt

### 1. Yêu cầu
- Python 3.10+
- pip
- (Tuỳ chọn) Redis cho Celery + WebSocket

### 2. Thiết lập môi trường ảo
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
cp .env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

### 5. Migrate database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo dữ liệu mẫu
```bash
python manage.py loaddata fixtures/initial_data.json
# Hoặc tạo superuser:
python manage.py createsuperuser
```

### 7. Chạy server
```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## Cấu trúc ứng dụng

| App | Chức năng |
|-----|-----------|
| `accounts` | Người dùng, xác thực, OTP, session |
| `infrastructure` | Đường, đèn, hạ tầng |
| `maintenance` | Phản ánh, bảo trì, lịch |
| `notifications` | Thông báo, WebSocket |
| `inventory` | Kho vật tư |
| `flood` | Cảnh báo ngập lụt |
| `chatbot` | Chatbot hỗ trợ |
| `hr` | Nhân sự |
| `maps` | Bản đồ Leaflet |
| `contracts` | Hợp đồng, đấu thầu |
| `weather` | Thời tiết |
| `surveys` | Khảo sát |
| `documents` | Tài liệu |
| `backup` | Sao lưu |
| `permits` | Giấy phép thi công |
| `vehicle_inspection` | Đăng kiểm xe |
| `feedback` | Phản hồi hệ thống |
| `integration` | Tích hợp API |
| `reports` | Báo cáo, xuất file |

## Vai trò người dùng
- `admin` – Quản trị viên hệ thống
- `manager` – Quản lý
- `staff` – Cán bộ kỹ thuật
- `inspector` – Kiểm định viên
- `citizen` – Người dân

## API Endpoints
- `/api/accounts/` – Người dùng
- `/api/infrastructure/` – Hạ tầng
- `/api/maintenance/` – Bảo trì
- `/api/flood/alerts/` – Cảnh báo ngập
- `/api/weather/current/` – Thời tiết
- `/api/chatbot/chat/` – Chatbot

## WebSocket
- `ws://localhost:8000/ws/notifications/` – Thông báo realtime
- `ws://localhost:8000/ws/flood/` – Cảnh báo ngập realtime
