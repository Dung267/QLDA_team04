"""
Management command: python manage.py seed_demo
Creates demo users, sample roads, maintenance requests, etc.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Tạo dữ liệu demo cho hệ thống'

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu demo...')

        # Create users
        users_data = [
            ('admin', 'Admin', 'System', 'admin@urban.vn', 'admin', True),
            ('manager01', 'Nguyễn', 'Văn Quản', 'manager@urban.vn', 'manager', False),
            ('staff01', 'Trần', 'Thị Kỹ', 'staff@urban.vn', 'staff', False),
            ('inspector01', 'Lê', 'Văn Kiểm', 'inspector@urban.vn', 'inspector', False),
            ('citizen01', 'Phạm', 'Thị Dân', 'citizen@example.vn', 'citizen', False),
        ]
        for username, first, last, email, role, is_super in users_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, password='Demo@2024',
                    first_name=first, last_name=last,
                    email=email, role=role
                )
                if is_super:
                    u.is_superuser = True
                    u.is_staff = True
                    u.save()
                self.stdout.write(f'  ✓ User: {username} (mật khẩu: Demo@2024)')

        # Create sample roads
        try:
            from infrastructure.models import Road, ManagementZone
            zone = ManagementZone.objects.first()
            admin = User.objects.get(username='admin')
            roads_data = [
                ('Lê Duẩn', 'LD-001', 'two_way', 'good', 3.5, 12, 4, 2000),
                ('Nguyễn Văn Linh', 'NVL-001', 'two_way', 'normal', 5.2, 10, 4, 1995),
                ('Điện Biên Phủ', 'DBP-001', 'two_way', 'bad', 2.8, 8, 2, 1985),
                ('Trường Sa', 'TS-001', 'one_way', 'good', 4.1, 8, 2, 2010),
                ('Hoàng Diệu', 'HD-001', 'two_way', 'normal', 1.9, 7, 2, 1990),
            ]
            for name, code, direction, status, length, width, lanes, year in roads_data:
                if not Road.objects.filter(code=code).exists():
                    Road.objects.create(
                        name=name, code=code, direction=direction, status=status,
                        length_km=length, width_m=width, lanes=lanes, built_year=year,
                        zone=zone, created_by=admin,
                        latitude=16.047 + (hash(code) % 100) / 1000,
                        longitude=108.206 + (hash(code[:3]) % 100) / 1000,
                    )
                    self.stdout.write(f'  ✓ Road: {name}')
        except Exception as e:
            self.stdout.write(f'  ! Roads skipped: {e}')

        # Create sample maintenance requests
        try:
            from maintenance.models import MaintenanceRequest
            citizen = User.objects.get(username='citizen01')
            staff = User.objects.get(username='staff01')
            roads = list(__import__('infrastructure.models', fromlist=['Road']).Road.objects.all()[:3])
            requests_data = [
                ('Ổ gà lớn trên đường Lê Duẩn', 'pothole', 'high', 'completed', roads[0] if roads else None),
                ('Đèn giao thông ngã tư Điện Biên Phủ hỏng', 'traffic_light', 'urgent', 'in_progress', None),
                ('Vỉa hè bị hư hỏng nghiêm trọng', 'road_damage', 'medium', 'pending', roads[1] if len(roads)>1 else None),
                ('Cống thoát nước bị tắc nghẽn', 'drainage', 'high', 'received', None),
                ('Biển báo giao thông bị ngã', 'sign', 'medium', 'assigned', None),
            ]
            from django.utils import timezone
            from datetime import timedelta
            for i, (title, itype, priority, status, road) in enumerate(requests_data):
                if not MaintenanceRequest.objects.filter(title=title).exists():
                    req = MaintenanceRequest.objects.create(
                        title=title, description=f'Mô tả chi tiết cho: {title}',
                        incident_type=itype, priority=priority, status=status,
                        reported_by=citizen, road=road,
                        address=f'Địa chỉ mẫu {i+1}, Đà Nẵng',
                        latitude=16.047 + i*0.01, longitude=108.206 + i*0.01,
                        created_at=timezone.now() - timedelta(days=i*3)
                    )
                    if status in ('assigned', 'in_progress', 'completed'):
                        req.assigned_to = staff
                        req.assigned_at = timezone.now() - timedelta(days=i*2)
                    if status == 'completed':
                        req.completed_at = timezone.now() - timedelta(days=i)
                        req.actual_cost = (i+1) * 5000000
                        req.citizen_rating = 4
                    req.save()
                    self.stdout.write(f'  ✓ Request: {title}')
        except Exception as e:
            self.stdout.write(f'  ! Requests skipped: {e}')

        # Create sample flood alert
        try:
            from flood.models import FloodAlert
            admin = User.objects.get(username='admin')
            if not FloodAlert.objects.exists():
                FloodAlert.objects.create(
                    title='Cảnh báo ngập lụt khu vực Hải Châu',
                    description='Mực nước tăng cao do mưa lớn kéo dài.',
                    level='2', area_type='district', area_name='Hải Châu',
                    water_level_cm=45, is_active=False,
                    safe_routes='Sử dụng đường Lê Duẩn thay thế',
                    created_by=admin, latitude=16.068, longitude=108.212
                )
                self.stdout.write('  ✓ Flood alert sample created')
        except Exception as e:
            self.stdout.write(f'  ! Flood skipped: {e}')

        self.stdout.write(self.style.SUCCESS('\n✅ Dữ liệu demo đã được tạo thành công!'))
        self.stdout.write('\nTài khoản demo:')
        self.stdout.write('  admin / Demo@2024  (Quản trị viên)')
        self.stdout.write('  manager01 / Demo@2024  (Quản lý)')
        self.stdout.write('  staff01 / Demo@2024  (Cán bộ kỹ thuật)')
        self.stdout.write('  citizen01 / Demo@2024  (Người dân)')
