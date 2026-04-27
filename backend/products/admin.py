from django.contrib import admin
from .models import Product, ProductSpec


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1
    fields = ['name', 'price', 'stock', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'min_price', 'specs_count', 'total_stock', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [ProductSpecInline]
    readonly_fields = ['specs_count', 'min_price', 'total_stock', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'image', 'description', 'is_active')
        }),
        ('统计信息', {
            'fields': ('specs_count', 'min_price', 'total_stock'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'name']
    ordering = ['product', 'id']