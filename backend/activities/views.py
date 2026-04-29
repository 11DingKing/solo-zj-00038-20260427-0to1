from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from .models import GroupBuyActivity, ActivityProduct, GroupBuyJoin
from .serializers import (
    GroupBuyActivitySerializer, GroupBuyActivityCreateSerializer,
    GroupBuyActivityListSerializer, GroupBuyActivityDetailSerializer,
    ActivityProductSerializer, GroupBuyJoinSerializer
)
from users.permissions import IsLeader, IsAdmin
import uuid


class GroupBuyActivityViewSet(viewsets.ModelViewSet):
    queryset = GroupBuyActivity.objects.select_related('leader').prefetch_related(
        'products', 'products__product', 'products__product_spec', 'joins', 'joins__user'
    )
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'by_share_code', 'joins']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'publish', 'close', 'my_activities']:
            return [IsLeader()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GroupBuyActivityListSerializer
        elif self.action == 'create':
            return GroupBuyActivityCreateSerializer
        elif self.action == 'retrieve':
            return GroupBuyActivityDetailSerializer
        return GroupBuyActivitySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if self.action == 'list':
            status_filter = self.request.query_params.get('status', None)
            if status_filter == 'active':
                now = timezone.now()
                queryset = queryset.filter(
                    status=GroupBuyActivity.STATUS_ACTIVE,
                    start_time__lte=now,
                    end_time__gte=now
                )
            elif status_filter:
                queryset = queryset.filter(status=status_filter)
            
            leader_id = self.request.query_params.get('leader', None)
            if leader_id:
                queryset = queryset.filter(leader_id=leader_id)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'activity:{instance.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        user = request.user
        activities = self.get_queryset().filter(leader=user)
        serializer = GroupBuyActivityListSerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_share_code(self, request):
        share_code = request.query_params.get('code', None)
        if not share_code:
            return Response({'error': '请提供分享码'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            activity = self.get_queryset().get(share_code=share_code)
            serializer = GroupBuyActivityDetailSerializer(activity)
            return Response(serializer.data)
        except GroupBuyActivity.DoesNotExist:
            return Response({'error': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        activity = self.get_object()
        
        if activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '只有活动创建者或管理员可以发布活动'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if activity.status != GroupBuyActivity.STATUS_DRAFT:
            return Response(
                {'error': '只能发布草稿状态的活动'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not activity.products.filter(is_active=True).exists():
            return Response(
                {'error': '活动至少需要一个有效商品'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activity.status = GroupBuyActivity.STATUS_ACTIVE
        activity.save()
        
        cache.delete(f'activity:{activity.id}')
        cache.delete_pattern('activity:*')
        
        return Response({
            'message': '活动发布成功',
            'share_code': activity.share_code,
            'share_link': f'/activity/{activity.id}'
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        activity = self.get_object()
        
        if activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '只有活动创建者或管理员可以关闭活动'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if activity.status != GroupBuyActivity.STATUS_ACTIVE:
            return Response(
                {'error': '只能关闭进行中的活动'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activity.status = GroupBuyActivity.STATUS_CLOSED
        activity.save()
        
        cache.delete(f'activity:{activity.id}')
        cache.delete_pattern('activity:*')
        
        return Response({'message': '活动已关闭'})
    
    @action(detail=True, methods=['get'])
    def joins(self, request, pk=None):
        activity = self.get_object()
        joins = activity.joins.select_related('user').order_by('-created_at')
        
        page = self.paginate_queryset(joins)
        if page is not None:
            serializer = GroupBuyJoinSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = GroupBuyJoinSerializer(joins, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def share_info(self, request, pk=None):
        activity = self.get_object()
        
        if not activity.is_active:
            return Response(
                {'error': '活动未开始或已结束'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        first_product = activity.products.filter(is_active=True).first()
        cover_image = first_product.product.image.url if first_product and first_product.product.image else None
        min_price = min(p.group_price for p in activity.products.filter(is_active=True)) if activity.products.filter(is_active=True).exists() else 0
        
        return Response({
            'id': str(activity.id),
            'title': activity.title,
            'share_code': activity.share_code,
            'share_link': f'/activity/{activity.id}?code={activity.share_code}',
            'cover_image': cover_image,
            'min_price': min_price,
            'participant_count': activity.participant_count,
            'end_time': activity.end_time.isoformat(),
            'leader_name': activity.leader.username,
            'shop_name': activity.leader.shop_name,
        })


class ActivityProductViewSet(viewsets.ModelViewSet):
    queryset = ActivityProduct.objects.select_related('activity', 'product', 'product_spec').all()
    serializer_class = ActivityProductSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsLeader()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        activity_id = self.request.query_params.get('activity', None)
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete(f'activity:{instance.activity.id}')
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'activity:{instance.activity.id}')
    
    def perform_destroy(self, instance):
        activity_id = instance.activity.id
        instance.delete()
        cache.delete(f'activity:{activity_id}')