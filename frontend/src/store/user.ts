import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { request } from '@/utils/request'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const userInfo = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => {
    if (userInfo.value?.is_admin === true) return true
    if (userInfo.value?.role === 'admin') return true
    return false
  })
  const isLeader = computed(() => {
    if (userInfo.value?.is_leader === true) return true
    if (userInfo.value?.role === 'leader' && userInfo.value?.leader_status === 'approved') return true
    return false
  })
  const isMember = computed(() => {
    if (userInfo.value?.role === 'member') return true
    if (!isAdmin.value && !isLeader.value) return true
    return false
  })

  async function login(username: string, password: string) {
    const res = await request.post<{
      access: string
      refresh: string
      user: User
    }>('/users/login/', { username, password })

    token.value = res.access
    refreshToken.value = res.refresh
    userInfo.value = res.user

    localStorage.setItem('token', res.access)
    localStorage.setItem('refreshToken', res.refresh)
    localStorage.setItem('userInfo', JSON.stringify(res.user))

    return res
  }

  async function register(data: {
    username: string
    email: string
    password: string
    password_confirm: string
    role: 'admin' | 'leader' | 'member'
    phone?: string
    shop_name?: string
    shop_address?: string
    id_card?: string
  }) {
    return await request.post('/users/', data)
  }

  async function fetchUserInfo() {
    if (!token.value) return null
    
    try {
      const res = await request.get<User>('/users/profile/')
      userInfo.value = res
      localStorage.setItem('userInfo', JSON.stringify(res))
      return res
    } catch (error) {
      logout()
      return null
    }
  }

  async function refreshTokens() {
    if (!refreshToken.value) {
      logout()
      return false
    }

    try {
      const res = await request.post<{
        access: string
      }>('/token/refresh/', {
        refresh: refreshToken.value
      })

      token.value = res.access
      localStorage.setItem('token', res.access)
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')

    router.push('/login')
  }

  function initFromStorage() {
    const savedUserInfo = localStorage.getItem('userInfo')
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch {
        userInfo.value = null
      }
    }
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    isAdmin,
    isLeader,
    isMember,
    login,
    register,
    fetchUserInfo,
    refreshTokens,
    logout,
    initFromStorage
  }
})