from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Employee, WorkAssignment, LeaveRequest, Department, Training
from .serializers import (EmployeeSerializer, WorkAssignmentSerializer,
                           LeaveRequestSerializer, DepartmentSerializer, TrainingSerializer)


class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.select_related('user', 'department').filter(is_active=True)
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkAssignmentListAPIView(generics.ListCreateAPIView):
    serializer_class = WorkAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = WorkAssignment.objects.select_related('employee', 'assigned_by')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class LeaveRequestListAPIView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'employee_profile'):
            return LeaveRequest.objects.filter(employee=self.request.user.employee_profile)
        return LeaveRequest.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'employee_profile'):
            serializer.save(employee=self.request.user.employee_profile)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_leave_api(request, pk):
    try:
        leave = LeaveRequest.objects.get(pk=pk)
        action = request.data.get('action', 'approved')
        if action in ('approved', 'rejected'):
            leave.status = action
            leave.approved_by = request.user
            leave.save()
            return Response({'success': True, 'status': leave.status})
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
