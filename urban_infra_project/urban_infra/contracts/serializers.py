from rest_framework import serializers
from .models import Contract, Tender, Contractor


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = '__all__'

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class TenderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Tender
        fields = '__all__'
