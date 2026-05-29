from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Danh sách tài liệu
    path('', views.list_documents, name='list'),
    
    # Upload tài liệu
    path('upload/', views.upload_document, name='upload'),
    
    # Chi tiết tài liệu
    path('<int:pk>/', views.document_detail, name='detail'),
    
    # Chỉnh sửa tài liệu
    path('<int:pk>/edit/', views.edit_document, name='edit'),
    
    # Xóa tài liệu
    path('<int:pk>/delete/', views.delete_document, name='delete'),
    
    # Download tài liệu
    path('<int:pk>/download/', views.download_document, name='download'),
]