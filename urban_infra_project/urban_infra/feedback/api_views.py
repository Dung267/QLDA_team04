from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import SystemFeedback
from .serializers import SystemFeedbackSerializer


class FeedbackListAPIView(generics.ListCreateAPIView):
    serializer_class = SystemFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        qs = SystemFeedback.objects.filter(status__in=['new', 'reviewed', 'resolved'])
        rating = self.request.query_params.get('rating')
        if rating:
            qs = qs.filter(rating=rating)
        return qs

    def perform_create(self, serializer):
        is_anon = self.request.data.get('is_anonymous', False)
        serializer.save(
            author=None if is_anon else self.request.user,
            is_anonymous=is_anon,
        )


class FeedbackDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = SystemFeedback.objects.all()
    serializer_class = SystemFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_feedback_api(request, pk):
    try:
        fb = SystemFeedback.objects.get(pk=pk)
        fb.likes += 1
        fb.save(update_fields=['likes'])
        return Response({'likes': fb.likes})
    except SystemFeedback.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def feedback_stats_api(request):
    stats = {
        'total': SystemFeedback.objects.count(),
        'avg_rating': SystemFeedback.objects.aggregate(avg=Avg('rating'))['avg'],
        'by_rating': list(
            SystemFeedback.objects.values('rating').annotate(count=Count('id')).order_by('rating')),
        'by_status': list(
            SystemFeedback.objects.values('status').annotate(count=Count('id'))),
    }
    return Response(stats)
