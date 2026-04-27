from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate, TruncMonth
from datetime import timedelta
import csv
import io
from django.http import HttpResponse

from orders.models import Order, OrderItem
from activities.models import GroupBuyActivity, ActivityProduct
from users.models import User
from users.permissions import IsAdmin, IsLeader, IsAdminOrLeader


class StatisticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def admin_dashboard(self, request):
        if not request.user.is_admin:
            return Response(
                {'error': '只有管理员可以查看平台统计'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        total_amount = Order.objects.filter(
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        active_leaders = User.objects.filter(
            role=User.ROLE_LEADER,
            leader_status=User.STATUS_APPROVED,
            activities__status=GroupBuyActivity.STATUS_ACTIVE
        ).distinct().count()
        
        total_orders = Order.objects.count()
        
        last_30_days_orders = Order.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        trading_trend = Order.objects.filter(
            created_at__gte=thirty_days_ago,
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_amount=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('date')
        
        hot_products = OrderItem.objects.filter(
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
            total_amount=Sum('subtotal'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')[:10]
        
        pending_leader_count = User.objects.filter(
            role=User.ROLE_LEADER,
            leader_status=User.STATUS_PENDING
        ).count()
        
        return Response({
            'total_amount': total_amount,
            'active_leaders': active_leaders,
            'total_orders': total_orders,
            'last_30_days_orders': last_30_days_orders,
            'pending_leader_count': pending_leader_count,
            'trading_trend': list(trading_trend),
            'hot_products': list(hot_products),
        })
    
    @action(detail=False, methods=['get'])
    def leader_dashboard(self, request):
        if not request.user.is_leader and not request.user.is_admin:
            return Response(
                {'error': '只有团长或管理员可以查看团长统计'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leader = request.user
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        activity_ids = GroupBuyActivity.objects.filter(leader=leader).values_list('id', flat=True)
        
        monthly_orders = Order.objects.filter(
            activity_id__in=activity_ids,
            created_at__gte=current_month_start,
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        )
        
        monthly_amount = monthly_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        monthly_order_count = monthly_orders.count()
        
        total_orders = Order.objects.filter(
            activity_id__in=activity_ids,
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING,
                Order.STATUS_COMPLETED
            ]
        )
        
        total_amount = total_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_order_count = total_orders.count()
        
        refunded_orders = Order.objects.filter(
            activity_id__in=activity_ids,
            status=Order.STATUS_REFUNDED
        )
        
        refunded_count = refunded_orders.count()
        refunded_amount = refunded_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        refund_rate = 0
        if total_order_count > 0:
            refund_rate = round((refunded_count / (total_order_count + refunded_count)) * 100, 2)
        
        active_activities = GroupBuyActivity.objects.filter(
            leader=leader,
            status=GroupBuyActivity.STATUS_ACTIVE,
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        recent_orders = Order.objects.filter(
            activity_id__in=activity_ids,
            status__in=[
                Order.STATUS_PAID,
                Order.STATUS_PREPARING,
                Order.STATUS_DELIVERING
            ]
        ).order_by('-created_at')[:10]
        
        recent_orders_data = []
        for order in recent_orders:
            recent_orders_data.append({
                'id': str(order.id),
                'order_no': order.order_no,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total_amount': order.total_amount,
                'receiver_name': order.receiver_name,
                'created_at': order.created_at,
                'activity_title': order.activity.title if order.activity else None,
            })
        
        return Response({
            'monthly_amount': monthly_amount,
            'monthly_order_count': monthly_order_count,
            'total_amount': total_amount,
            'total_order_count': total_order_count,
            'refunded_count': refunded_count,
            'refunded_amount': refunded_amount,
            'refund_rate': refund_rate,
            'active_activities': active_activities,
            'recent_orders': recent_orders_data,
        })
    
    @action(detail=False, methods=['get'])
    def export_orders_csv(self, request):
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
                {'error': '无权导出该活动订单'},
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
        ).prefetch_related('items').order_by('created_at')
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="orders_{activity_id}.csv"'
        
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        writer.writerow([
            '订单号', '商品名称', '规格', '单价', '数量', '小计',
            '收货人', '电话', '配送地址', '订单状态', '下单时间'
        ])
        
        for order in orders:
            for item in order.items.all():
                writer.writerow([
                    order.order_no,
                    item.product_name,
                    item.spec_name,
                    float(item.unit_price),
                    item.quantity,
                    float(item.subtotal),
                    order.receiver_name,
                    order.receiver_phone,
                    order.delivery_address or activity.pickup_address,
                    order.get_status_display(),
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def export_summary_by_spec(self, request):
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
                {'error': '无权导出该活动汇总'},
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
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="summary_by_spec_{activity_id}.csv"'
        
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        writer.writerow(['商品名称', '规格', '总数量', '总金额'])
        
        for item in items:
            writer.writerow([
                item['product_name'],
                item['spec_name'],
                item['total_quantity'],
                float(item['total_amount'])
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def export_summary_by_member(self, request):
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
                {'error': '无权导出该活动汇总'},
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
        ).select_related('user').prefetch_related('items').order_by('created_at')
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="summary_by_member_{activity_id}.csv"'
        
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        writer.writerow([
            '用户名', '收货人', '电话', '配送地址', '商品信息', '总数量', '总金额'
        ])
        
        for order in orders:
            items_info = []
            total_quantity = 0
            total_amount = 0
            
            for item in order.items.all():
                items_info.append(f"{item.product_name}({item.spec_name})x{item.quantity}")
                total_quantity += item.quantity
                total_amount += item.subtotal
            
            writer.writerow([
                order.user.username,
                order.receiver_name,
                order.receiver_phone,
                order.delivery_address or activity.pickup_address,
                '；'.join(items_info),
                total_quantity,
                float(total_amount)
            ])
        
        return response