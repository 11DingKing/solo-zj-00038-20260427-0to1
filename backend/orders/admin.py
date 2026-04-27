from django.contrib import admin
from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product_name', 'spec_name', 'unit_price', 'quantity', 'subtotal']
    readonly_fields = ['product_name', 'spec_name', 'unit_price', 'quantity', 'subtotal']
    can_delete = False


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    fields = ['from_status', 'to_status', 'operator', 'remark', 'created_at']
    readonly_fields = ['from_status', 'to_status', 'operator', 'remark', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_no', 'user', 'activity', 'status', 'total_amount',
        'receiver_name', 'receiver_phone', 'paid_at', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['order_no', 'user__username', 'receiver_name', 'receiver_phone']
    readonly_fields = ['id', 'order_no', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusLogInline]
    ordering = ['-created_at']
    raw_id_fields = ['user', 'activity']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'order_no', 'user', 'activity')
        }),
        ('订单状态', {
            'fields': ('status', 'total_amount')
        }),
        ('收货信息', {
            'fields': ('receiver_name', 'receiver_phone', 'delivery_address')
        }),
        ('时间信息', {
            'fields': ('paid_at', 'delivered_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('备注', {
            'fields': ('remark',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product_name', 'spec_name', 'unit_price',
        'quantity', 'subtotal', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['order__order_no', 'product_name', 'spec_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['order', 'activity_product']


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'from_status', 'to_status', 'operator', 'created_at'
    ]
    list_filter = ['from_status', 'to_status', 'created_at']
    search_fields = ['order__order_no', 'operator__username', 'remark']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['order', 'operator']