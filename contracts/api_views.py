from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Contract, Tender, Contractor
from .serializers import ContractSerializer, TenderSerializer, ContractorSerializer


class ContractListAPIView(generics.ListCreateAPIView):
    queryset = Contract.objects.select_related('contractor', 'created_by').all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['contract_number', 'title']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContractDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]


class TenderListAPIView(generics.ListCreateAPIView):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContractorListAPIView(generics.ListCreateAPIView):
    queryset = Contractor.objects.filter(is_active=True)
    serializer_class = ContractorSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def contract_stats_api(request):
    from django.db.models import Count, Sum
    stats = {
        'by_status': list(Contract.objects.values('status').annotate(count=Count('id'))),
        'total_value': float(Contract.objects.aggregate(t=Sum('value'))['t'] or 0),
        'active_contracts': Contract.objects.filter(status='active').count(),
        'open_tenders': Tender.objects.filter(status='open').count(),
    }
    return Response(stats)
