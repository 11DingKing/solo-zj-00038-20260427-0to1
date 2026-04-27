<template>
  <div class="leader-layout">
    <el-container>
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="sidebar-header">
          <el-icon size="28" color="#FF6B6B"><Shop /></el-icon>
          <span v-show="!isCollapse" class="sidebar-title">团长后台</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#FF6B6B"
          router
        >
          <el-menu-item index="/leader/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据统计</template>
          </el-menu-item>

          <el-menu-item index="/leader/activities">
            <el-icon><Goods /></el-icon>
            <template #title>团购管理</template>
          </el-menu-item>

          <el-menu-item index="/leader/orders">
            <el-icon><Document /></el-icon>
            <template #title>订单管理</template>
          </el-menu-item>

          <el-menu-item index="/leader/refunds">
            <el-icon><Wallet /></el-icon>
            <template #title>退款管理</template>
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
              <el-breadcrumb-item :to="{ path: '/leader/dashboard' }"
                >团长后台</el-breadcrumb-item
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
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox, ElMessage } from "element-plus";
import { useUserStore } from "@/store/user";
import {
  Shop,
  DataAnalysis,
  Goods,
  Document,
  Wallet,
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

const pageTitleMap: Record<string, string> = {
  "/leader/dashboard": "数据统计",
  "/leader/activities": "团购管理",
  "/leader/activities/create": "发起团购",
  "/leader/orders": "订单管理",
  "/leader/refunds": "退款管理",
};

const activeMenu = computed(() => {
  const path = route.path;
  if (path.startsWith("/leader/activities")) return "/leader/activities";
  if (path.startsWith("/leader/orders")) return "/leader/orders";
  if (path.startsWith("/leader/refunds")) return "/leader/refunds";
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
</script>

<style lang="scss" scoped>
.leader-layout {
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
          background-color: #ff6b6b;
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
            background: linear-gradient(135deg, #ff6b6b, #ff8e53);
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
