from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('activities', '0001_initial'),
        ('products', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order_no', models.CharField(max_length=32, unique=True, verbose_name='订单号')),
                ('status', models.CharField(choices=[('pending', '待付款'), ('paid', '已付款'), ('preparing', '备货中'), ('delivering', '配送中'), ('completed', '已完成'), ('cancelled', '已取消'), ('refunding', '退款中'), ('refunded', '已退款')], default='pending', max_length=20, verbose_name='订单状态')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单总金额')),
                ('receiver_name', models.CharField(max_length=50, verbose_name='收货人姓名')),
                ('receiver_phone', models.CharField(max_length=20, verbose_name='收货人电话')),
                ('delivery_address', models.CharField(blank=True, max_length=255, verbose_name='配送地址')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='支付时间')),
                ('delivered_at', models.DateTimeField(blank=True, null=True, verbose_name='配送时间')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('remark', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='activities.groupbuyactivity', verbose_name='团购活动')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderStatusLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('from_status', models.CharField(blank=True, choices=[('pending', '待付款'), ('paid', '已付款'), ('preparing', '备货中'), ('delivering', '配送中'), ('completed', '已完成'), ('cancelled', '已取消'), ('refunding', '退款中'), ('refunded', '已退款')], max_length=20, null=True, verbose_name='原状态')),
                ('to_status', models.CharField(choices=[('pending', '待付款'), ('paid', '已付款'), ('preparing', '备货中'), ('delivering', '配送中'), ('completed', '已完成'), ('cancelled', '已取消'), ('refunding', '退款中'), ('refunded', '已退款')], max_length=20, verbose_name='新状态')),
                ('remark', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='操作人')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_logs', to='orders.order', verbose_name='订单')),
            ],
            options={
                'verbose_name': '订单状态日志',
                'verbose_name_plural': '订单状态日志',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=200, verbose_name='商品名称')),
                ('spec_name', models.CharField(max_length=100, verbose_name='规格名称')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('quantity', models.PositiveIntegerField(verbose_name='数量')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='小计')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('activity_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activities.activityproduct', verbose_name='活动商品')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order', verbose_name='订单')),
            ],
            options={
                'verbose_name': '订单项',
                'verbose_name_plural': '订单项',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_no'], name='orders_orde_order_no_b63f0b_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user', '-created_at'], name='orders_orde_user_id_122386_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['activity', '-created_at'], name='orders_orde_activit_38d294_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='orders_orde_status_822781_idx'),
        ),
    ]
