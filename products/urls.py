from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SupplierUpdateView, SupplierStatusView


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('supplier/update/', SupplierUpdateView.as_view(), name='supplier-update'),
    path('supplier/status/', SupplierStatusView.as_view(), name='supplier-status'),
]