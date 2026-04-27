from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from decimal import Decimal


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PREPARING = 'preparing'
    STATUS_DELIVERING = 'delivering'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDING = 'refunding'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, '待付款'),
        (STATUS_PAID, '已付款'),
        (STATUS_PREPARING, '备货中'),
        (STATUS_DELIVERING, '配送中'),
        (STATUS_COMPLETED, '已完成'),
        (STATUS_CANCELLED, '已取消'),
        (STATUS_REFUNDING, '退款中'),
        (STATUS_REFUNDED, '已退款'),
    ]
    
    STATUS_TRANSITIONS = {
        STATUS_PENDING: [STATUS_PAID, STATUS_CANCELLED],
        STATUS_PAID: [STATUS_PREPARING, STATUS_REFUNDING],
        STATUS_PREPARING: [STATUS_DELIVERING, STATUS_REFUNDING],
        STATUS_DELIVERING: [STATUS_COMPLETED],
        STATUS_COMPLETED: [],
        STATUS_CANCELLED: [],
        STATUS_REFUNDING: [STATUS_REFUNDED, STATUS_PAID],
        STATUS_REFUNDED: [],
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单号')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='用户'
    )
    activity = models.ForeignKey(
        'activities.GroupBuyActivity',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='团购活动'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='订单状态'
    )
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总金额')
    
    receiver_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    receiver_phone = models.CharField(max_length=20, verbose_name='收货人电话')
    delivery_address = models.CharField(max_length=255, blank=True, verbose_name='配送地址')
    
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='配送时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    remark = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_no']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order_no} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self._generate_order_no()
        super().save(*args, **kwargs)
    
    def _generate_order_no(self):
        import time
        import random
        timestamp = str(int(time.time()))
        random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"GB{timestamp}{random_str}"
    
    def can_transition_to(self, new_status):
        return new_status in self.STATUS_TRANSITIONS.get(self.status, [])
    
    @property
    def can_cancel(self):
        return self.status == self.STATUS_PENDING
    
    @property
    def can_pay(self):
        return self.status == self.STATUS_PENDING
    
    @property
    def can_apply_refund(self):
        return self.status in [self.STATUS_PAID, self.STATUS_PREPARING]
    
    @property
    def is_refundable(self):
        return self.status == self.STATUS_REFUNDING


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='订单'
    )
    activity_product = models.ForeignKey(
        'activities.ActivityProduct',
        on_delete=models.CASCADE,
        verbose_name='活动商品'
    )
    
    product_name = models.CharField(max_length=200, verbose_name='商品名称')
    spec_name = models.CharField(max_length=100, verbose_name='规格名称')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order.order_no} - {self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='订单'
    )
    from_status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='原状态'
    )
    to_status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        verbose_name='新状态'
    )
    
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作人'
    )
    
    remark = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '订单状态日志'
        verbose_name_plural = '订单状态日志'
        ordering = ['-created_at']
    
    def __str__(self):
        from_display = self.get_from_status_display() if self.from_status else '无'
        return f"{self.order.order_no}: {from_display} → {self.get_to_status_display()}"