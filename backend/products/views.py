from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from .models import Product, ProductSpec
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductListSerializer,
    ProductSpecSerializer
)
from users.permissions import IsAdmin, IsAdminOrLeader


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('specs')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.action == 'list':
            is_active = self.request.query_params.get('is_active', None)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'product:{instance.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=3600)
        return Response(data)
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete_pattern('product:*')
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'product:{instance.id}')
        cache.delete_pattern('product:*')
    
    def perform_destroy(self, instance):
        product_id = instance.id
        instance.delete()
        cache.delete(f'product:{product_id}')
        cache.delete_pattern('product:*')
    
    @action(detail=True, methods=['get'])
    def specs(self, request, pk=None):
        product = self.get_object()
        specs = product.specs.all()
        serializer = ProductSpecSerializer(specs, many=True)
        return Response(serializer.data)


class ProductSpecViewSet(viewsets.ModelViewSet):
    queryset = ProductSpec.objects.select_related('product').all()
    serializer_class = ProductSpecSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete(f'product:{instance.product.id}')
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'product:{instance.product.id}')
    
    def perform_destroy(self, instance):
        product_id = instance.product.id
        instance.delete()
        cache.delete(f'product:{product_id}')