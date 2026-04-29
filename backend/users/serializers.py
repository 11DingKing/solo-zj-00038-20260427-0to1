from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['username'] = user.username
        token['role'] = user.role
        token['is_leader'] = user.is_leader
        token['is_admin'] = user.is_admin
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'phone': self.user.phone,
            'is_leader': self.user.is_leader,
            'is_admin': self.user.is_admin,
            'leader_status': self.user.leader_status if self.user.role == User.ROLE_LEADER else None,
            'shop_name': self.user.shop_name,
            'shop_address': self.user.shop_address,
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    leader_status_display = serializers.CharField(source='get_leader_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'role', 'role_display',
            'phone', 'avatar', 'leader_status', 'leader_status_display',
            'shop_name', 'shop_address', 'id_card', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'leader_status']
        extra_kwargs = {
            'password': {'write_only': True},
            'id_card': {'write_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        
        if user.role == User.ROLE_LEADER:
            user.leader_status = User.STATUS_PENDING
        
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'role', 'phone', 'shop_name', 'shop_address', 'id_card'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
            'id_card': {'write_only': True},
        }
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        
        if data['role'] == User.ROLE_LEADER:
            if not data.get('shop_name') or not data.get('shop_address') or not data.get('id_card'):
                raise serializers.ValidationError("申请团长需要填写店铺名称、地址和身份证号")
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        
        if user.role == User.ROLE_LEADER:
            user.leader_status = User.STATUS_PENDING
        
        user.save()
        return user


class LeaderApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'leader_status']
        read_only_fields = ['id']
    
    def validate_leader_status(self, value):
        if value not in [User.STATUS_APPROVED, User.STATUS_REJECTED]:
            raise serializers.ValidationError("审核状态只能是通过或拒绝")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    leader_status_display = serializers.CharField(source='get_leader_status_display', read_only=True)
    is_leader = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'role_display',
            'phone', 'avatar', 'leader_status', 'leader_status_display',
            'shop_name', 'shop_address', 'created_at',
            'is_leader', 'is_admin',
        ]
        read_only_fields = ['id', 'created_at', 'role', 'leader_status']
    
    def get_is_leader(self, obj):
        return obj.is_leader
    
    def get_is_admin(self, obj):
        return obj.is_admin