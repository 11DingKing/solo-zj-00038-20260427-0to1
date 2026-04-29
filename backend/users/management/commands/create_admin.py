from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '创建管理员账号 admin/admin123'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('管理员账号已存在'))
            return

        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role=User.ROLE_ADMIN,
        )
        self.stdout.write(self.style.SUCCESS('管理员账号创建成功: admin / admin123'))
