from rest_framework import serializers
from .models import Material, StockTransaction, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Material
        fields = '__all__'


class StockTransactionSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    performer_name = serializers.SerializerMethodField()

    class Meta:
        model = StockTransaction
        fields = '__all__'

    def get_performer_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return None
