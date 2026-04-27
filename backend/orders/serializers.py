from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem, OrderStatusLog
from activities.models import GroupBuyActivity, ActivityProduct, GroupBuyJoin
from products.models import ProductSpec


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'activity_product', 'product_name', 'spec_name',
            'unit_price', 'quantity', 'subtotal'
        ]
        read_only_fields = ['id', 'product_name', 'spec_name', 'unit_price', 'subtotal']


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'spec_name', 'unit_price',
            'quantity', 'subtotal', 'product_image'
        ]
    
    def get_product_image(self, obj):
        if obj.activity_product and obj.activity_product.product and obj.activity_product.product.image:
            return obj.activity_product.product.image.url
        return None


class OrderItemCreateSerializer(serializers.Serializer):
    activity_product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    activity_id = serializers.UUIDField()
    items = OrderItemCreateSerializer(many=True)
    receiver_name = serializers.CharField(max_length=50)
    receiver_phone = serializers.CharField(max_length=20)
    delivery_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        from django.db import transaction
        import redis
        from django.conf import settings
        
        activity_id = data['activity_id']
        items = data['items']
        
        try:
            activity = GroupBuyActivity.objects.get(id=activity_id)
        except GroupBuyActivity.DoesNotExist:
            raise serializers.ValidationError('团购活动不存在')
        
        if not activity.is_active:
            raise serializers.ValidationError('活动未开始或已结束')
        
        now = timezone.now()
        if now < activity.start_time or now > activity.end_time:
            raise serializers.ValidationError('活动不在有效时间内')
        
        if activity.delivery_type == GroupBuyActivity.DELIVERY_DELIVERY and not data.get('delivery_address'):
            raise serializers.ValidationError('配送模式需要填写配送地址')
        
        if not items:
            raise serializers.ValidationError('至少需要选择一个商品')
        
        total_amount = Decimal('0')
        activity_products = {}
        
        for item in items:
            try:
                ap = ActivityProduct.objects.select_related('product_spec').get(
                    id=item['activity_product_id'],
                    activity=activity,
                    is_active=True
                )
            except ActivityProduct.DoesNotExist:
                raise serializers.ValidationError(f"活动商品不存在: {item['activity_product_id']}")
            
            quantity = item['quantity']
            
            if ap.limit_per_user > 0:
                user_purchased = OrderItem.objects.filter(
                    activity_product=ap,
                    order__user=self.context['request'].user,
                    order__status__in=[
                        Order.STATUS_PAID, 
                        Order.STATUS_PREPARING, 
                        Order.STATUS_DELIVERING, 
                        Order.STATUS_COMPLETED
                    ]
                ).aggregate(total=models.Sum('quantity'))['total'] or 0
                
                if user_purchased + quantity > ap.limit_per_user:
                    raise serializers.ValidationError(
                        f"商品 {ap.product.name} {ap.product_spec.name} 每人限购 {ap.limit_per_user} 份，"
                        f"您已购买 {user_purchased} 份"
                    )
            
            available_stock = ap.available_stock
            if available_stock < quantity:
                raise serializers.ValidationError(
                    f"商品 {ap.product.name} {ap.product_spec.name} 库存不足，"
                    f"当前库存: {available_stock}"
                )
            
            item_subtotal = ap.group_price * quantity
            total_amount += item_subtotal
            
            activity_products[item['activity_product_id']] = {
                'ap': ap,
                'quantity': quantity,
                'subtotal': item_subtotal
            }
        
        if total_amount < activity.min_order_amount:
            raise serializers.ValidationError(
                f"订单金额 {total_amount} 元未达到起购金额 {activity.min_order_amount} 元"
            )
        
        data['activity'] = activity
        data['activity_products'] = activity_products
        data['total_amount'] = total_amount
        
        return data


class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemDetailSerializer(many=True, read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_pay = serializers.BooleanField(read_only=True)
    can_apply_refund = serializers.BooleanField(read_only=True)
    is_refundable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'activity', 'status', 'status_display',
            'total_amount', 'receiver_name', 'receiver_phone', 'delivery_address',
            'remark', 'paid_at', 'delivered_at', 'completed_at',
            'items', 'can_cancel', 'can_pay', 'can_apply_refund', 'is_refundable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_no', 'status', 'paid_at', 'delivered_at', 'completed_at', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    leader_name = serializers.CharField(source='activity.leader.username', read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'activity_title', 'leader_name',
            'status', 'status_display', 'total_amount', 'item_count',
            'created_at'
        ]


class OrderStatusLogSerializer(serializers.ModelSerializer):
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True, default='系统')
    
    class Meta:
        model = OrderStatusLog
        fields = [
            'id', 'from_status', 'from_status_display',
            'to_status', 'to_status_display',
            'operator', 'operator_name', 'remark', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderSummaryBySpecSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    spec_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderSummaryByMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    receiver_name = serializers.CharField()
    receiver_phone = serializers.CharField()
    delivery_address = serializers.CharField()
    total_quantity = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    items = OrderItemDetailSerializer(many=True)