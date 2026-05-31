from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .models import ConstructionPermit, PermitDocument
from .forms import PermitForm

PUBLIC_STATUSES = [
    "submitted",
    "received",
    "reviewing",
    "additional_required",
    "approved",
    "rejected",
    "construction",
    "completed",
    "suspended",
]

TIMELINE_STEPS = [
    ("submitted", "Nop ho so"),
    ("received", "Tiep nhan"),
    ("reviewing", "Dang duyet"),
    ("approved", "Co ket qua"),
]

TIMELINE_STATUS_INDEX = {
    "draft": -1,
    "submitted": 0,
    "received": 1,
    "additional_required": 1,
    "reviewing": 2,
    "approved": 3,
    "rejected": 3,
    "construction": 3,
    "completed": 3,
    "suspended": 3,
}


class PermitListView(ListView):
    model = ConstructionPermit
    template_name = "permits/list.html"
    context_object_name = "permits"
    paginate_by = 12

    def get_queryset(self):
        queryset = ConstructionPermit.objects.select_related("applicant").order_by("-created_at")
        keyword = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        date_from_raw = self.request.GET.get("date_from", "").strip()
        date_to_raw = self.request.GET.get("date_to", "").strip()
        user = self.request.user
        is_staff_user = user.is_authenticated and (
            user.is_superuser or getattr(user, "is_staff_member", False) or user.is_staff
        )

        if is_staff_user:
            queryset = queryset.exclude(status="draft")
        elif user.is_authenticated:
            queryset = queryset.filter(applicant=user)
        else:
            queryset = queryset.filter(status__in=PUBLIC_STATUSES)

        if keyword:
            queryset = queryset.filter(
                Q(permit_number__icontains=keyword)
                | Q(title__icontains=keyword)
                | Q(applicant__username__icontains=keyword)
            )

        if status:
            queryset = queryset.filter(status=status)

        date_from = parse_date(date_from_raw) if date_from_raw else None
        date_to = parse_date(date_to_raw) if date_to_raw else None
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Tra cuu va theo doi cap phep xay dung"
        context["search_query"] = self.request.GET.get("q", "")
        context["status_choices"] = ConstructionPermit.STATUS_CHOICES
        context["selected_status"] = self.request.GET.get("status", "")
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["current_filters"] = query_params.urlencode()
        context["status_classes"] = {
            "draft": "text-bg-secondary",
            "submitted": "text-bg-info",
            "reviewing": "text-bg-warning",
            "approved": "text-bg-success",
            "rejected": "text-bg-danger",
            "received": "text-bg-primary",
            "additional_required": "text-bg-warning",
            "construction": "text-bg-primary",
            "completed": "text-bg-success",
            "suspended": "text-bg-dark",
        }
        return context


class PermitDetailView(DetailView):
    model = ConstructionPermit
    template_name = "permits/detail.html"
    context_object_name = "permit"

    def get_queryset(self):
        queryset = ConstructionPermit.objects.select_related(
            "applicant",
            "assigned_reviewer",
            "approved_by",
        )
        user = self.request.user
        is_staff_user = user.is_authenticated and (
            user.is_superuser or getattr(user, "is_staff_member", False) or user.is_staff
        )
        if is_staff_user:
            return queryset.exclude(status="draft")
        if user.is_authenticated:
            return queryset.filter(Q(applicant=user) | Q(status__in=PUBLIC_STATUSES))
        return queryset.filter(status__in=PUBLIC_STATUSES)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_status = self.object.status
        active_idx = TIMELINE_STATUS_INDEX.get(current_status, -1)
        context["timeline"] = [
            {"key": key, "label": label, "is_active": idx <= active_idx}
            for idx, (key, label) in enumerate(TIMELINE_STEPS)
        ]
        context["current_status"] = current_status
        context["page_title"] = "Chi tiet ho so cap phep xay dung"
        context["status_classes"] = {
            "draft": "text-bg-secondary",
            "submitted": "text-bg-info",
            "reviewing": "text-bg-warning",
            "approved": "text-bg-success",
            "rejected": "text-bg-danger",
            "received": "text-bg-primary",
            "additional_required": "text-bg-warning",
            "construction": "text-bg-primary",
            "completed": "text-bg-success",
            "suspended": "text-bg-dark",
        }
        return context

class PermitCreateView(LoginRequiredMixin, CreateView):
    model = ConstructionPermit
    form_class = PermitForm
    template_name = "permits/permit_form.html"

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        action = self.request.POST.get("action", "submit")
        form.instance.status = "draft" if action == "draft" else "submitted"
        response = super().form_valid(form)
        for uploaded in self.request.FILES.getlist("documents"):
            PermitDocument.objects.create(
                permit=self.object,
                name=uploaded.name,
                file=uploaded,
                uploaded_by=self.request.user,
            )
        if form.instance.status == "submitted":
            messages.success(self.request, "Da nop ho so thanh cong. Ho so da chuyen sang trang thai Da nop.")
        else:
            messages.success(self.request, "Da luu ho so o trang thai Ban nhap.")
        return response

    def get_success_url(self):
        return reverse("permits:detail", kwargs={"pk": self.object.pk})

@login_required
@require_POST
def process_permit(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)

    if not getattr(request.user, "is_manager", False):
        messages.error(request, "Ban khong co quyen xu ly ho so nay.")
        return redirect("permits:detail", pk=pk)

    action = request.POST.get("action", "").strip()

    if action == "receive":
        permit.status = "reviewing"
        if permit.assigned_reviewer_id is None:
            permit.assigned_reviewer = request.user
        permit.save(update_fields=["status", "assigned_reviewer", "updated_at"])
        messages.success(request, "Da tiep nhan ho so va chuyen sang trang thai Dang xet duyet.")
    elif action == "approve":
        permit.status = "approved"
        permit.approved_by = request.user
        permit.issued_at = timezone.now()
        if not permit.permit_number:
            permit.permit_number = f"GP-{timezone.now().year}-{permit.pk:04d}"
        permit.save(update_fields=["status", "approved_by", "issued_at", "permit_number", "updated_at"])
        messages.success(request, "Da phe duyet ho so thanh cong.")
    elif action == "reject":
        permit.status = "rejected"
        permit.save(update_fields=["status", "updated_at"])
        messages.success(request, "Da tu choi ho so.")
    else:
        messages.error(request, "Hanh dong khong hop le.")

    return redirect("permits:detail", pk=pk)


@login_required
def permit_detail(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)
    if request.user.role=='citizen' and permit.applicant!=request.user:
        messages.error(request,'Bạn không có quyền xem hồ sơ này.')
        return redirect('permits:list')
    return render(request,'permits/detail.html',{'permit':permit,'page_title':permit.title})

@login_required
def permit_submit(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk, applicant=request.user)
    if permit.status == 'draft':
        permit.status = 'submitted'
        permit.save()
        messages.success(request,'Đã nộp hồ sơ thành công.')
    return redirect('permits:detail', pk=pk)

@login_required
def permit_stats(request):
    from django.db.models import Count
    stats = {'by_status': list(ConstructionPermit.objects.values('status').annotate(count=Count('id')))}
    return render(request,'permits/stats.html',{'stats':stats,'page_title':'Thống kê giấy phép'})
