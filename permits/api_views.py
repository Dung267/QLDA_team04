from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count
from .models import ConstructionPermit
from .serializers import ConstructionPermitSerializer


class PermitListAPIView(generics.ListCreateAPIView):
    serializer_class = ConstructionPermitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'permit_number', 'location']

    def get_queryset(self):
        qs = ConstructionPermit.objects.select_related('applicant')
        if self.request.user.role == 'citizen':
            qs = qs.filter(applicant=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class PermitDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ConstructionPermit.objects.all()
    serializer_class = ConstructionPermitSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_permit_api(request, pk):
    try:
        permit = ConstructionPermit.objects.get(pk=pk, applicant=request.user)
        if permit.status == 'draft':
            permit.status = 'submitted'
            permit.save()
            return Response({'success': True, 'status': permit.status})
        return Response({'error': 'Can only submit draft permits'}, status=400)
    except ConstructionPermit.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def permit_stats_api(request):
    stats = {
        'by_status': list(ConstructionPermit.objects.values('status').annotate(count=Count('id'))),
        'total': ConstructionPermit.objects.count(),
    }
    return Response(stats)
