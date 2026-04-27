<template>
  <div class="admin-leader-approval">
    <div class="page-header">
      <h2>团长审核</h2>
      <div class="header-stats">
        <el-tag type="warning" v-if="pendingCount > 0">
          待审核: {{ pendingCount }} 人
        </el-tag>
      </div>
    </div>

    <div class="leader-list" v-loading="loading">
      <el-empty
        v-if="leaders.length === 0 && !loading"
        description="暂无待审核的团长申请"
      />

      <div v-for="leader in leaders" :key="leader.id" class="leader-card">
        <div class="card-header">
          <div class="user-info">
            <el-avatar :size="48" class="user-avatar">
              {{ leader.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div class="user-detail">
              <h3 class="user-name">{{ leader.username }}</h3>
              <p class="user-email">{{ leader.email }}</p>
              <p class="user-phone">{{ leader.phone }}</p>
            </div>
          </div>
          <el-tag
            :type="getLeaderStatusTag(leader.leader_status).type"
            size="large"
          >
            {{ getLeaderStatusTag(leader.leader_status).text }}
          </el-tag>
        </div>

        <div class="card-content">
          <div class="info-row">
            <span class="label">店铺名称:</span>
            <span class="value">{{ leader.shop_name || "未填写" }}</span>
          </div>
          <div class="info-row">
            <span class="label">店铺地址:</span>
            <span class="value">{{ leader.shop_address || "未填写" }}</span>
          </div>
        </div>

        <div class="card-actions" v-if="leader.leader_status === 'pending'">
          <el-button type="success" size="large" @click="approveLeader(leader)">
            <el-icon><CircleCheck /></el-icon>
            通过审核
          </el-button>
          <el-button type="danger" size="large" @click="rejectLeader(leader)">
            <el-icon><CircleClose /></el-icon>
            拒绝申请
          </el-button>
        </div>

        <div class="card-actions" v-else>
          <span class="processed-time">
            处理时间: {{ formatDate(leader.created_at) }}
          </span>
        </div>
      </div>
    </div>

    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type ElMessageBoxOptions,
} from "element-plus";
import { userApi } from "@/api";
import { formatDate, getLeaderStatusTag } from "@/utils";
import type { User, PaginatedResponse } from "@/types";
import { CircleCheck, CircleClose } from "@element-plus/icons-vue";

const loading = ref(false);
const leaders = ref<User[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const pendingCount = computed(() => {
  return leaders.value.filter((l) => l.leader_status === "pending").length;
});

const fetchLeaders = async () => {
  loading.value = true;
  try {
    const res: PaginatedResponse<User> = await userApi.getUsers({
      page: currentPage.value,
      page_size: pageSize.value,
      role: "leader",
    });
    leaders.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取团长列表失败:", error);
    ElMessage.error("获取团长列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchLeaders();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchLeaders();
};

const approveLeader = async (leader: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过团长「${leader.username}」的申请吗？`,
      "提示",
      {
        confirmButtonText: "确定通过",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await userApi.approveLeader(leader.id, "approved");
    ElMessage.success("审核通过");
    fetchLeaders();
  } catch (error) {
    // 用户取消
  }
};

const rejectLeader = async (leader: User) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      "请输入拒绝原因",
      "拒绝申请",
      {
        confirmButtonText: "确认拒绝",
        cancelButtonText: "取消",
        inputPlaceholder: "请输入拒绝原因",
      } as ElMessageBoxOptions,
    );

    await userApi.approveLeader(leader.id, "rejected");
    ElMessage.success("已拒绝申请");
    fetchLeaders();
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  fetchLeaders();
});
</script>

<style lang="scss" scoped>
.admin-leader-approval {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .leader-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .leader-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;

      .user-info {
        display: flex;
        gap: 16px;

        .user-avatar {
          background: linear-gradient(135deg, #409eff, #67c23a);
          color: #fff;
          font-size: 20px;
          font-weight: 600;
          flex-shrink: 0;
        }

        .user-detail {
          .user-name {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin: 0 0 4px;
          }

          .user-email,
          .user-phone {
            font-size: 13px;
            color: #999;
            margin: 0 0 2px;
          }
        }
      }
    }

    .card-content {
      padding: 16px;
      background: #fafafa;
      border-radius: 8px;
      margin-bottom: 20px;

      .info-row {
        display: flex;
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }

        .label {
          width: 80px;
          font-size: 14px;
          color: #999;
          flex-shrink: 0;
        }

        .value {
          font-size: 14px;
          color: #333;
          flex: 1;
        }
      }
    }

    .card-actions {
      display: flex;
      gap: 16px;
      justify-content: flex-end;

      .processed-time {
        font-size: 13px;
        color: #999;
      }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}
</style>
