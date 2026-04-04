from django.urls import path
from . import api_views

urlpatterns = [
    path('contracts/', api_views.ContractListAPIView.as_view(), name='api_contract_list'),
    path('contracts/<int:pk>/', api_views.ContractDetailAPIView.as_view(), name='api_contract_detail'),
    path('tenders/', api_views.TenderListAPIView.as_view(), name='api_tender_list'),
    path('contractors/', api_views.ContractorListAPIView.as_view(), name='api_contractor_list'),
    path('stats/', api_views.contract_stats_api, name='api_contract_stats'),
]
