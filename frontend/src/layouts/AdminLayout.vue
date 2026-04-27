<template>
  <div class="admin-layout">
    <el-container>
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="sidebar-header">
          <el-icon size="28" color="#409EFF"><Setting /></el-icon>
          <span v-show="!isCollapse" class="sidebar-title">管理后台</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据统计</template>
          </el-menu-item>

          <el-menu-item index="/admin/products">
            <el-icon><Goods /></el-icon>
            <template #title>商品管理</template>
          </el-menu-item>

          <el-menu-item index="/admin/leaders">
            <el-icon><UserFilled /></el-icon>
            <template #title>团长审核</template>
            <el-badge
              v-if="pendingLeaderCount > 0"
              :value="pendingLeaderCount"
              class="badge"
              is-dot
            />
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <el-button
            text
            type="info"
            :icon="isCollapse ? 'Expand' : 'Fold'"
            @click="isCollapse = !isCollapse"
            class="collapse-btn"
          />
        </div>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-content">
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item :to="{ path: '/admin/dashboard' }"
                >管理后台</el-breadcrumb-item
              >
              <el-breadcrumb-item v-if="currentPageTitle">{{
                currentPageTitle
              }}</el-breadcrumb-item>
            </el-breadcrumb>

            <div class="header-right">
              <el-dropdown @command="handleCommand">
                <span class="user-dropdown">
                  <el-avatar :size="32" class="user-avatar">
                    {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <span class="user-name">{{
                    userStore.userInfo?.username
                  }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="member">
                      <el-icon><ShoppingCart /></el-icon>
                      返回首页
                    </el-dropdown-item>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      个人中心
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
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox, ElMessage } from "element-plus";
import { useUserStore } from "@/store/user";
import { userApi } from "@/api";
import {
  Setting,
  DataAnalysis,
  Goods,
  UserFilled,
  ShoppingCart,
  User,
  ArrowDown,
  SwitchButton,
  Fold,
  Expand,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);
const pendingLeaderCount = ref(0);

const pageTitleMap: Record<string, string> = {
  "/admin/dashboard": "数据统计",
  "/admin/products": "商品管理",
  "/admin/products/create": "添加商品",
  "/admin/leaders": "团长审核",
};

const activeMenu = computed(() => {
  const path = route.path;
  if (path.startsWith("/admin/products")) return "/admin/products";
  if (path.startsWith("/admin/leaders")) return "/admin/leaders";
  return path;
});

const currentPageTitle = computed(() => {
  const path = route.path;
  for (const [key, title] of Object.entries(pageTitleMap)) {
    if (path === key || path.startsWith(key + "/")) {
      return title;
    }
  }
  return "";
});

const fetchPendingLeaders = async () => {
  try {
    const leaders = await userApi.getPendingLeaders();
    pendingLeaderCount.value = leaders.length;
  } catch (error) {
    console.error("获取待审核团长列表失败:", error);
  }
};

const handleCommand = (command: string) => {
  switch (command) {
    case "member":
      router.push("/activities");
      break;
    case "profile":
      router.push("/profile");
      break;
    case "logout":
      ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          userStore.logout();
          ElMessage.success("已退出登录");
        })
        .catch(() => {});
      break;
  }
};

onMounted(() => {
  fetchPendingLeaders();
});
</script>

<style lang="scss" scoped>
.admin-layout {
  height: 100vh;

  .sidebar {
    background-color: #304156;
    display: flex;
    flex-direction: column;
    transition: width 0.3s;

    .sidebar-header {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      border-bottom: 1px solid #3a4a5f;

      .sidebar-title {
        color: #fff;
        font-size: 18px;
        font-weight: 600;
      }
    }

    .sidebar-menu {
      flex: 1;
      border-right: none;

      .el-menu-item {
        height: 50px;
        line-height: 50px;

        &:hover {
          background-color: #263445;
        }

        &.is-active {
          background-color: #409eff;
          color: #fff;

          .el-icon {
            color: #fff;
          }
        }
      }
    }

    .sidebar-footer {
      padding: 12px;
      border-top: 1px solid #3a4a5f;
      text-align: center;

      .collapse-btn {
        color: #bfcbd9;
        font-size: 20px;

        &:hover {
          color: #fff;
        }
      }
    }
  }

  .header {
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 0;
    height: 60px !important;
    line-height: 60px;

    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 100%;
      padding: 0 24px;

      .breadcrumb {
        .el-breadcrumb__item {
          font-size: 14px;

          .el-breadcrumb__inner {
            color: #666;
          }

          &:last-child .el-breadcrumb__inner {
            color: #333;
            font-weight: 500;
          }
        }
      }

      .header-right {
        .user-dropdown {
          display: flex;
          align-items: center;
          cursor: pointer;

          .user-avatar {
            background: linear-gradient(135deg, #409eff, #67c23a);
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
  }

  .main-content {
    background-color: #f5f7fa;
    padding: 24px;
  }
}

.badge {
  margin-left: 8px;
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
