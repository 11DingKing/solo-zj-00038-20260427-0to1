from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupBuyActivityViewSet, ActivityProductViewSet

router = DefaultRouter()
router.register(r'products', ActivityProductViewSet, basename='activity-product')
router.register(r'', GroupBuyActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]