from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    LeaderApprovalSerializer, UserProfileSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsLeader, IsOwnerOrAdmin
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action == 'list':
            return [IsAdmin()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'approve_leader':
            return LeaderApprovalSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_leaders(self, request):
        if not request.user.is_admin:
            return Response(
                {'error': '只有管理员可以查看待审核团长列表'},
                status=status.HTTP_403_FORBIDDEN
            )
        pending_leaders = User.objects.filter(
            role=User.ROLE_LEADER,
            leader_status=User.STATUS_PENDING
        )
        serializer = self.get_serializer(pending_leaders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_leader(self, request, pk=None):
        if not request.user.is_admin:
            return Response(
                {'error': '只有管理员可以审核团长申请'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        if user.role != User.ROLE_LEADER:
            return Response(
                {'error': '该用户不是团长角色'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': '团长审核状态已更新',
            'user': UserSerializer(user).data
        })