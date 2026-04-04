from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Material, StockTransaction, Supplier
from .serializers import MaterialSerializer, StockTransactionSerializer, SupplierSerializer


class MaterialListAPIView(generics.ListAPIView):
    queryset = Material.objects.select_related('supplier').all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class MaterialDetailAPIView(generics.RetrieveAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]


class StockTransactionListAPIView(generics.ListCreateAPIView):
    queryset = StockTransaction.objects.select_related('material', 'performed_by').all()
    serializer_class = StockTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def low_stock_api(request):
    """Materials with stock <= min_stock"""
    from .serializers import MaterialSerializer
    items = Material.objects.all()
    low = [m for m in items if m.is_low_stock]
    return Response(MaterialSerializer(low, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inventory_stats_api(request):
    from django.db.models import Sum, Count
    stats = {
        'total_materials': Material.objects.count(),
        'low_stock_count': sum(1 for m in Material.objects.all() if m.is_low_stock),
        'total_transactions': StockTransaction.objects.count(),
    }
    return Response(stats)
