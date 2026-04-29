from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '初始化测试用户账号'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role=User.ROLE_ADMIN,
            )
            self.stdout.write(self.style.SUCCESS('管理员账号创建成功: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('管理员账号已存在'))

        if not User.objects.filter(username='leader').exists():
            leader = User.objects.create_user(
                username='leader',
                email='leader@example.com',
                password='leader123',
                role=User.ROLE_LEADER,
                phone='13800138001',
                shop_name='邻里团购小铺',
                shop_address='幸福小区12栋101室',
                id_card='110101199001011234',
                leader_status=User.STATUS_APPROVED,
            )
            self.stdout.write(self.style.SUCCESS('团长账号创建成功: leader / leader123 (已审核)'))
        else:
            self.stdout.write(self.style.WARNING('团长账号已存在'))

        if not User.objects.filter(username='tuanzhang001').exists():
            leader = User.objects.create_user(
                username='tuanzhang001',
                email='tuanzhang001@example.com',
                password='abc123',
                role=User.ROLE_LEADER,
                phone='13800138003',
                shop_name='团长优选',
                shop_address='阳光小区8栋202室',
                id_card='110101199001015678',
                leader_status=User.STATUS_APPROVED,
            )
            self.stdout.write(self.style.SUCCESS('团长账号创建成功: tuanzhang001 / abc123 (已审核)'))
        else:
            leader = User.objects.filter(username='tuanzhang001').first()
            if leader and leader.leader_status != User.STATUS_APPROVED:
                leader.leader_status = User.STATUS_APPROVED
                leader.save()
                self.stdout.write(self.style.SUCCESS('团长账号 tuanzhang001 已审核通过'))
            else:
                self.stdout.write(self.style.WARNING('团长账号 tuanzhang001 已存在'))

        if not User.objects.filter(username='member').exists():
            User.objects.create_user(
                username='member',
                email='member@example.com',
                password='member123',
                role=User.ROLE_MEMBER,
                phone='13800138002',
            )
            self.stdout.write(self.style.SUCCESS('团员账号创建成功: member / member123'))
        else:
            self.stdout.write(self.style.WARNING('团员账号已存在'))

        self.stdout.write(self.style.SUCCESS('\n所有测试账号初始化完成！'))
        self.stdout.write(self.style.WARNING('========================================'))
        self.stdout.write(self.style.WARNING('  管理员: admin / admin123'))
        self.stdout.write(self.style.WARNING('  团长:   leader / leader123 (已审核)'))
        self.stdout.write(self.style.WARNING('  团长:   tuanzhang001 / abc123 (已审核)'))
        self.stdout.write(self.style.WARNING('  团员:   member / member123'))
        self.stdout.write(self.style.WARNING('========================================'))
