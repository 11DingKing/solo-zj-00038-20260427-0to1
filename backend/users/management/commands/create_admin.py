from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '初始化测试用户账号'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            admin = User(
                username='admin',
                email='admin@example.com',
                role=User.ROLE_ADMIN,
                is_staff=True,
                is_superuser=True,
            )
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'管理员账号创建成功: admin / admin123 (role={admin.role}, is_superuser={admin.is_superuser})'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING(f'管理员账号已存在 (role={admin.role})'))

        if not User.objects.filter(username='leader').exists():
            leader = User(
                username='leader',
                email='leader@example.com',
                role=User.ROLE_LEADER,
                phone='13800138001',
                shop_name='邻里团购小铺',
                shop_address='幸福小区12栋101室',
                id_card='110101199001011234',
                leader_status=User.STATUS_APPROVED,
                is_staff=False,
                is_superuser=False,
            )
            leader.set_password('leader123')
            leader.save()
            self.stdout.write(self.style.SUCCESS(f'团长账号创建成功: leader / leader123 (role={leader.role}, leader_status={leader.leader_status}, is_leader={leader.is_leader})'))
        else:
            leader = User.objects.get(username='leader')
            if leader.leader_status != User.STATUS_APPROVED:
                leader.leader_status = User.STATUS_APPROVED
                leader.save()
                self.stdout.write(self.style.WARNING(f'团长账号已存在，已更新审核状态 (role={leader.role}, leader_status={leader.leader_status}, is_leader={leader.is_leader})'))
            else:
                self.stdout.write(self.style.WARNING(f'团长账号已存在 (role={leader.role}, leader_status={leader.leader_status}, is_leader={leader.is_leader})'))

        if not User.objects.filter(username='member').exists():
            member = User(
                username='member',
                email='member@example.com',
                role=User.ROLE_MEMBER,
                phone='13800138002',
                is_staff=False,
                is_superuser=False,
            )
            member.set_password('member123')
            member.save()
            self.stdout.write(self.style.SUCCESS(f'团员账号创建成功: member / member123 (role={member.role})'))
        else:
            member = User.objects.get(username='member')
            self.stdout.write(self.style.WARNING(f'团员账号已存在 (role={member.role})'))

        self.stdout.write(self.style.SUCCESS('\n所有测试账号初始化完成！'))
        self.stdout.write(self.style.WARNING('========================================'))
        self.stdout.write(self.style.WARNING('  管理员: admin / admin123'))
        self.stdout.write(self.style.WARNING('  团长:   leader / leader123 (已审核)'))
        self.stdout.write(self.style.WARNING('  团员:   member / member123'))
        self.stdout.write(self.style.WARNING('========================================'))
