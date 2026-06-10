from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet


router = DefaultRouter()
router.register(r'user/contacts', ContactViewSet, basename='contacts')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/jwt/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
