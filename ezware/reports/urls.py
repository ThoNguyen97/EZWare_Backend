from django.urls import path
from . import views

urlpatterns = [
    path('reports/low-stock', views.LowStockReportView.as_view(), name='report-low-stock'),
]
