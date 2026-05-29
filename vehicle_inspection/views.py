from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.db.models import OuterRef, Subquery, Max, F, Q
from django.http import HttpResponse, HttpResponseForbidden

from .models import Vehicle, Inspection, InspectionCenter
from .forms import VehicleForm, ScheduleInspectionForm, InspectionResultForm, PaymentForm


class VehicleListView(LoginRequiredMixin, ListView):
    """
    Danh sách phương tiện của chủ xe
    - ORM: Dùng Subquery + OuterRef tránh N+1 query
    - Logic: Chỉ xem xe của user hiện tại
    """
    template_name = 'vehicle_inspection/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20

    def get_queryset(self):
        latest_inspection_qs = Inspection.objects.filter(
            vehicle=OuterRef('pk')
        ).order_by('-scheduled_date')

        latest_expiry_qs = Inspection.objects.filter(
            vehicle=OuterRef('pk'),
            valid_until__isnull=False,
            status='passed'
        ).order_by('-valid_until')

        latest_center_qs = Inspection.objects.filter(
            vehicle=OuterRef('pk')
        ).order_by('-scheduled_date')

        queryset = Vehicle.objects.filter(
            owner=self.request.user,
            is_active=True
        ).annotate(
            latest_scheduled_date=Subquery(
                latest_inspection_qs.values('scheduled_date')[:1]
            ),
            latest_center_name=Subquery(
                latest_center_qs.values('center__name')[:1]
            ),
            # ĐÃ SỬA LỖI Ở ĐÂY: Đổi tên biến tránh xung đột với @property
            inspection_expiry=Subquery(
                latest_expiry_qs.values('valid_until')[:1]
            ),
        ).select_related().order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        # Tính toán trạng thái hạn đăng kiểm cho mỗi xe
        for vehicle in context['vehicles']:
            vehicle.expiry_date = getattr(vehicle, "inspection_expiry", None)
            vehicle.expiry_status = vehicle.get_expiry_status()

        context['page_title'] = 'Quản lý phương tiện'
        context['page_description'] = 'Theo dõi hạn đăng kiểm phương tiện'
        return context


