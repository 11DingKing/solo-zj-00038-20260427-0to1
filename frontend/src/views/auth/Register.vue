<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <el-icon size="48" color="#FF6B6B"><ShoppingCart /></el-icon>
        <h1>用户注册</h1>
        <p>加入社区团购，享受便捷购物</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="registerForm.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="registerForm.role" size="large">
            <el-radio value="member">团员</el-radio>
            <el-radio value="leader">团长</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            size="large"
          />
        </el-form-item>
        
        <template v-if="registerForm.role === 'leader'">
          <el-form-item label="店铺名称" prop="shop_name">
            <el-input
              v-model="registerForm.shop_name"
              placeholder="请输入店铺名称"
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="店铺地址" prop="shop_address">
            <el-input
              v-model="registerForm.shop_address"
              type="textarea"
              :rows="2"
              placeholder="请输入店铺地址"
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="身份证号" prop="id_card">
            <el-input
              v-model="registerForm.id_card"
              placeholder="请输入身份证号"
              size="large"
            />
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-btn"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
        
        <div class="register-links">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/store/user'
import { ShoppingCart } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'member' as 'member' | 'leader',
  phone: '',
  shop_name: '',
  shop_address: '',
  id_card: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = computed<FormRules>(() => {
  const rules: FormRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 2, max: 20, message: '用户名长度为 2-20 个字符', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
    ],
    password_confirm: [
      { required: true, message: '请再次输入密码', trigger: 'blur' },
      { validator: validateConfirmPassword, trigger: 'blur' }
    ],
    role: [
      { required: true, message: '请选择角色', trigger: 'change' }
    ],
    phone: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
    ]
  }
  
  if (registerForm.role === 'leader') {
    rules.shop_name = [{ required: true, message: '请输入店铺名称', trigger: 'blur' }]
    rules.shop_address = [{ required: true, message: '请输入店铺地址', trigger: 'blur' }]
    rules.id_card = [
      { required: true, message: '请输入身份证号', trigger: 'blur' },
      { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
    ]
  }
  
  return rules
})

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          password_confirm: registerForm.password_confirm,
          role: registerForm.role,
          phone: registerForm.phone,
          shop_name: registerForm.shop_name || undefined,
          shop_address: registerForm.shop_address || undefined,
          id_card: registerForm.id_card || undefined
        })
        
        ElMessage.success(
          registerForm.role === 'leader' 
            ? '注册成功！请等待管理员审核' 
            : '注册成功！请登录'
        )
        
        router.push('/login')
      } catch (error: any) {
        const errors = error.response?.data
        if (errors) {
          const errorMessages = Object.values(errors).flat().join('; ')
          ElMessage.error(errorMessages || '注册失败')
        } else {
          ElMessage.error('注册失败，请稍后重试')
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  padding: 40px 20px;
}

.register-container {
  width: 100%;
  max-width: 520px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 40px;
}

.register-header {
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

.register-form {
  .el-form-item {
    margin-bottom: 20px;
  }
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  border: none;
  margin-top: 10px;
  
  &:hover {
    opacity: 0.9;
  }
}

.register-links {
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
</style>