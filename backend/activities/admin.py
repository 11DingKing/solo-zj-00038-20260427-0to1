from django.contrib import admin
from .models import GroupBuyActivity, ActivityProduct, GroupBuyJoin


class ActivityProductInline(admin.TabularInline):
    model = ActivityProduct
    extra = 0
    fields = ['product', 'product_spec', 'group_price', 'limit_per_user', 'is_active']
    raw_id_fields = ['product', 'product_spec']


class GroupBuyJoinInline(admin.TabularInline):
    model = GroupBuyJoin
    extra = 0
    fields = ['user', 'product_name', 'spec_name', 'quantity', 'unit_price', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'order']


@admin.register(GroupBuyActivity)
class GroupBuyActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'leader', 'status', 'start_time', 'end_time',
        'delivery_type', 'min_order_amount', 'participant_count',
        'total_orders', 'created_at'
    ]
    list_filter = ['status', 'delivery_type', 'start_time', 'end_time', 'created_at']
    search_fields = ['title', 'description', 'leader__username', 'share_code']
    readonly_fields = ['id', 'share_code', 'participant_count', 'total_orders', 'total_amount', 'created_at', 'updated_at']
    inlines = [ActivityProductInline, GroupBuyJoinInline]
    ordering = ['-created_at']
    raw_id_fields = ['leader']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'title', 'description', 'leader', 'status', 'share_code')
        }),
        ('时间设置', {
            'fields': ('start_time', 'end_time')
        }),
        ('配送设置', {
            'fields': ('delivery_type', 'pickup_address', 'min_order_amount')
        }),
        ('统计信息', {
            'fields': ('participant_count', 'total_orders', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityProduct)
class ActivityProductAdmin(admin.ModelAdmin):
    list_display = [
        'activity', 'product', 'product_spec', 'group_price',
        'limit_per_user', 'is_active', 'sold_quantity', 'available_stock'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['activity__title', 'product__name', 'product_spec__name']
    readonly_fields = ['sold_quantity', 'available_stock', 'created_at']
    raw_id_fields = ['activity', 'product', 'product_spec']
    ordering = ['-created_at']


@admin.register(GroupBuyJoin)
class GroupBuyJoinAdmin(admin.ModelAdmin):
    list_display = [
        'activity', 'user', 'product_name', 'spec_name',
        'quantity', 'unit_price', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['activity__title', 'user__username', 'product_name', 'spec_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['activity', 'user', 'order']
    ordering = ['-created_at']