from surveys.models import Survey, SurveyResponse
from datetime import date

# =========================
# KHẢO SÁT
# =========================

survey1, _ = Survey.objects.get_or_create(
    title="Đánh giá chất lượng hệ thống giao thông Đà Nẵng năm 2025",
    defaults={
        "description": "Khảo sát mức độ hài lòng của người dân về chất lượng đường giao thông, đèn tín hiệu và hạ tầng đô thị.",
        "is_active": True,
        "deadline": date(2025, 12, 31),
        "created_by": None
    }
)

survey2, _ = Survey.objects.get_or_create(
    title="Khảo sát tình trạng đèn giao thông tại các nút giao trọng điểm",
    defaults={
        "description": "Thu thập ý kiến người dân về hiệu quả hoạt động của hệ thống đèn tín hiệu giao thông.",
        "is_active": True,
        "deadline": date(2025, 11, 30),
        "created_by": None
    }
)

survey3, _ = Survey.objects.get_or_create(
    title="Khảo sát chất lượng đường ven biển Đà Nẵng",
    defaults={
        "description": "Đánh giá chất lượng các tuyến đường ven biển phục vụ du lịch và giao thông.",
        "is_active": True,
        "deadline": date(2025, 10, 31),
        "created_by": None
    }
)