from django.core.management.base import BaseCommand
from infrastructure.models import (
    InfrastructureType,
    ManagementZone,
    Road,
    TrafficLight,
    Infrastructure,
    Pothole,
    RoadRepairHistory
)


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu hạ tầng Đà Nẵng"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Đang tạo dữ liệu mẫu..."))

        # =========================
        # Loại hạ tầng
        # =========================
        bridge, _ = InfrastructureType.objects.get_or_create(
            code="BRIDGE",
            defaults={
                "name": "Cầu giao thông",
                "description": "Các công trình cầu giao thông."
            }
        )

        tunnel, _ = InfrastructureType.objects.get_or_create(
            code="TUNNEL",
            defaults={
                "name": "Hầm giao thông",
                "description": "Các công trình hầm giao thông."
            }
        )

        drain, _ = InfrastructureType.objects.get_or_create(
            code="DRAIN",
            defaults={
                "name": "Cống thoát nước",
                "description": "Hệ thống thoát nước đô thị."
            }
        )

        camera, _ = InfrastructureType.objects.get_or_create(
            code="CAMERA",
            defaults={
                "name": "Camera giao thông",
                "description": "Camera giám sát giao thông."
            }
        )

        # =========================
        # Khu vực quản lý
        # =========================
        hai_chau, _ = ManagementZone.objects.get_or_create(
            name="Trung tâm Hải Châu",
            district="Hải Châu",
            defaults={
                "description": "Khu vực trung tâm hành chính thành phố."
            }
        )

        son_tra, _ = ManagementZone.objects.get_or_create(
            name="Ven biển Sơn Trà",
            district="Sơn Trà",
            defaults={
                "description": "Khu vực du lịch ven biển."
            }
        )

        thanh_khe, _ = ManagementZone.objects.get_or_create(
            name="Thanh Khê",
            district="Thanh Khê",
            defaults={
                "description": "Khu dân cư và thương mại."
            }
        )

        lien_chieu, _ = ManagementZone.objects.get_or_create(
            name="Liên Chiểu",
            district="Liên Chiểu",
            defaults={
                "description": "Khu công nghiệp và cảng biển."
            }
        )

        # =========================
        # Tuyến đường
        # =========================
        roads_data = [
        {
        "name": "Đường Bạch Đằng",
        "code": "DN-R001",
        "zone": hai_chau,
        "length_km": 3.2,
        "width_m": 24,
        "lanes": 4,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "high",
        "built_year": 2005
        },
        {
        "name": "Đường Nguyễn Văn Linh",
        "code": "DN-R002",
        "zone": hai_chau,
        "length_km": 5.1,
        "width_m": 32,
        "lanes": 6,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "very_high",
        "built_year": 2003
        },
        {
        "name": "Đường Võ Nguyên Giáp",
        "code": "DN-R003",
        "zone": son_tra,
        "length_km": 12.8,
        "width_m": 30,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "high",
        "built_year": 2012
        },
        {
        "name": "Đường Hoàng Sa",
        "code": "DN-R004",
        "zone": son_tra,
        "length_km": 9.5,
        "width_m": 20,
        "lanes": 4,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "medium",
        "built_year": 2010
        },
        {
        "name": "Đường Trường Sa",
        "code": "DN-R005",
        "zone": son_tra,
        "length_km": 15.0,
        "width_m": 24,
        "lanes": 4,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "high",
        "built_year": 2011
        },

        # Thêm mới

        {
        "name": "Đường Lê Duẩn",
        "code": "DN-R006",
        "zone": hai_chau,
        "length_km": 4.3,
        "width_m": 26,
        "lanes": 4,
        "status": "good",
        "quality_score": 4,
        "traffic_density": "high",
        "built_year": 2000
        },
        {
        "name": "Đường Điện Biên Phủ",
        "code": "DN-R007",
        "zone": thanh_khe,
        "length_km": 7.8,
        "width_m": 30,
        "lanes": 6,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "very_high",
        "built_year": 2002
        },
        {
        "name": "Đường Hàm Nghi",
        "code": "DN-R008",
        "zone": hai_chau,
        "length_km": 3.6,
        "width_m": 20,
        "lanes": 4,
        "status": "good",
        "quality_score": 4,
        "traffic_density": "high",
        "built_year": 2004
        },
        {
        "name": "Đường Phan Châu Trinh",
        "code": "DN-R009",
        "zone": hai_chau,
        "length_km": 2.8,
        "width_m": 18,
        "lanes": 4,
        "status": "normal",
        "quality_score": 3,
        "traffic_density": "high",
        "built_year": 1998
        },
        {
        "name": "Đường Ngô Quyền",
        "code": "DN-R010",
        "zone": son_tra,
        "length_km": 8.2,
        "width_m": 28,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "high",
        "built_year": 2007
        },
        {
        "name": "Đường Phạm Văn Đồng",
        "code": "DN-R011",
        "zone": son_tra,
        "length_km": 4.5,
        "width_m": 30,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "high",
        "built_year": 2008
        },
        {
        "name": "Đường Tôn Đức Thắng",
        "code": "DN-R012",
        "zone": lien_chieu,
        "length_km": 11.4,
        "width_m": 24,
        "lanes": 4,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "high",
        "built_year": 2001
        },
        {
        "name": "Đường Nguyễn Tất Thành",
        "code": "DN-R013",
        "zone": lien_chieu,
        "length_km": 14.2,
        "width_m": 28,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "medium",
        "built_year": 2006
        },
        {
        "name": "Đường Âu Cơ",
        "code": "DN-R014",
        "zone": lien_chieu,
        "length_km": 10.1,
        "width_m": 18,
        "lanes": 4,
        "status": "normal",
        "quality_score": 3,
        "traffic_density": "medium",
        "built_year": 1999
        },
        {
        "name": "Đường Võ Chí Công",
        "code": "DN-R015",
        "zone": son_tra,
        "length_km": 13.6,
        "width_m": 32,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "high",
        "built_year": 2015
        },
        {
        "name": "Đường 2 Tháng 9",
        "code": "DN-R016",
        "zone": hai_chau,
        "length_km": 6.7,
        "width_m": 30,
        "lanes": 6,
        "status": "good",
        "quality_score": 5,
        "traffic_density": "very_high",
        "built_year": 2004
        },
        {
        "name": "Đường Núi Thành",
        "code": "DN-R017",
        "zone": hai_chau,
        "length_km": 5.0,
        "width_m": 24,
        "lanes": 4,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "high",
        "built_year": 2002
        },
        {
        "name": "Đường Duy Tân",
        "code": "DN-R018",
        "zone": hai_chau,
        "length_km": 3.8,
        "width_m": 22,
        "lanes": 4,
        "status": "good",
        "quality_score": 4,
        "traffic_density": "medium",
        "built_year": 2005
        },
        {
        "name": "Đường Nguyễn Hữu Thọ",
        "code": "DN-R019",
        "zone": hai_chau,
        "length_km": 8.5,
        "width_m": 28,
        "lanes": 6,
        "status": "normal",
        "quality_score": 4,
        "traffic_density": "very_high",
        "built_year": 2008
        },
        {
        "name": "Đường Lê Văn Hiến",
        "code": "DN-R020",
        "zone": son_tra,
        "length_km": 7.2,
        "width_m": 20,
        "lanes": 4,
        "status": "good",
        "quality_score": 4,
        "traffic_density": "medium",
        "built_year": 2010
        }
    ]

        roads = []

        for item in roads_data:
            road, _ = Road.objects.get_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "direction": "two_way",
                    "status": item["status"],
                    "quality_score": item["quality_score"],
                    "length_km": item["length_km"],
                    "width_m": item["width_m"],
                    "lanes": item["lanes"],
                    "built_year": item["built_year"],
                    "traffic_density": item["traffic_density"],
                    "zone": item["zone"],
                    "managing_unit": "Sở GTVT Đà Nẵng",
                    "start_point": "Điểm đầu",
                    "end_point": "Điểm cuối"
                }
            )

            roads.append(road)

        # =========================
        # Đèn giao thông
        # =========================
        TrafficLight.objects.get_or_create(
            code="TL-DN-001",
            defaults={
                "location": "Ngã tư Nguyễn Văn Linh - Phan Châu Trinh",
                "road": roads[1],
                "status": "active",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": hai_chau
            }
        )

        TrafficLight.objects.get_or_create(
            code="TL-DN-002",
            defaults={
                "location": "Ngã tư Võ Nguyên Giáp - Phạm Văn Đồng",
                "road": roads[2],
                "status": "maintenance",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": son_tra
            }
        )

        TrafficLight.objects.get_or_create(
            code="TL-DN-003",
            defaults={
                "location": "Ngã tư Bạch Đằng - Lê Duẩn",
                "road": roads[0],
                "status": "active",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": hai_chau
            }
        )

        # =========================
        # Công trình hạ tầng
        # =========================
        Infrastructure.objects.get_or_create(
            code="INF-BR-001",
            defaults={
                "type": bridge,
                "name": "Cầu Rồng",
                "status": "good",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": hai_chau,
                "description": "Biểu tượng thành phố Đà Nẵng.",
                "expected_lifespan_years": 100
            }
        )

        Infrastructure.objects.get_or_create(
            code="INF-BR-002",
            defaults={
                "type": bridge,
                "name": "Cầu Sông Hàn",
                "status": "good",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": hai_chau,
                "description": "Cầu quay nổi tiếng của Đà Nẵng.",
                "expected_lifespan_years": 80
            }
        )

        Infrastructure.objects.get_or_create(
            code="INF-TN-001",
            defaults={
                "type": tunnel,
                "name": "Hầm chui Điện Biên Phủ",
                "status": "normal",
                "managing_unit": "Sở GTVT Đà Nẵng",
                "zone": thanh_khe,
                "description": "Hầm chui giao thông trọng điểm."
            }
        )

        # =========================
        # Ổ gà
        # =========================
        Pothole.objects.get_or_create(
            road=roads[1],
            description="Ổ gà gần giao lộ Nguyễn Văn Linh - Hàm Nghi",
            defaults={
                "severity": "moderate",
                "is_repaired": False
            }
        )

        Pothole.objects.get_or_create(
            road=roads[4],
            description="Mặt đường bong tróc sau mùa mưa",
            defaults={
                "severity": "minor",
                "is_repaired": False
            }
        )

        Pothole.objects.get_or_create(
            road=roads[3],
            description="Ổ gà ven biển ảnh hưởng giao thông",
            defaults={
                "severity": "severe",
                "is_repaired": False
            }
        )

        # =========================
        # Lịch sử sửa chữa
        # =========================
        RoadRepairHistory.objects.get_or_create(
            road=roads[0],
            repair_date="2025-03-15",
            defaults={
                "description": "Thảm lại mặt đường đoạn trung tâm.",
                "cost": 1500000000,
                "contractor": "Công ty Cầu Đường Đà Nẵng"
            }
        )

        RoadRepairHistory.objects.get_or_create(
            road=roads[1],
            repair_date="2024-09-10",
            defaults={
                "description": "Sửa chữa các điểm lún cục bộ.",
                "cost": 850000000,
                "contractor": "Công ty Hạ tầng Miền Trung"
            }
        )

        self.stdout.write(
            self.style.SUCCESS("Tạo dữ liệu mẫu thành công!")
        )