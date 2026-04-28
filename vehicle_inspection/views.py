from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Subquery
from django.urls import reverse_lazy

from .models import Vehicle, Inspection, InspectionCenter
from accounts.decorators import staff_required
from .forms import VehicleForm, ScheduleForm


class VehicleListView(LoginRequiredMixin, ListView):
    template_name = "vehicle_inspection/vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        latest_inspection_qs = Inspection.objects.filter(vehicle=OuterRef("pk")).order_by("-scheduled_date")
        latest_expiry_qs = (
            Inspection.objects.filter(vehicle=OuterRef("pk"), valid_until__isnull=False)
            .order_by("-valid_until")
            .values("valid_until")
        )
        return (
            Vehicle.objects.filter(owner=self.request.user, is_active=True)
            .annotate(
                latest_schedule_date=Subquery(latest_inspection_qs.values("scheduled_date")[:1]),
                latest_center_name=Subquery(latest_inspection_qs.values("center__name")[:1]),
                inspection_expiry=Subquery(latest_expiry_qs[:1]),
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        for vehicle in context["vehicles"]:
            expiry_date = getattr(vehicle, "inspection_expiry", None)
            if expiry_date:
                days_left = (expiry_date - today).days
                vehicle.days_left = days_left
                if days_left < 0:
                    vehicle.expiry_badge_class = "text-bg-danger"
                    vehicle.expiry_badge_text = "Het han"
                    vehicle.expiry_is_alert = True
                    vehicle.expiry_note = f"Da qua han {abs(days_left)} ngay"
                    vehicle.expiry_note_class = "text-danger"
                elif days_left <= 30:
                    vehicle.expiry_badge_class = "text-bg-danger"
                    vehicle.expiry_badge_text = "Sap het han"
                    vehicle.expiry_is_alert = True
                    vehicle.expiry_note = f"Con {days_left} ngay"
                    vehicle.expiry_note_class = "text-muted"
                else:
                    vehicle.expiry_badge_class = "text-bg-success"
                    vehicle.expiry_badge_text = "Hop le"
                    vehicle.expiry_is_alert = False
                    vehicle.expiry_note = f"Con {days_left} ngay"
                    vehicle.expiry_note_class = "text-muted"
            else:
                vehicle.days_left = None
                vehicle.expiry_badge_class = "text-bg-secondary"
                vehicle.expiry_badge_text = "Chua co du lieu"
                vehicle.expiry_is_alert = False
                vehicle.expiry_note = ""
                vehicle.expiry_note_class = "text-muted"
        context["page_title"] = "Quan ly phuong tien"
        return context


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicle_inspection/vehicle_form.html"
    success_url = reverse_lazy("vehicle_inspection:vehicle_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Da them phuong tien thanh cong.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Them phuong tien"
        return context


class InspectionListView(LoginRequiredMixin, ListView):
    template_name = "vehicle_inspection/inspection_list.html"
    context_object_name = "inspections"
    paginate_by = 20

    def get_queryset(self):
        queryset = Inspection.objects.select_related("vehicle", "center")
        if not self.request.user.is_staff_member:
            queryset = queryset.filter(vehicle__owner=self.request.user)
        selected_status = self.request.GET.get("status", "").strip()
        if selected_status:
            queryset = queryset.filter(status=selected_status)
        return queryset.order_by("-scheduled_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for inspection in context["inspections"]:
            if inspection.status == "pending":
                inspection.workflow_label = "Cho xac nhan"
                inspection.workflow_badge = "text-bg-warning"
            elif inspection.status in ["in_progress", "needs_repair"]:
                inspection.workflow_label = "Da duyet"
                inspection.workflow_badge = "text-bg-primary"
            else:
                inspection.workflow_label = "Hoan thanh"
                inspection.workflow_badge = "text-bg-success"
            inspection.can_cancel = inspection.status == "pending" and not self.request.user.is_staff_member
        context["status_choices"] = Inspection.STATUS_CHOICES
        context["selected_status"] = self.request.GET.get("status", "")
        context["page_title"] = "Danh sach lich dang kiem"
        return context


class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Inspection
    form_class = ScheduleForm
    template_name = "vehicle_inspection/schedule_form.html"
    success_url = reverse_lazy("vehicle_inspection:inspection_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["vehicle"].queryset = Vehicle.objects.filter(owner=self.request.user, is_active=True)
        form.fields["center"].queryset = InspectionCenter.objects.filter(is_active=True)
        return form

    def form_valid(self, form):
        selected_vehicle = form.cleaned_data["vehicle"]
        if selected_vehicle.owner_id != self.request.user.id:
            messages.error(self.request, "Ban khong the dat lich cho phuong tien khong thuoc so huu cua minh.")
            return self.form_invalid(form)
        form.instance.vehicle = selected_vehicle
        form.instance.status = "pending"
        response = super().form_valid(form)
        messages.success(self.request, "Dat lich dang kiem thanh cong.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Dat lich dang kiem"
        context["schedule_min_date"] = timezone.localdate().isoformat()
        return context

@login_required
def vehicle_list(request):
    return VehicleListView.as_view()(request)

@login_required
def vehicle_create(request):
    return VehicleCreateView.as_view()(request)

@login_required
def inspection_list(request):
    return InspectionListView.as_view()(request)

@login_required
def schedule_inspection(request):
    return ScheduleCreateView.as_view()(request)

@login_required
def cancel_inspection(request, pk):
    insp = get_object_or_404(Inspection, pk=pk, vehicle__owner=request.user)
    if insp.status == 'pending':
        insp.status = 'cancelled'
        insp.save()
        messages.success(request,'Đã hủy lịch đăng kiểm.')
    return redirect('vehicle_inspection:inspection_list')

@login_required
@staff_required
def update_inspection(request, pk):
    insp = get_object_or_404(Inspection, pk=pk)
    if request.method=='POST':
        insp.status = request.POST.get('status', insp.status)
        insp.technical_notes = request.POST.get('technical_notes','')
        insp.defects = request.POST.get('defects','')
        insp.repair_required = request.POST.get('repair_required','')
        if request.POST.get('certificate_number'):
            insp.certificate_number = request.POST.get('certificate_number')
        insp.inspector = request.user
        insp.save()
        messages.success(request,'Đã cập nhật kết quả đăng kiểm.')
    return redirect('vehicle_inspection:inspection_list')

@login_required
def pay_fee(request, pk):
    insp = get_object_or_404(Inspection, pk=pk, vehicle__owner=request.user)
    insp.is_fee_paid = True
    insp.save()
    messages.success(request,'Đã xác nhận thanh toán.')
    return redirect('vehicle_inspection:inspection_list')
