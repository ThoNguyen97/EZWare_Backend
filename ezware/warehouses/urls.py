from django.urls import path
from . import views

urlpatterns = [
    path('warehouses', views.WarehouseListCreateView.as_view(), name='warehouse-list-create'),
    path('warehouses/<int:warehouse_id>', views.WarehouseDetailView.as_view(), name='warehouse-detail'),
    path(
        'warehouses/<int:warehouse_id>/inventory',
        views.WarehouseInventoryView.as_view(),
        name='warehouse-inventory',
    ),
]
