import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/activities',
    children: [
      {
        path: 'activities',
        name: 'Activities',
        component: () => import('@/views/member/ActivityList.vue'),
        meta: { requiresAuth: true, title: '团购活动' }
      },
      {
        path: 'activities/:id',
        name: 'ActivityDetail',
        component: () => import('@/views/member/ActivityDetail.vue'),
        meta: { requiresAuth: true, title: '活动详情' }
      },
      {
        path: 'orders',
        name: 'MemberOrders',
        component: () => import('@/views/member/OrderList.vue'),
        meta: { requiresAuth: true, title: '我的订单' }
      },
      {
        path: 'orders/:id',
        name: 'MemberOrderDetail',
        component: () => import('@/views/member/OrderDetail.vue'),
        meta: { requiresAuth: true, title: '订单详情' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/common/Profile.vue'),
        meta: { requiresAuth: true, title: '个人中心' }
      }
    ]
  },
  {
    path: '/leader',
    component: () => import('@/layouts/LeaderLayout.vue'),
    redirect: '/leader/dashboard',
    meta: { requiresAuth: true, requiresLeader: true },
    children: [
      {
        path: 'dashboard',
        name: 'LeaderDashboard',
        component: () => import('@/views/leader/Dashboard.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'activities',
        name: 'LeaderActivities',
        component: () => import('@/views/leader/ActivityList.vue'),
        meta: { title: '团购管理' }
      },
      {
        path: 'activities/create',
        name: 'CreateActivity',
        component: () => import('@/views/leader/ActivityCreate.vue'),
        meta: { title: '发起团购' }
      },
      {
        path: 'activities/:id',
        name: 'LeaderActivityDetail',
        component: () => import('@/views/leader/ActivityDetail.vue'),
        meta: { title: '活动详情' }
      },
      {
        path: 'orders',
        name: 'LeaderOrders',
        component: () => import('@/views/leader/OrderList.vue'),
        meta: { title: '订单管理' }
      },
      {
        path: 'orders/:id',
        name: 'LeaderOrderDetail',
        component: () => import('@/views/leader/OrderDetail.vue'),
        meta: { title: '订单详情' }
      },
      {
        path: 'refunds',
        name: 'LeaderRefunds',
        component: () => import('@/views/leader/RefundList.vue'),
        meta: { title: '退款管理' }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('@/views/admin/ProductList.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'products/create',
        name: 'CreateProduct',
        component: () => import('@/views/admin/ProductCreate.vue'),
        meta: { title: '添加商品' }
      },
      {
        path: 'products/:id/edit',
        name: 'EditProduct',
        component: () => import('@/views/admin/ProductEdit.vue'),
        meta: { title: '编辑商品' }
      },
      {
        path: 'leaders',
        name: 'LeaderApproval',
        component: () => import('@/views/admin/LeaderApproval.vue'),
        meta: { title: '团长审核' }
      }
    ]
  },
  {
    path: '/share/:code',
    name: 'ShareActivity',
    component: () => import('@/views/member/ActivityShare.vue'),
    meta: { requiresAuth: false, title: '团购分享' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  userStore.initFromStorage()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresAuth && userStore.isLoggedIn && !userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      userStore.logout()
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  if (to.meta.requiresLeader && !userStore.isLeader) {
    next({ name: 'Activities' })
    return
  }

  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Activities' })
    return
  }

  next()
})

export default router