from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'leader_status', 'is_active', 'created_at']
    list_filter = ['role', 'leader_status', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone', 'shop_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('角色信息', {
            'fields': ('role', 'phone', 'avatar')
        }),
        ('团长信息', {
            'fields': ('leader_status', 'shop_name', 'shop_address', 'id_card'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('角色信息', {
            'fields': ('role', 'phone', 'avatar')
        }),
    )