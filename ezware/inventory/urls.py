from django.urls import path
from . import views

urlpatterns = [
    path('receipts', views.ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('receipts/<int:receipt_id>', views.ReceiptDetailGetView.as_view(), name='receipt-detail'),
    path(
        'receipts/<int:receipt_id>/details',
        views.ReceiptDetailAddView.as_view(),
        name='receipt-detail-add',
    ),
    path(
        'receipts/<int:receipt_id>/status',
        views.ReceiptUpdateStatusView.as_view(),
        name='receipt-update-status',
    ),
]
