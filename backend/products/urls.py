from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductSpecViewSet

router = DefaultRouter()
router.register(r'specs', ProductSpecViewSet, basename='product-spec')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]