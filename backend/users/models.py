from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_LEADER = 'leader'
    ROLE_MEMBER = 'member'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, '平台管理员'),
        (ROLE_LEADER, '团长'),
        (ROLE_MEMBER, '团员'),
    ]
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已拒绝'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
        verbose_name='角色'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    
    leader_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='团长审核状态',
        help_text='仅当角色为团长时有效'
    )
    shop_name = models.CharField(max_length=100, blank=True, verbose_name='店铺名称')
    shop_address = models.CharField(max_length=255, blank=True, verbose_name='店铺地址')
    id_card = models.CharField(max_length=18, blank=True, verbose_name='身份证号')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    @property
    def is_leader(self):
        return self.role == self.ROLE_LEADER and self.leader_status == self.STATUS_APPROVED
    
    @property
    def is_member(self):
        return self.role == self.ROLE_MEMBER