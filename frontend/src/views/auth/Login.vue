<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <el-icon size="48" color="#FF6B6B"><ShoppingCart /></el-icon>
        <h1>社区团购接龙平台</h1>
        <p>让购物更便捷，让生活更美好</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="login-links">
          <router-link to="/register">还没有账号？立即注册</router-link>
        </div>
      </el-form>
      
      <div class="login-tips">
        <p>测试账号：</p>
        <p>管理员：admin / admin123</p>
        <p>团长：leader / leader123</p>
        <p>团长：tuanzhang001 / abc123</p>
        <p>团员：member / member123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/store/user'
import { ShoppingCart, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        
        const redirect = route.query.redirect as string
        if (redirect) {
          router.push(redirect)
        } else if (userStore.isAdmin) {
          router.push('/admin/dashboard')
        } else if (userStore.isLeader) {
          router.push('/leader/dashboard')
        } else {
          router.push('/activities')
        }
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    margin: 16px 0 8px;
    font-size: 24px;
    color: #333;
    font-weight: 600;
  }
  
  p {
    margin: 0;
    color: #999;
    font-size: 14px;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  border: none;
  
  &:hover {
    opacity: 0.9;
  }
}

.login-links {
  text-align: center;
  margin-top: 20px;
  
  a {
    color: #FF6B6B;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.login-tips {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #eee;
  text-align: center;
  
  p {
    margin: 4px 0;
    font-size: 12px;
    color: #999;
  }
}
</style>