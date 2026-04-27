<template>
  <div class="profile-page">
    <div class="profile-header" v-if="userStore.userInfo">
      <div class="user-info">
        <el-avatar :size="64" class="user-avatar">
          {{ userStore.userInfo.username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
        <div class="user-detail">
          <h2 class="user-name">{{ userStore.userInfo.username }}</h2>
          <p class="user-email">{{ userStore.userInfo.email }}</p>
          <div class="user-roles">
            <el-tag v-if="userStore.isAdmin" type="danger" size="small"
              >管理员</el-tag
            >
            <el-tag v-else-if="userStore.isLeader" type="success" size="small">
              团长
              <span
                v-if="userStore.userInfo.leader_status === 'pending'"
                class="status-badge"
              >
                (审核中)
              </span>
              <span
                v-else-if="userStore.userInfo.leader_status === 'rejected'"
                class="status-badge rejected"
              >
                (审核未通过)
              </span>
            </el-tag>
            <el-tag v-else type="primary" size="small">团员</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div class="order-card">
      <div class="card-header">
        <span class="card-title">我的订单</span>
        <el-button type="primary" text @click="goToOrders">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="order-status">
        <div class="status-item" @click="goToOrdersWithStatus('pending')">
          <div class="status-icon">
            <el-icon :size="28"><Coin /></el-icon>
            <el-badge
              v-if="orderCount.pending > 0"
              :value="orderCount.pending"
              class="badge"
            />
          </div>
          <span class="status-label">待付款</span>
        </div>
        <div class="status-item" @click="goToOrdersWithStatus('paid')">
          <div class="status-icon">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <span class="status-label">已付款</span>
        </div>
        <div class="status-item" @click="goToOrdersWithStatus('delivering')">
          <div class="status-icon">
            <el-icon :size="28"><ShoppingCart /></el-icon>
          </div>
          <span class="status-label">待收货</span>
        </div>
        <div class="status-item" @click="goToOrdersWithStatus('completed')">
          <div class="status-icon">
            <el-icon :size="28"><Ticket /></el-icon>
          </div>
          <span class="status-label">已完成</span>
        </div>
        <div class="status-item" @click="goToOrdersWithStatus('refund')">
          <div class="status-icon">
            <el-icon :size="28"><Warning /></el-icon>
            <el-badge
              v-if="orderCount.refunding > 0"
              :value="orderCount.refunding"
              class="badge"
            />
          </div>
          <span class="status-label">退款/售后</span>
        </div>
      </div>
    </div>

    <div class="menu-section">
      <div class="menu-card">
        <div class="menu-group" v-if="userStore.isLeader">
          <div class="menu-item" @click="goToLeaderDashboard">
            <el-icon :size="22" color="#67C23A"><DataAnalysis /></el-icon>
            <span class="menu-label">团长后台</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="menu-group" v-if="userStore.isAdmin">
          <div class="menu-item" @click="goToAdminDashboard">
            <el-icon :size="22" color="#F56C6C"><Setting /></el-icon>
            <span class="menu-label">管理后台</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="menu-group">
          <div class="menu-item" @click="showEditProfile">
            <el-icon :size="22" color="#409EFF"><User /></el-icon>
            <span class="menu-label">个人资料</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="menu-item" @click="showChangePassword">
            <el-icon :size="22" color="#E6A23C"><Lock /></el-icon>
            <span class="menu-label">修改密码</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="menu-group">
          <div class="menu-item" @click="handleLogout">
            <el-icon :size="22" color="#909399"><SwitchButton /></el-icon>
            <span class="menu-label">退出登录</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="editProfileVisible" title="编辑个人资料" width="420px">
      <el-form :model="profileForm" :rules="profileRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item
          label="店铺名称"
          prop="shop_name"
          v-if="userStore.isLeader"
        >
          <el-input
            v-model="profileForm.shop_name"
            placeholder="请输入店铺名称"
          />
        </el-form-item>
        <el-form-item
          label="店铺地址"
          prop="shop_address"
          v-if="userStore.isLeader"
        >
          <el-input
            v-model="profileForm.shop_address"
            type="textarea"
            :rows="2"
            placeholder="请输入店铺地址"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitProfile">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="changePasswordVisible" title="修改密码" width="420px">
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        ref="passwordFormRef"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入旧密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitPassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { useUserStore } from "@/store/user";
import { userApi, orderApi } from "@/api";
import type { Order, PaginatedResponse } from "@/types";
import {
  ArrowRight,
  Coin,
  CircleCheck,
  ShoppingCart,
  Ticket,
  Warning,
  DataAnalysis,
  Setting,
  User,
  Lock,
  SwitchButton,
} from "@element-plus/icons-vue";

const router = useRouter();
const userStore = useUserStore();

const editProfileVisible = ref(false);
const changePasswordVisible = ref(false);
const submitting = ref(false);
const passwordFormRef = ref<FormInstance>();

const orderCount = reactive({
  pending: 0,
  paid: 0,
  delivering: 0,
  completed: 0,
  refunding: 0,
});

const profileForm = reactive({
  username: "",
  email: "",
  phone: "",
  shop_name: "",
  shop_address: "",
});

const profileRules: FormRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 2, max: 20, message: "用户名长度为 2-20 个字符", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号",
      trigger: "blur",
    },
  ],
};

