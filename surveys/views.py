from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Avg, Count, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormMixin

from .forms import SurveyCreateForm, SurveyResponseForm
from .models import Survey, SurveyResponse


class StaffRequiredMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class SurveyCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Survey
    form_class = SurveyCreateForm
    template_name = "surveys/survey_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Đã tạo khảo sát mới.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("surveys:list")


class SurveyListView(LoginRequiredMixin, ListView):
    model = Survey
    template_name = "surveys/list.html"
    context_object_name = "surveys"

    def get_queryset(self):
        today = timezone.localdate()
        queryset = Survey.objects.select_related("created_by").annotate(
            response_count=Count("responses", distinct=True),
        )
        if self.request.user.is_staff:
            return queryset.order_by("-created_at")
        return queryset.filter(is_active=True).filter(Q(deadline__isnull=True) | Q(deadline__gte=today)).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_ids = [survey.id for survey in context["surveys"]]
        responded_ids = set()
        if self.request.user.is_authenticated and survey_ids:
            responded_ids = set(
                SurveyResponse.objects.filter(
                    survey_id__in=survey_ids,
                    respondent=self.request.user,
                ).values_list("survey_id", flat=True)
            )
        context["responded_ids"] = responded_ids
        context["page_title"] = "Quản lý khảo sát" if self.request.user.is_staff else "Khảo sát ý kiến người dân"
        context["today"] = timezone.localdate()
        return context


class SurveyDetailRespondView(LoginRequiredMixin, FormMixin, DetailView):
    model = Survey
    form_class = SurveyResponseForm
    template_name = "surveys/respond.html"
    context_object_name = "survey"

    def get_queryset(self):
        return Survey.objects.select_related("created_by")

    def _survey_is_open(self):
        today = timezone.localdate()
        return self.object.is_active and (self.object.deadline is None or self.object.deadline >= today)

    def _user_has_responded(self):
        return SurveyResponse.objects.filter(survey=self.object, respondent=self.request.user).exists()

    def _build_survey_stats(self):
        rating_qs = self.object.responses.filter(satisfaction_score__isnull=False)
        total_votes = rating_qs.count()
        average_score = rating_qs.aggregate(avg=Avg("satisfaction_score"))["avg"] or 0
        breakdown_map = {
            item["satisfaction_score"]: item["count"]
            for item in rating_qs.values("satisfaction_score").annotate(count=Count("id"))
        }
        breakdown = []
        for rating in range(5, 0, -1):
            count = breakdown_map.get(rating, 0)
            percentage = (count * 100 / total_votes) if total_votes else 0
            breakdown.append({
                "rating": rating,
                "count": count,
                "percentage": f"{percentage:.1f}",
            })
        return {
            "total_votes": total_votes,
            "average_score": average_score,
            "average_score_display": f"{average_score:.1f}",
            "breakdown": breakdown,
        }

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self._survey_is_open() and not self._user_has_responded():
            if request.user.is_staff:
                return super().dispatch(request, *args, **kwargs)
            messages.warning(request, "Khảo sát này đã đóng.")
            return redirect("surveys:list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_has_responded = self._user_has_responded()
        show_stats = user_has_responded or (not self._survey_is_open() and self.request.user.is_staff)
        context["survey"] = self.object
        context["page_title"] = self.object.title
        context["survey_is_open"] = self._survey_is_open()
        context["user_has_responded"] = user_has_responded
        context["response_count"] = self.object.responses.count()
        context["show_stats"] = show_stats
        if show_stats:
            context.pop("form", None)
            context["survey_stats"] = self._build_survey_stats()
        else:
            context["form"] = kwargs.get("form") or self.get_form()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self._survey_is_open():
            if request.user.is_staff:
                messages.info(request, "Khảo sát đã đóng, bạn chỉ có thể xem kết quả.")
                return redirect(self.get_success_url())
            messages.warning(request, "Khảo sát này đã đóng.")
            return redirect("surveys:list")
        if self._user_has_responded():
            messages.warning(request, "Bạn đã tham gia khảo sát này rồi.")
            return redirect(self.get_success_url())
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        already_responded = SurveyResponse.objects.filter(survey=self.object, respondent=self.request.user).exists()
        if already_responded:
            messages.warning(self.request, "Bạn đã tham gia khảo sát này rồi.")
            return redirect(self.get_success_url())

        form.instance.survey = self.object
        form.instance.respondent = self.request.user
        form.save()
        messages.success(self.request, "Cảm ơn bạn đã tham gia khảo sát!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("surveys:respond", kwargs={"pk": self.object.pk})
