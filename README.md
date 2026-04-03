# Urban Infrastructure Management System

## Mô tả dự án
Dự án này là hệ thống quản lý hạ tầng đô thị, bao gồm các chức năng như:
- Quản lý tài khoản người dùng
- Quản lý cơ sở hạ tầng
- Quản lý sự cố và bảo trì
- Quản lý vật tư
- Thống kê và báo cáo
- Cảnh báo thiên tai và ngập lụt
- Hỗ trợ chatbot tự động

## Yêu cầu trước khi bắt đầu
Trước khi bạn bắt đầu, hãy chắc chắn rằng bạn đã cài đặt các công cụ sau:

- **Python 3.8+**: [Tải Python tại đây](https://www.python.org/downloads/)
- **MySQL**: Đảm bảo bạn có MySQL phiên bản 5.7 trở lên được cài đặt trên máy tính của mình. [Tải MySQL tại đây](https://dev.mysql.com/downloads/installer/)
- **Redis**: Dùng Redis cho việc đồng bộ các tác vụ định kỳ (ví dụ: Celery). [Tải Redis tại đây](https://redis.io/download)

## Các bước cài đặt và chạy dự án

### 1. **Clone dự án từ GitHub**
Đầu tiên, bạn cần clone dự án về máy tính của mình:

```bash
git clone https://github.com/Dung267/QLDA_team04.git

### 2. **Tạo môi trường ảo**

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

