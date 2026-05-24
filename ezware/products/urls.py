from django.urls import path
from . import views

urlpatterns = [
    path('products', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:product_id>', views.ProductDetailView.as_view(), name='product-detail'),
]
