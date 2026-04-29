from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='商品名称')),
                ('image', models.ImageField(upload_to='products/', verbose_name='商品图片')),
                ('description', models.TextField(verbose_name='商品描述')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否上架')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductSpec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='规格名称')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='库存')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否有效')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='products.product', verbose_name='所属商品')),
            ],
            options={
                'verbose_name': '商品规格',
                'verbose_name_plural': '商品规格',
                'ordering': ['id'],
            },
        ),
    ]
