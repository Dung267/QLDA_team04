from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.DocumentListAPIView.as_view(), name='api_document_list'),
    path('<int:pk>/', api_views.DocumentDetailAPIView.as_view(), name='api_document_detail'),
    path('categories/', api_views.DocumentCategoryListAPIView.as_view(), name='api_doc_categories'),
]
