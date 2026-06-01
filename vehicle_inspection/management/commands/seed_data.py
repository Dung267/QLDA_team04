from vehicle_inspection.models import InspectionCenter

# =====================================
# TRUNG TÂM ĐĂNG KIỂM ĐÀ NẴNG
# =====================================

InspectionCenter.objects.get_or_create(
    name="Trung tâm Đăng kiểm 43-01S",
    defaults={
        "address": "47 Điện Biên Phủ, Quận Thanh Khê, TP. Đà Nẵng",
        "phone": "0236 388 8888",
        "is_active": True
    }
)

InspectionCenter.objects.get_or_create(
    name="Trung tâm Đăng kiểm 43-02S",
    defaults={
        "address": "Đường Lê Văn Hiến, Quận Ngũ Hành Sơn, TP. Đà Nẵng",
        "phone": "0236 377 7777",
        "is_active": True
    }
)

InspectionCenter.objects.get_or_create(
    name="Trung tâm Đăng kiểm 43-03S",
    defaults={
        "address": "Đường Nguyễn Tất Thành, Quận Liên Chiểu, TP. Đà Nẵng",
        "phone": "0236 366 6666",
        "is_active": True
    }
)

InspectionCenter.objects.get_or_create(
    name="Trung tâm Đăng kiểm 43-04D",
    defaults={
        "address": "Quốc lộ 1A, Huyện Hòa Vang, TP. Đà Nẵng",
        "phone": "0236 355 5555",
        "is_active": True
    }
)

print("Đã tạo dữ liệu mẫu trung tâm đăng kiểm.")