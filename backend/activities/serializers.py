from rest_framework import serializers
from django.utils import timezone
from .models import GroupBuyActivity, ActivityProduct, GroupBuyJoin
from products.serializers import ProductListSerializer, ProductSpecDetailSerializer


class ActivityProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    spec_name = serializers.CharField(source='product_spec.name', read_only=True)
    original_price = serializers.DecimalField(source='product_spec.price', max_digits=10, decimal_places=2, read_only=True)
    sold_quantity = serializers.IntegerField(read_only=True)
    available_stock = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ActivityProduct
        fields = [
            'id', 'activity', 'product', 'product_name', 'product_image',
            'product_spec', 'spec_name', 'original_price', 'group_price',
            'limit_per_user', 'is_active', 'sold_quantity', 'available_stock', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sold_quantity', 'available_stock']


class ActivityProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityProduct
        fields = [
            'id', 'product', 'product_spec', 'group_price', 'limit_per_user', 'is_active'
        ]
        read_only_fields = ['id']


class GroupBuyJoinSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GroupBuyJoin
        fields = [
            'id', 'user_name', 'product_name', 'spec_name', 'quantity', 
            'unit_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GroupBuyActivitySerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source='leader.username', read_only=True)
    leader_shop_name = serializers.CharField(source='leader.shop_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    products = ActivityProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupBuyActivity
        fields = [
            'id', 'title', 'description', 'leader', 'leader_name', 'leader_shop_name',
            'status', 'status_display', 'start_time', 'end_time',
            'delivery_type', 'delivery_type_display', 'pickup_address',
            'min_order_amount', 'share_code', 'is_active',
            'participant_count', 'total_orders', 'total_amount',
            'products', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'share_code', 'is_active', 'participant_count', 'total_orders', 'total_amount']


class GroupBuyActivityCreateSerializer(serializers.ModelSerializer):
    products = ActivityProductCreateSerializer(many=True, required=True)
    
    class Meta:
        model = GroupBuyActivity
        fields = [
            'title', 'description', 'start_time', 'end_time',
            'delivery_type', 'pickup_address', 'min_order_amount',
            'products'
        ]
    
    def validate_end_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("截止时间必须晚于当前时间")
        return value
    
    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("开始时间必须早于截止时间")
        
        if data.get('delivery_type') == GroupBuyActivity.DELIVERY_PICKUP and not data.get('pickup_address'):
            raise serializers.ValidationError("选择自提时必须填写自提点地址")
        
        products = data.get('products', [])
        if not products:
            raise serializers.ValidationError("至少需要选择一个商品")
        
        return data
    
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        validated_data['leader'] = self.context['request'].user
        validated_data['status'] = GroupBuyActivity.STATUS_DRAFT
        
        activity = GroupBuyActivity.objects.create(**validated_data)
        
        for product_data in products_data:
            ActivityProduct.objects.create(activity=activity, **product_data)
        
        return activity


class GroupBuyActivityListSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source='leader.username', read_only=True)
    leader_shop_name = serializers.CharField(source='leader.shop_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    min_price = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupBuyActivity
        fields = [
            'id', 'title', 'description', 'leader_name', 'leader_shop_name',
            'status', 'status_display', 'start_time', 'end_time',
            'delivery_type', 'delivery_type_display', 'pickup_address',
            'min_order_amount', 'share_code', 'is_active',
            'participant_count', 'min_price', 'cover_image', 'created_at'
        ]
    
    def get_min_price(self, obj):
        products = obj.products.filter(is_active=True)
        if products.exists():
            return min(p.group_price for p in products)
        return 0
    
    def get_cover_image(self, obj):
        products = obj.products.filter(is_active=True)
        if products.exists():
            first_product = products.first()
            if first_product.product and first_product.product.image:
                return first_product.product.image.url
        return None


class GroupBuyActivityDetailSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source='leader.username', read_only=True)
    leader_shop_name = serializers.CharField(source='leader.shop_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    products = ActivityProductSerializer(many=True, read_only=True)
    joins = GroupBuyJoinSerializer(many=True, read_only=True, source='joins.all')
    
    class Meta:
        model = GroupBuyActivity
        fields = [
            'id', 'title', 'description', 'leader', 'leader_name', 'leader_shop_name',
            'status', 'status_display', 'start_time', 'end_time',
            'delivery_type', 'delivery_type_display', 'pickup_address',
            'min_order_amount', 'share_code', 'is_active',
            'participant_count', 'total_orders', 'total_amount',
            'products', 'joins', 'created_at', 'updated_at'
        ]