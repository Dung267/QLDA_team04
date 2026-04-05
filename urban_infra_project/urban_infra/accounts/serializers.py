from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'role', 'role_display',
                  'phone', 'district', 'ward', 'is_locked', 'date_joined']
        read_only_fields = ['date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
