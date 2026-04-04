from rest_framework import serializers
from .models import ConstructionPermit, PermitDocument


class PermitDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermitDocument
        fields = '__all__'


class ConstructionPermitSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    applicant_name = serializers.SerializerMethodField()
    documents = PermitDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ConstructionPermit
        fields = '__all__'

    def get_applicant_name(self, obj):
        if obj.applicant:
            return obj.applicant.get_full_name() or obj.applicant.username
        return None
