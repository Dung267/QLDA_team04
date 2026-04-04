from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import BackupRecord, RestoreRecord, BackupConfig
from .serializers import BackupRecordSerializer, RestoreRecordSerializer, BackupConfigSerializer


class BackupListAPIView(generics.ListAPIView):
    queryset = BackupRecord.objects.all()
    serializer_class = BackupRecordSerializer
    permission_classes = [permissions.IsAdminUser]


class BackupDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = BackupRecord.objects.all()
    serializer_class = BackupRecordSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def trigger_backup_api(request):
    from datetime import datetime
    backup_type = request.data.get('type', 'full')
    fname = f"backup_{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    record = BackupRecord.objects.create(
        backup_type=backup_type,
        file_name=fname,
        status='success',
        created_by=request.user,
        completed_at=timezone.now(),
    )
    return Response(BackupRecordSerializer(record).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def restore_backup_api(request, pk):
    try:
        backup = BackupRecord.objects.get(pk=pk, status='success')
        record = RestoreRecord.objects.create(
            backup=backup,
            restored_by=request.user,
            status='success',
        )
        return Response({'success': True, 'restore_id': record.pk})
    except BackupRecord.DoesNotExist:
        return Response({'error': 'Backup not found or not successful'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def backup_config_api(request):
    config, _ = BackupConfig.objects.get_or_create(pk=1)
    return Response(BackupConfigSerializer(config).data)
