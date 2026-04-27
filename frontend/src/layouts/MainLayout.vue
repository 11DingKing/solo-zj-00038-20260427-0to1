<template>
  <div class="main-layout">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="goHome">
          <el-icon size="28" color="#FF6B6B"><ShoppingCart /></el-icon>
          <span class="logo-text">社区团购</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="header-menu"
          mode="horizontal"
          background-color="transparent"
          text-color="#333"
          active-text-color="#FF6B6B"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/activities">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>团购活动</span>
            </template>
          </el-menu-item>
          <el-menu-item index="/orders">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>我的订单</span>
            </template>
          </el-menu-item>
        </el-menu>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ userStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isLeader" command="leader">
                  <el-icon><Shop /></el-icon>
                  团长后台
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isAdmin" command="admin">
                  <el-icon><Setting /></el-icon>
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
    
    <el-footer class="footer">
      <p>© 2024 社区团购接龙平台 - 让购物更便捷</p>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ShoppingCart, Goods, Document, ArrowDown, User,
  Shop, Setting, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/activities')) return '/activities'
  if (path.startsWith('/orders')) return '/orders'
  return '/activities'
})

const goHome = () => {
  router.push('/activities')
}

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'leader':
      if (userStore.isLeader) {
        router.push('/leader/dashboard')
      }
      break
    case 'admin':
      if (userStore.isAdmin) {
        router.push('/admin/dashboard')
      }
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        userStore.logout()
        ElMessage.success('已退出登录')
      }).catch(() => {})
      break
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 64px !important;
  line-height: 64px;
  
  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
  }
  
  .logo {
    display: flex;
    align-items: center;
    cursor: pointer;
    
    .logo-text {
      margin-left: 8px;
      font-size: 20px;
      font-weight: 600;
      color: #333;
    }
  }
  
  .header-menu {
    flex: 1;
    margin-left: 40px;
    border-bottom: none;
    
    .el-menu-item {
      height: 64px;
      line-height: 64px;
      border-bottom: none;
      
      &:hover, &.is-active {
        background-color: transparent;
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    
    .user-dropdown {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .user-avatar {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: #fff;
        font-weight: 600;
      }
      
      .user-name {
        margin: 0 8px;
        color: #333;
        font-size: 14px;
      }
    }
  }
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
  box-sizing: border-box;
}

.footer {
  background-color: #fff;
  border-top: 1px solid #eee;
  text-align: center;
  padding: 20px 0;
  color: #999;
  font-size: 14px;
  
  p {
    margin: 0;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>