from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Survey, SurveyResponse
from .serializers import SurveySerializer, SurveyResponseSerializer


class SurveyListAPIView(generics.ListAPIView):
    queryset = Survey.objects.filter(is_active=True)
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]


class SurveyDetailAPIView(generics.RetrieveAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]


class SurveyResponseCreateAPIView(generics.CreateAPIView):
    serializer_class = SurveyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(respondent=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def survey_stats_api(request, pk):
    try:
        survey = Survey.objects.get(pk=pk)
    except Survey.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    responses = survey.responses.all()
    stats = {
        'total_responses': responses.count(),
        'avg_satisfaction': responses.filter(
            satisfaction_score__isnull=False).aggregate(avg=Avg('satisfaction_score'))['avg'],
        'score_distribution': list(
            responses.values('satisfaction_score').annotate(count=Count('id')).order_by('satisfaction_score')),
    }
    return Response(stats)
