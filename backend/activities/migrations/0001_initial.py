from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupBuyActivity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='活动标题')),
                ('description', models.TextField(blank=True, verbose_name='活动描述')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('active', '进行中'), ('closed', '已关闭'), ('ended', '已结束')], default='draft', max_length=20, verbose_name='活动状态')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='截止时间')),
                ('delivery_type', models.CharField(choices=[('pickup', '自提'), ('delivery', '配送')], default='pickup', max_length=20, verbose_name='配送方式')),
                ('pickup_address', models.CharField(blank=True, max_length=255, verbose_name='自提点地址')),
                ('min_order_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='起购金额')),
                ('share_code', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='分享码')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='users.user', verbose_name='团长')),
            ],
            options={
                'verbose_name': '团购活动',
                'verbose_name_plural': '团购活动',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ActivityProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='团购价')),
                ('limit_per_user', models.PositiveIntegerField(default=0, verbose_name='每人限购数量（0表示不限）')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否有效')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='activities.groupbuyactivity', verbose_name='所属活动')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='商品')),
                ('product_spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productspec', verbose_name='商品规格')),
            ],
            options={
                'verbose_name': '活动商品',
                'verbose_name_plural': '活动商品',
                'ordering': ['id'],
                'unique_together': {('activity', 'product_spec')},
            },
        ),
        migrations.CreateModel(
            name='GroupBuyJoin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200, verbose_name='商品名称')),
                ('spec_name', models.CharField(max_length=100, verbose_name='规格名称')),
                ('quantity', models.PositiveIntegerField(verbose_name='购买数量')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='接龙时间')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joins', to='activities.groupbuyactivity', verbose_name='所属活动')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '团购接龙',
                'verbose_name_plural': '团购接龙',
                'ordering': ['-created_at'],
            },
        ),
    ]