class VehicleCreateView(LoginRequiredMixin, CreateView):
    """
    Tạo phương tiện mới
    - Tự động gán owner = request.user
    - Redirect về danh sách sau khi tạo
    """
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicle_inspection/vehicle_form.html'
    success_url = reverse_lazy('vehicle_inspection:vehicle_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Đã thêm phương tiện "{form.instance.license_plate}" thành công.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Thêm phương tiện mới'
        context['action'] = 'create'
        return context


class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Chỉnh sửa thông tin phương tiện
    - Chỉ chủ xe mới được chỉnh sửa
    """
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicle_inspection/vehicle_form.html'
    success_url = reverse_lazy('vehicle_inspection:vehicle_list')

    def test_func(self):
        """Kiểm tra quyền: chỉ chủ xe được chỉnh sửa"""
        vehicle = self.get_object()
        return vehicle.owner == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Đã cập nhật phương tiện "{form.instance.license_plate}" thành công.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Chỉnh sửa phương tiện'
        context['action'] = 'update'
        return context

    def handle_no_permission(self):
        messages.error(self.request, 'Bạn không có quyền chỉnh sửa phương tiện này.')
        return redirect('vehicle_inspection:vehicle_list')


class InspectionListView(LoginRequiredMixin, ListView):
    """
    Danh sách lịch đăng kiểm
    - Chủ xe: Chỉ xem lịch của xe mình
    - Cán bộ: Xem tất cả lịch
    - Filter theo trạng thái
    """
    template_name = 'vehicle_inspection/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 20

    def get_queryset(self):
        """Optimized query với select_related"""
        queryset = Inspection.objects.select_related(
            'vehicle',
            'vehicle__owner',
            'center',
            'inspector'
        ).order_by('-scheduled_date')

        # Chủ xe: Chỉ xem lịch của xe mình
        if not self.request.user.is_staff:
            queryset = queryset.filter(vehicle__owner=self.request.user)

        # Filter theo trạng thái nếu có
        status_filter = self.request.GET.get('status', '').strip()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Thêm thông tin badge cho mỗi lịch
        for inspection in context['inspections']:
            inspection.status_badge_class = inspection.get_status_badge_class()
            inspection.status_label = inspection.get_status_label()
            inspection.can_cancel = (
                inspection.status == 'pending' and
                inspection.vehicle.owner == self.request.user
            )
            inspection.can_update = (
                self.request.user.is_staff and
                inspection.status in ['pending', 'in_progress']
            )
            inspection.can_pay = (
                not self.request.user.is_staff and
                inspection.vehicle.owner == self.request.user and
                inspection.fee and
                not inspection.is_fee_paid
            )

        context['status_choices'] = Inspection.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['page_title'] = 'Danh sách lịch đăng kiểm'
        context['is_staff'] = self.request.user.is_staff
        return context


class ScheduleInspectionView(LoginRequiredMixin, CreateView):
    """
    Đặt lịch đăng kiểm (cho chủ xe)
    - Chỉ chọn Xe, Trung tâm, Ngày hẹn
    - KHÔNG hiển thị field fee
    - Tự động set status = 'pending'
    """
    model = Inspection
    form_class = ScheduleInspectionForm
    template_name = 'vehicle_inspection/schedule_form.html'
    success_url = reverse_lazy('vehicle_inspection:inspection_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Kiểm tra quyền và set inspector"""
        selected_vehicle = form.cleaned_data['vehicle']

        # Kiểm tra xe thuộc về user
        if selected_vehicle.owner != self.request.user:
            messages.error(
                self.request,
                'Bạn không thể đặt lịch cho phương tiện không thuộc sở hữu của mình.'
            )
            return self.form_invalid(form)

        form.instance.vehicle = selected_vehicle
        form.instance.status = 'pending'
        form.instance.fee = 0  # Cán bộ sẽ nhập phí sau

        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Đã đặt lịch đăng kiểm cho {selected_vehicle.license_plate} thành công.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Đặt lịch đăng kiểm'
        context['schedule_min_date'] = timezone.localdate().isoformat()
        context['instructions'] = [
            'Chọn phương tiện của bạn',
            'Chọn trung tâm đăng kiểm',
            'Chọn ngày hẹn (tối thiểu hôm nay)',
            'Nhấn "Xác nhận đặt lịch"'
        ]
        return context


class InspectionDetailView(LoginRequiredMixin, DetailView):
    """
    Chi tiết lịch đăng kiểm
    - Chủ xe: Xem thông tin cơ bản
    - Cán bộ: Xem đầy đủ, có thể cập nhật kết quả
    """
    model = Inspection
    template_name = 'vehicle_inspection/inspection_detail.html'
    context_object_name = 'inspection'

    def get_queryset(self):
        queryset = Inspection.objects.select_related(
            'vehicle',
            'vehicle__owner',
            'center',
            'inspector'
        )

        # Chủ xe: Chỉ xem lịch của xe mình
        if not self.request.user.is_staff:
            queryset = queryset.filter(vehicle__owner=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inspection = self.get_object()

        context['is_staff'] = self.request.user.is_staff
        context['can_update'] = (
            self.request.user.is_staff and
            inspection.status in ['pending', 'in_progress']
        )
        context['can_cancel'] = (
            not self.request.user.is_staff and
            inspection.vehicle.owner == self.request.user and
            inspection.status == 'pending'
        )
        context['can_pay'] = (
            not self.request.user.is_staff and
            inspection.vehicle.owner == self.request.user and
            inspection.fee and
            not inspection.is_fee_paid
        )

        # Status badge
        inspection.status_badge_class = inspection.get_status_badge_class()
        inspection.status_label = inspection.get_status_label()

        context['page_title'] = f'Lịch đăng kiểm {inspection.vehicle.license_plate}'
        return context


class InspectionResultView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Cập nhật kết quả đăng kiểm (cho cán bộ)
    - Nhập lỗi, kết quả, phí, số giấy chứng nhận
    - Chỉ cán bộ mới được cập nhật
    """
    model = Inspection
    form_class = InspectionResultForm
    template_name = 'vehicle_inspection/inspection_result_form.html'
    success_url = reverse_lazy('vehicle_inspection:inspection_list')

    def test_func(self):
        """Chỉ cán bộ mới được cập nhật"""
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Cập nhật kết quả đăng kiểm {self.get_object().vehicle.license_plate}'
        context['inspection'] = self.get_object()
        return context

    def form_valid(self, form):
        form.instance.inspector = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Đã cập nhật kết quả đăng kiểm thành công.'
        )
        return response

    def handle_no_permission(self):
        messages.error(self.request, 'Chỉ cán bộ mới có quyền cập nhật kết quả.')
        return redirect('vehicle_inspection:inspection_list')


@login_required
def cancel_inspection(request, pk):
    """
    Hủy lịch đăng kiểm (cho chủ xe)
    - Chỉ hủy được lịch ở trạng thái pending
    """
    inspection = get_object_or_404(
        Inspection,
        pk=pk,
        vehicle__owner=request.user,
        status='pending'
    )

    if request.method == 'POST':
        inspection.status = 'cancelled'
        inspection.save()
        messages.success(request, 'Đã hủy lịch đăng kiểm.')
        return redirect('vehicle_inspection:inspection_list')

    context = {
        'inspection': inspection,
        'page_title': 'Xác nhận hủy lịch',
    }
    return render(request, 'vehicle_inspection/cancel_confirm.html', context)


@login_required
def pay_inspection_fee(request, pk):
    """
    Thanh toán phí đăng kiểm (cho chủ xe)
    - Chỉ thanh toán khi cán bộ đã nhập phí
    """
    inspection = get_object_or_404(
        Inspection,
        pk=pk,
        vehicle__owner=request.user
    )

    # Kiểm tra điều kiện thanh toán
    if not inspection.fee or inspection.fee == 0:
        messages.error(request, 'Cán bộ chưa nhập phí đăng kiểm.')
        return redirect('vehicle_inspection:inspection_detail', pk=pk)

    if inspection.is_fee_paid:
        messages.warning(request, 'Phí đã được thanh toán rồi.')
        return redirect('vehicle_inspection:inspection_detail', pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            inspection.is_fee_paid = True
            inspection.save()
            messages.success(
                request,
                f'Đã xác nhận thanh toán phí {inspection.fee:,.0f} VNĐ.'
            )
            return redirect('vehicle_inspection:inspection_list')
    else:
        form = PaymentForm()

    context = {
        'inspection': inspection,
        'form': form,
        'page_title': 'Thanh toán phí đăng kiểm',
    }
    return render(request, 'vehicle_inspection/payment_confirm.html', context)


def _pdf_text(value):
    import unicodedata

    text = str(value or "")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


@login_required
def inspection_certificate_pdf(request, pk):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas as rl_canvas

    inspection = get_object_or_404(
        Inspection.objects.select_related("vehicle", "vehicle__owner", "center", "inspector"),
        pk=pk,
    )
    if not request.user.is_staff and inspection.vehicle.owner_id != request.user.id:
        return HttpResponseForbidden("Ban khong co quyen in chung nhan nay.")
    if inspection.status != "passed":
        return HttpResponseForbidden("Chi co the in chung nhan cho ket qua dat.")

    filename = f"chung_nhan_dang_kiem_{inspection.vehicle.license_plate}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    p = rl_canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFillColor(colors.HexColor("#198754"))
    p.rect(0, height - 3.2 * cm, width, 3.2 * cm, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 1.45 * cm, "GIAY CHUNG NHAN DANG KIEM")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2, height - 2.25 * cm, "He thong quan ly dang kiem phuong tien Da Nang")

    y = height - 4.2 * cm
    rows = [
        ("So chung nhan", inspection.certificate_number or f"DK-{inspection.pk}"),
        ("Bien so", inspection.vehicle.license_plate),
        ("Loai xe", inspection.vehicle.get_vehicle_type_display()),
        ("Hang/Model", f"{inspection.vehicle.brand} {inspection.vehicle.model}".strip()),
        ("Chu xe", inspection.vehicle.owner.get_full_name() or inspection.vehicle.owner.username),
        ("Trung tam", inspection.center.name if inspection.center else ""),
        ("Ngay kiem dinh", inspection.scheduled_date.strftime("%d/%m/%Y")),
        ("Hieu luc den", inspection.valid_until.strftime("%d/%m/%Y") if inspection.valid_until else ""),
        ("Can bo kiem tra", inspection.inspector.get_full_name() if inspection.inspector else ""),
        ("Phi", f"{inspection.fee:,.0f} VND" if inspection.fee else "0 VND"),
    ]

    p.setFillColor(colors.black)
    for label, value in rows:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(2 * cm, y, f"{label}:")
        p.setFont("Helvetica", 10)
        p.drawString(6 * cm, y, _pdf_text(value)[:95])
        y -= 0.65 * cm

    y -= 0.5 * cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2 * cm, y, "Ghi chu ky thuat")
    y -= 0.6 * cm
    p.setFont("Helvetica", 10)
    notes = _pdf_text(inspection.technical_notes or "Phuong tien dat yeu cau dang kiem.")
    for line in [notes[i:i + 100] for i in range(0, len(notes), 100)][:5]:
        p.drawString(2 * cm, y, line)
        y -= 0.5 * cm

    y = max(y - 1 * cm, 4 * cm)
    p.line(11 * cm, y, 18 * cm, y)
    p.setFont("Helvetica", 10)
    p.drawString(12.2 * cm, y - 0.5 * cm, "Can bo dang kiem")

    p.showPage()
    p.save()
    return response
