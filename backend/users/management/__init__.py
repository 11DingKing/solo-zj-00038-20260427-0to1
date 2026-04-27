from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, ProductSpec

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the database with default data'

    def handle(self, *args, **options):
        self.stdout.write('Creating default users...')
        
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': User.ROLE_ADMIN,
                'phone': '13800138000',
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        leader, created = User.objects.get_or_create(
            username='leader',
            defaults={
                'email': 'leader@example.com',
                'role': User.ROLE_LEADER,
                'phone': '13800138001',
                'leader_status': User.STATUS_APPROVED,
                'shop_name': '新鲜果蔬店',
                'shop_address': '北京市朝阳区建国路88号',
            }
        )
        if created:
            leader.set_password('leader123')
            leader.save()
            self.stdout.write(self.style.SUCCESS('Leader user created: leader / leader123'))
        else:
            self.stdout.write(self.style.WARNING('Leader user already exists'))
        
        member, created = User.objects.get_or_create(
            username='member',
            defaults={
                'email': 'member@example.com',
                'role': User.ROLE_MEMBER,
                'phone': '13800138002',
            }
        )
        if created:
            member.set_password('member123')
            member.save()
            self.stdout.write(self.style.SUCCESS('Member user created: member / member123'))
        else:
            self.stdout.write(self.style.WARNING('Member user already exists'))
        
        self.stdout.write('\nCreating default products...')
        
        products_data = [
            {
                'name': '新鲜苹果',
                'description': '来自山东烟台的红富士苹果，果肉脆甜多汁，果香浓郁。精选优质果实，个大饱满，新鲜采摘，品质保证。',
                'specs': [
                    {'name': '500g装', 'price': 12.90, 'stock': 100},
                    {'name': '1kg装', 'price': 22.90, 'stock': 50},
                    {'name': '2kg礼盒装', 'price': 45.90, 'stock': 30},
                ]
            },
            {
                'name': '有机草莓',
                'description': '奶油草莓，新鲜采摘，香甜可口，果肉细嫩多汁，果香浓郁。无农药残留，安全健康。',
                'specs': [
                    {'name': '300g装', 'price': 19.90, 'stock': 80},
                    {'name': '500g装', 'price': 29.90, 'stock': 60},
                ]
            },
            {
                'name': '农家土鸡蛋',
                'description': '来自农村散养土鸡，鸡蛋个大饱满，蛋黄颜色鲜亮，营养丰富，口感香醇。',
                'specs': [
                    {'name': '10枚装', 'price': 25.00, 'stock': 200},
                    {'name': '20枚装', 'price': 45.00, 'stock': 100},
                    {'name': '30枚礼盒装', 'price': 65.00, 'stock': 50},
                ]
            },
            {
                'name': '新鲜牛奶',
                'description': '巴氏杀菌鲜牛奶，每日新鲜配送，口感醇厚，营养丰富，适合全家饮用。',
                'specs': [
                    {'name': '250ml/盒', 'price': 3.50, 'stock': 500},
                    {'name': '1L/盒', 'price': 12.00, 'stock': 200},
                ]
            },
            {
                'name': '精品蔬菜包',
                'description': '当季新鲜蔬菜组合，包含多种绿叶菜和根茎类蔬菜，营养均衡，新鲜配送。',
                'specs': [
                    {'name': '2kg家庭装', 'price': 39.90, 'stock': 100},
                    {'name': '4kg超值装', 'price': 69.90, 'stock': 50},
                ]
            },
            {
                'name': '进口车厘子',
                'description': '智利进口车厘子，果大饱满，果肉脆甜，色泽鲜红，品质上乘。',
                'specs': [
                    {'name': '500g装', 'price': 58.00, 'stock': 40},
                    {'name': '1kg装', 'price': 99.00, 'stock': 30},
                    {'name': '2kg礼盒装', 'price': 188.00, 'stock': 20},
                ]
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                }
            )
            if created:
                for spec_data in product_data['specs']:
                    ProductSpec.objects.create(
                        product=product,
                        name=spec_data['name'],
                        price=spec_data['price'],
                        stock=spec_data['stock'],
                    )
                self.stdout.write(self.style.SUCCESS(f'Product created: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
        
        self.stdout.write('\n' + self.style.SUCCESS('Initialization completed!'))
        self.stdout.write(self.style.SUCCESS('Test accounts:'))
        self.stdout.write('  - Admin: admin / admin123')
        self.stdout.write('  - Leader: leader / leader123')
        self.stdout.write('  - Member: member / member123')