const passwordForm = reactive({
  old_password: "",
  new_password: "",
  confirm_password: "",
});

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.new_password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const passwordRules: FormRules = {
  old_password: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  new_password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于 6 个字符", trigger: "blur" },
  ],
  confirm_password: [
    { required: true, message: "请再次输入新密码", trigger: "blur" },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
};

const fetchOrderCount = async () => {
  try {
    const [pendingRes, paidRes, deliveringRes, refundingRes] =
      await Promise.all([
        orderApi.getMyOrders({ page: 1, page_size: 1, status: "pending" }),
        orderApi.getMyOrders({ page: 1, page_size: 1, status: "paid" }),
        orderApi.getMyOrders({ page: 1, page_size: 1, status: "delivering" }),
        orderApi.getMyOrders({ page: 1, page_size: 1, status: "refunding" }),
      ]);

    orderCount.pending = pendingRes.count;
    orderCount.paid = paidRes.count;
    orderCount.delivering = deliveringRes.count;
    orderCount.refunding = refundingRes.count;
  } catch (error) {
    console.error("获取订单数量失败:", error);
  }
};

const showEditProfile = () => {
  if (userStore.userInfo) {
    profileForm.username = userStore.userInfo.username;
    profileForm.email = userStore.userInfo.email;
    profileForm.phone = userStore.userInfo.phone || "";
    profileForm.shop_name = userStore.userInfo.shop_name || "";
    profileForm.shop_address = userStore.userInfo.shop_address || "";
  }
  editProfileVisible.value = true;
};

const showChangePassword = () => {
  passwordForm.old_password = "";
  passwordForm.new_password = "";
  passwordForm.confirm_password = "";
  changePasswordVisible.value = true;
};

const submitProfile = async () => {
  submitting.value = true;
  try {
    const data: any = {
      username: profileForm.username,
      email: profileForm.email,
      phone: profileForm.phone,
    };

    if (userStore.isLeader) {
      data.shop_name = profileForm.shop_name;
      data.shop_address = profileForm.shop_address;
    }

    await userApi.updateProfile(data);
    await userStore.fetchUserInfo();
    ElMessage.success("保存成功");
    editProfileVisible.value = false;
  } catch (error: any) {
    const errors = error.response?.data;
    if (errors) {
      const errorMessages = Object.values(errors).flat().join("; ");
      ElMessage.error(errorMessages || "保存失败");
    } else {
      ElMessage.error("保存失败");
    }
  } finally {
    submitting.value = false;
  }
};

const submitPassword = async () => {
  if (!passwordFormRef.value) return;

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        ElMessage.success("密码修改成功");
        changePasswordVisible.value = false;
      } catch (error) {
        ElMessage.error("密码修改失败");
      } finally {
        submitting.value = false;
      }
    }
  });
};

const goToOrders = () => {
  router.push("/orders");
};

const goToOrdersWithStatus = (status: string) => {
  router.push({ path: "/orders", query: { status } });
};

const goToLeaderDashboard = () => {
  router.push("/leader/dashboard");
};

const goToAdminDashboard = () => {
  router.push("/admin/dashboard");
};

const handleLogout = () => {
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
};

onMounted(() => {
  fetchOrderCount();
});
</script>

<style lang="scss" scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 20px;

  .profile-header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
    padding: 24px 20px;
    border-radius: 0 0 16px 16px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 16px;

      .user-avatar {
        background: #fff;
        color: #ff6b6b;
        font-size: 28px;
        font-weight: 600;
        flex-shrink: 0;
      }

      .user-detail {
        flex: 1;

        .user-name {
          font-size: 20px;
          font-weight: 600;
          color: #fff;
          margin: 0 0 4px;
        }

        .user-email {
          font-size: 13px;
          color: rgba(255, 255, 255, 0.8);
          margin: 0 0 8px;
        }

        .user-roles {
          display: flex;
          gap: 8px;

          .status-badge {
            font-size: 11px;
            opacity: 0.9;

            &.rejected {
              color: #f56c6c;
            }
          }
        }
      }
    }
  }

  .order-card {
    background: #fff;
    border-radius: 12px;
    margin: 16px;
    padding: 16px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }

    .order-status {
      display: flex;
      justify-content: space-around;

      .status-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;

        .status-icon {
          position: relative;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #666;

          .badge {
            position: absolute;
            top: 0;
            right: 0;
          }
        }

        .status-label {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
        }

        &:hover {
          .status-icon {
            color: #ff6b6b;
          }
        }
      }
    }
  }

  .menu-section {
    padding: 0 16px;

    .menu-card {
      background: #fff;
      border-radius: 12px;
      overflow: hidden;

      .menu-group {
        &:not(:last-child) {
          border-bottom: 1px solid #f0f0f0;
        }

        .menu-item {
          display: flex;
          align-items: center;
          padding: 16px;
          cursor: pointer;
          transition: background 0.2s;

          &:hover {
            background: #fafafa;
          }

          .menu-label {
            flex: 1;
            font-size: 15px;
            color: #333;
            margin-left: 12px;
          }

          .el-icon:last-child {
            color: #ccc;
          }
        }
      }
    }
  }
}
</style>
