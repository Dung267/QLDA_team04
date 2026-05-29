from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Survey, SurveyResponse


User = get_user_model()


class SurveyViewsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="danang-manager", password="secret123", is_staff=True)
        self.citizen = User.objects.create_user(username="danang-citizen", password="secret123")
        self.today = timezone.localdate()
        self.open_survey = Survey.objects.create(
            title="Khảo sát sự hài lòng về Cầu Rồng",
            description="Góp ý cho tuyến cầu biểu tượng của thành phố.",
            is_active=True,
            deadline=self.today + timedelta(days=7),
            created_by=self.manager,
        )
        self.closed_survey = Survey.objects.create(
            title="Đánh giá tuyến phố đi bộ Bạch Đằng",
            description="Khảo sát đã hết hạn.",
            is_active=True,
            deadline=self.today - timedelta(days=1),
            created_by=self.manager,
        )

    def test_citizen_sees_only_open_surveys(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse("surveys:list"))
        self.assertContains(response, self.open_survey.title)
        self.assertNotContains(response, self.closed_survey.title)
        self.assertNotContains(response, "Tạo Khảo sát mới")

    def test_manager_sees_closed_surveys_and_create_button(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse("surveys:list"))
        self.assertContains(response, self.open_survey.title)
        self.assertContains(response, self.closed_survey.title)
        self.assertContains(response, "Tạo Khảo sát mới")

    def test_manager_can_create_survey_and_created_by_is_assigned(self):
        self.client.force_login(self.manager)
        payload = {
            "title": "Khảo sát quy hoạch tuyến ven sông Hàn",
            "description": "Lấy ý kiến người dân về hành lang ven sông và cảnh quan đô thị.",
            "deadline": (self.today + timedelta(days=14)).isoformat(),
            "is_active": True,
        }
        response = self.client.post(reverse("surveys:create"), payload, follow=True)
        self.assertRedirects(response, reverse("surveys:list"))
        survey = Survey.objects.get(title="Khảo sát quy hoạch tuyến ven sông Hàn")
        self.assertEqual(survey.created_by, self.manager)
        create_messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("Đã tạo" in message for message in create_messages))

    def test_citizen_cannot_access_create_view(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse("surveys:create"))
        self.assertEqual(response.status_code, 403)

    def test_detail_shows_form_until_user_votes(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse("surveys:respond", args=[self.open_survey.pk]))
        self.assertContains(response, "Gửi phản hồi")
        self.assertContains(response, "Chưa chọn đánh giá")
        self.assertNotContains(response, "Kết quả khảo sát")

    def test_duplicate_response_is_blocked_and_detail_shows_stats_after_vote(self):
        self.client.force_login(self.citizen)
        data = {
            "satisfaction_score": 5,
            "comments": "Rất hài lòng với hạ tầng quanh Cầu Rồng.",
        }

        first_response = self.client.post(reverse("surveys:respond", args=[self.open_survey.pk]), data, follow=True)
        self.assertEqual(SurveyResponse.objects.filter(survey=self.open_survey, respondent=self.citizen).count(), 1)
        first_messages = [str(message) for message in get_messages(first_response.wsgi_request)]
        self.assertTrue(any("Cảm ơn" in message for message in first_messages))
        self.assertContains(first_response, "Kết quả khảo sát")
        self.assertContains(first_response, "100.0%")

        second_response = self.client.post(reverse("surveys:respond", args=[self.open_survey.pk]), data, follow=True)
        self.assertEqual(SurveyResponse.objects.filter(survey=self.open_survey, respondent=self.citizen).count(), 1)
        second_messages = [str(message) for message in get_messages(second_response.wsgi_request)]
        self.assertTrue(any("đã tham gia" in message.lower() for message in second_messages))

    def test_manager_can_view_closed_survey_stats_but_citizen_is_redirected(self):
        SurveyResponse.objects.create(
            survey=self.closed_survey,
            respondent=self.manager,
            satisfaction_score=4,
            comments="Tốt",
        )

        self.client.force_login(self.manager)
        manager_response = self.client.get(reverse("surveys:respond", args=[self.closed_survey.pk]))
        self.assertContains(manager_response, "Kết quả khảo sát")
        self.assertNotContains(manager_response, "Gửi phản hồi")

        self.client.force_login(self.citizen)
        citizen_response = self.client.get(reverse("surveys:respond", args=[self.closed_survey.pk]), follow=True)
        self.assertRedirects(citizen_response, reverse("surveys:list"))
        self.assertContains(citizen_response, self.open_survey.title)

