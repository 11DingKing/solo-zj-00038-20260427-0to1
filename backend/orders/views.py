from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count
from django.core.cache import cache
import redis
from django.conf import settings
from decimal import Decimal
import uuid

from .models import Order, OrderItem, OrderStatusLog
from .serializers import (
    OrderSerializer, OrderListSerializer, OrderCreateSerializer,
    OrderStatusLogSerializer, OrderSummaryBySpecSerializer,
    OrderSummaryByMemberSerializer
)
from activities.models import GroupBuyActivity, ActivityProduct, GroupBuyJoin
from users.permissions import IsLeader, IsAdminOrLeader


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'user', 'activity', 'activity__leader'
    ).prefetch_related('items', 'items__activity_product', 'status_logs')
    
    def get_permissions(self):
        if self.action in ['create', 'my_orders', 'cancel', 'pay', 'apply_refund']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['activity_orders', 'summary_by_spec', 'summary_by_member', 
                             'update_status', 'process_refund', 'export_csv']:
            return [IsLeader()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if self.action == 'list':
            if not user.is_admin:
                queryset = queryset.filter(user=user)
            
            activity_id = self.request.query_params.get('activity', None)
            if activity_id:
                queryset = queryset.filter(activity_id=activity_id)
            
            status_filter = self.request.query_params.get('status', None)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.annotate(item_count=Count('items'))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not request.user.is_admin and instance.user != request.user and instance.activity.leader != request.user:
            return Response(
                {'error': '无权查看该订单'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        activity = validated_data['activity']
        activity_products = validated_data['activity_products']
        total_amount = validated_data['total_amount']
        
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )
        
        try:
            with transaction.atomic():
                lock_key = f"order:lock:activity:{activity.id}"
                lock = redis_client.lock(lock_key, timeout=10)
                
                if not lock.acquire(blocking_timeout=5):
                    return Response(
                        {'error': '系统繁忙，请稍后再试'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                
                try:
                    for item_id, item_data in activity_products.items():
                        ap = item_data['ap']
                        quantity = item_data['quantity']
                        
                        sold_quantity = OrderItem.objects.filter(
                            activity_product=ap,
                            order__status__in=[
                                Order.STATUS_PAID, 
                                Order.STATUS_PREPARING, 
                                Order.STATUS_DELIVERING, 
                                Order.STATUS_COMPLETED
                            ]
                        ).aggregate(total=Sum('quantity'))['total'] or 0
                        
                        available_stock = ap.product_spec.stock - sold_quantity
                        
                        if available_stock < quantity:
                            raise serializers.ValidationError(
                                f"商品 {ap.product.name} {ap.product_spec.name} 库存不足"
                            )
                    
                    order = Order.objects.create(
                        user=request.user,
                        activity=activity,
                        status=Order.STATUS_PENDING,
                        total_amount=total_amount,
                        receiver_name=validated_data['receiver_name'],
                        receiver_phone=validated_data['receiver_phone'],
                        delivery_address=validated_data.get('delivery_address', ''),
                        remark=validated_data.get('remark', '')
                    )
                    
                    for item_id, item_data in activity_products.items():
                        ap = item_data['ap']
                        quantity = item_data['quantity']
                        
                        OrderItem.objects.create(
                            order=order,
                            activity_product=ap,
                            product_name=ap.product.name,
                            spec_name=ap.product_spec.name,
                            unit_price=ap.group_price,
                            quantity=quantity,
                            subtotal=item_data['subtotal']
                        )
                    
                    OrderStatusLog.objects.create(
                        order=order,
                        from_status=None,
                        to_status=Order.STATUS_PENDING,
                        operator=request.user,
                        remark='订单创建'
                    )
                    
                finally:
                    lock.release()
            
            cache.delete(f'activity:{activity.id}')
            
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        queryset = self.get_queryset().filter(user=request.user).annotate(item_count=Count('items'))
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activity_orders(self, request):
        activity_id = request.query_params.get('activity', None)
        if not activity_id:
            return Response(
                {'error': '请提供活动ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            activity = GroupBuyActivity.objects.get(id=activity_id)
        except GroupBuyActivity.DoesNotExist:
            return Response(
                {'error': '活动不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '无权查看该活动订单'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(
            activity=activity
        ).annotate(item_count=Count('items'))
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.user != request.user:
            return Response(
                {'error': '只能取消自己的订单'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not order.can_cancel:
            return Response(
                {'error': '当前订单状态不能取消'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_status = order.status
            order.status = Order.STATUS_CANCELLED
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                from_status=old_status,
                to_status=Order.STATUS_CANCELLED,
                operator=request.user,
                remark='用户取消订单'
            )
        
        return Response({'message': '订单已取消'})
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        
        if order.user != request.user:
            return Response(
                {'error': '只能支付自己的订单'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not order.can_pay:
            return Response(
                {'error': '当前订单状态不能支付'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )
        
        try:
            with transaction.atomic():
                lock_key = f"order:lock:pay:{order.id}"
                lock = redis_client.lock(lock_key, timeout=10)
                
                if not lock.acquire(blocking_timeout=5):
                    return Response(
                        {'error': '系统繁忙，请稍后再试'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                
                try:
                    items = order.items.select_related('activity_product', 'activity_product__product_spec').all()
                    
                    for item in items:
                        ap = item.activity_product
                        spec = ap.product_spec
                        
                        sold_quantity = OrderItem.objects.filter(
                            activity_product=ap,
                            order__status__in=[
                                Order.STATUS_PAID, 
                                Order.STATUS_PREPARING, 
                                Order.STATUS_DELIVERING, 
                                Order.STATUS_COMPLETED
                            ]
                        ).aggregate(total=Sum('quantity'))['total'] or 0
                        
                        available_stock = spec.stock - sold_quantity
                        
                        if available_stock < item.quantity:
                            raise Exception(f"商品 {item.product_name} {item.spec_name} 库存不足")
                    
                    old_status = order.status
                    order.status = Order.STATUS_PAID
                    order.paid_at = timezone.now()
                    order.save()
                    
                    OrderStatusLog.objects.create(
                        order=order,
                        from_status=old_status,
                        to_status=Order.STATUS_PAID,
                        operator=request.user,
                        remark='模拟支付成功'
                    )
                    
                    for item in items:
                        GroupBuyJoin.objects.create(
                            activity=order.activity,
                            user=order.user,
                            order=order,
                            product_name=item.product_name,
                            spec_name=item.spec_name,
                            quantity=item.quantity,
                            unit_price=item.unit_price
                        )
                    
                finally:
                    lock.release()
            
            cache.delete(f'activity:{order.activity.id}')
            
            return Response({
                'message': '支付成功',
                'order': OrderSerializer(order).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def apply_refund(self, request, pk=None):
        order = self.get_object()
        
        if order.user != request.user:
            return Response(
                {'error': '只能对自己的订单申请退款'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not order.can_apply_refund:
            return Response(
                {'error': '当前订单状态不能申请退款'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        with transaction.atomic():
            old_status = order.status
            order.status = Order.STATUS_REFUNDING
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                from_status=old_status,
                to_status=Order.STATUS_REFUNDING,
                operator=request.user,
                remark=f'申请退款: {reason}'
            )
        
        return Response({'message': '退款申请已提交'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        
        if order.activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '无权操作该订单'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        remark = request.data.get('remark', '')
        
        if not order.can_transition_to(new_status):
            return Response(
                {'error': f'不能从 {order.get_status_display()} 转换到 {Order(new_status).get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status in [Order.STATUS_REFUNDED, Order.STATUS_REFUNDING]:
            return Response(
                {'error': '请使用退款相关接口处理退款'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_status = order.status
            order.status = new_status
            
            if new_status == Order.STATUS_DELIVERING:
                order.delivered_at = timezone.now()
            elif new_status == Order.STATUS_COMPLETED:
                order.completed_at = timezone.now()
            
            order.save()
            
            status_remarks = {
                Order.STATUS_PREPARING: '开始备货',
                Order.STATUS_DELIVERING: '开始配送',
                Order.STATUS_COMPLETED: '订单完成',
            }
            
            OrderStatusLog.objects.create(
                order=order,
                from_status=old_status,
                to_status=new_status,
                operator=request.user,
                remark=remark or status_remarks.get(new_status, '状态更新')
            )
        
        return Response({
            'message': '订单状态已更新',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['post'])
    def process_refund(self, request, pk=None):
        order = self.get_object()
        
        if order.activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '无权处理该退款'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != Order.STATUS_REFUNDING:
            return Response(
                {'error': '当前订单不是退款中状态'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = request.data.get('action')
        remark = request.data.get('remark', '')
        
        if action == 'approve':
            new_status = Order.STATUS_REFUNDED
            log_remark = f'退款已批准: {remark}'
        elif action == 'reject':
            new_status = Order.STATUS_PAID
            log_remark = f'退款被拒绝: {remark}'
        else:
            return Response(
                {'error': '操作类型只能是 approve 或 reject'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            old_status = order.status
            order.status = new_status
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                from_status=old_status,
                to_status=new_status,
                operator=request.user,
                remark=log_remark
            )
        
        return Response({
            'message': '退款已处理',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=False, methods=['get'])
    def summary_by_spec(self, request):
        activity_id = request.query_params.get('activity', None)
        if not activity_id:
            return Response(
                {'error': '请提供活动ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            activity = GroupBuyActivity.objects.get(id=activity_id)
        except GroupBuyActivity.DoesNotExist:
            return Response(
                {'error': '活动不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '无权查看该活动汇总'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        items = OrderItem.objects.filter(
            order__activity=activity,
            order__status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        ).values(
            'product_name', 'spec_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum('subtotal')
        ).order_by('product_name', 'spec_name')
        
        return Response(list(items))
    
    @action(detail=False, methods=['get'])
    def summary_by_member(self, request):
        activity_id = request.query_params.get('activity', None)
        if not activity_id:
            return Response(
                {'error': '请提供活动ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            activity = GroupBuyActivity.objects.get(id=activity_id)
        except GroupBuyActivity.DoesNotExist:
            return Response(
                {'error': '活动不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if activity.leader != request.user and not request.user.is_admin:
            return Response(
                {'error': '无权查看该活动汇总'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        orders = Order.objects.filter(
            activity=activity,
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        ).select_related('user').prefetch_related('items')
        
        result = []
        for order in orders:
            items = list(order.items.values(
                'product_name', 'spec_name', 'unit_price', 'quantity', 'subtotal'
            ))
            
            total_quantity = sum(item['quantity'] for item in items)
            total_amount = sum(item['subtotal'] for item in items)
            
            result.append({
                'user_id': order.user.id,
                'user_name': order.user.username,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone,
                'delivery_address': order.delivery_address or activity.pickup_address,
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'items': items
            })
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def status_logs(self, request, pk=None):
        order = self.get_object()
        
        if not request.user.is_admin and order.user != request.user and order.activity.leader != request.user:
            return Response(
                {'error': '无权查看该订单日志'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        logs = order.status_logs.select_related('operator').order_by('-created_at')
        serializer = OrderStatusLogSerializer(logs, many=True)
        return Response(serializer.data)