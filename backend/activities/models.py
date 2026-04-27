from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class GroupBuyActivity(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'
    STATUS_ENDED = 'ended'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, '草稿'),
        (STATUS_ACTIVE, '进行中'),
        (STATUS_CLOSED, '已关闭'),
        (STATUS_ENDED, '已结束'),
    ]
    
    DELIVERY_PICKUP = 'pickup'
    DELIVERY_DELIVERY = 'delivery'
    
    DELIVERY_CHOICES = [
        (DELIVERY_PICKUP, '自提'),
        (DELIVERY_DELIVERY, '配送'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='活动标题')
    description = models.TextField(blank=True, verbose_name='活动描述')
    
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='团长'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='活动状态'
    )
    
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='截止时间')
    
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_PICKUP,
        verbose_name='配送方式'
    )
    pickup_address = models.CharField(max_length=255, blank=True, verbose_name='自提点地址')
    
    min_order_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='起购金额'
    )
    
    share_code = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='分享码')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '团购活动'
        verbose_name_plural = '团购活动'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            import random
            import string
            self.share_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        now = timezone.now()
        return (
            self.status == self.STATUS_ACTIVE and
            self.start_time <= now <= self.end_time
        )
    
    @property
    def participant_count(self):
        return self.orders.values('user').distinct().count()
    
    @property
    def total_orders(self):
        return self.orders.count()
    
    @property
    def total_amount(self):
        from django.db.models import Sum
        from orders.models import Order
        return self.orders.filter(
            status__in=[Order.STATUS_PAID, Order.STATUS_PREPARING, Order.STATUS_DELIVERING, Order.STATUS_COMPLETED]
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0


class ActivityProduct(models.Model):
    activity = models.ForeignKey(
        GroupBuyActivity,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='所属活动'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name='商品'
    )
    product_spec = models.ForeignKey(
        'products.ProductSpec',
        on_delete=models.CASCADE,
        verbose_name='商品规格'
    )
    
    group_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='团购价')
    limit_per_user = models.PositiveIntegerField(default=0, verbose_name='每人限购数量（0表示不限）')
    
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '活动商品'
        verbose_name_plural = '活动商品'
        unique_together = ['activity', 'product_spec']
        ordering = ['id']
    
    def __str__(self):
        return f"{self.activity.title} - {self.product.name} - {self.product_spec.name}"
    
    @property
    def sold_quantity(self):
        from orders.models import OrderItem
        from django.db.models import Sum
        sold = OrderItem.objects.filter(
            activity_product=self,
            order__status__in=['paid', 'preparing', 'delivering', 'completed']
        ).aggregate(Sum('quantity'))['quantity__sum']
        return sold or 0
    
    @property
    def available_stock(self):
        return self.product_spec.stock - self.sold_quantity


class GroupBuyJoin(models.Model):
    activity = models.ForeignKey(
        GroupBuyActivity,
        on_delete=models.CASCADE,
        related_name='joins',
        verbose_name='所属活动'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='join_record',
        verbose_name='订单'
    )
    
    product_name = models.CharField(max_length=200, verbose_name='商品名称')
    spec_name = models.CharField(max_length=100, verbose_name='规格名称')
    quantity = models.PositiveIntegerField(verbose_name='购买数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='接龙时间')
    
    class Meta:
        verbose_name = '团购接龙'
        verbose_name_plural = '团购接龙'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product_name} - {self.quantity}份"