from django.db import models
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='商品名称')
    image = models.ImageField(upload_to='products/', verbose_name='商品图片')
    description = models.TextField(verbose_name='商品描述')
    
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def specs_count(self):
        return self.specs.count()
    
    @property
    def min_price(self):
        specs = self.specs.filter(is_active=True)
        if specs.exists():
            return min(spec.price for spec in specs)
        return 0
    
    @property
    def total_stock(self):
        specs = self.specs.filter(is_active=True)
        return sum(spec.stock for spec in specs)


class ProductSpec(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specs',
        verbose_name='所属商品'
    )
    name = models.CharField(max_length=100, verbose_name='规格名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    stock = models.PositiveIntegerField(default=0, verbose_name='库存')
    
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品规格'
        verbose_name_plural = '商品规格'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        self.stock += quantity
        self.save()