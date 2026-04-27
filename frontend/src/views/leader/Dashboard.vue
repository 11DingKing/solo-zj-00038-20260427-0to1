<template>
  <div class="leader-dashboard">
    <div class="page-header">
      <h2>数据统计</h2>
      <p>查看您的团购业务数据</p>
    </div>

    <div class="stats-cards" v-loading="loading">
      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%)"
        >
          <el-icon :size="32" color="#fff"><Wallet /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">
            ¥{{ dashboard?.monthly_amount?.toFixed(2) || "0.00" }}
          </p>
          <p class="stat-label">本月成交额</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #409eff 0%, #67c23a 100%)"
        >
          <el-icon :size="32" color="#fff"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ dashboard?.monthly_order_count || 0 }}</p>
          <p class="stat-label">本月订单数</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%)"
        >
          <el-icon :size="32" color="#fff"><Goods /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ dashboard?.active_activities || 0 }}</p>
          <p class="stat-label">进行中的团购</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #909399 0%, #67c23a 100%)"
        >
          <el-icon :size="32" color="#fff"><Coin /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">
            {{ (dashboard?.refund_rate || 0).toFixed(1) }}%
          </p>
          <p class="stat-label">退款率</p>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="content-section">
        <div class="section-header">
          <h3>总览数据</h3>
        </div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="累计成交额">
            <span class="highlight"
              >¥{{ dashboard?.total_amount?.toFixed(2) || "0.00" }}</span
            >
          </el-descriptions-item>
          <el-descriptions-item label="累计订单数">
            <span class="highlight">{{
              dashboard?.total_order_count || 0
            }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="累计退款数">
            <span>{{ dashboard?.refunded_count || 0 }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="累计退款金额">
            <span class="danger"
              >¥{{ dashboard?.refunded_amount?.toFixed(2) || "0.00" }}</span
            >
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="content-section" v-if="dashboard?.recent_orders?.length > 0">
        <div class="section-header">
          <h3>最近订单</h3>
          <el-button type="primary" text @click="goToOrders">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <el-table :data="dashboard.recent_orders" style="width: 100%">
          <el-table-column prop="order_no" label="订单号" width="180" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTag(scope.row.status).type" size="small">
                {{ getStatusTag(scope.row.status).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="receiver_name" label="收货人" width="100" />
          <el-table-column prop="receiver_phone" label="手机号" width="120" />
          <el-table-column label="订单金额" width="120">
            <template #default="scope">
              <span class="highlight"
                >¥{{ scope.row.total_amount.toFixed(2) }}</span
              >
            </template>
          </el-table-column>
          <el-table-column label="下单时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button
                type="primary"
                link
                size="small"
                @click="goToOrderDetail(scope.row.id)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="content-section">
        <div class="section-header">
          <h3>快捷操作</h3>
        </div>
        <div class="quick-actions">
          <div class="action-item" @click="goToCreateActivity">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
              "
            >
              <el-icon :size="28" color="#fff"><Plus /></el-icon>
            </div>
            <span class="action-label">发起新团购</span>
          </div>
          <div class="action-item" @click="goToActivities">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
              "
            >
              <el-icon :size="28" color="#fff"><Goods /></el-icon>
            </div>
            <span class="action-label">管理团购</span>
          </div>
          <div class="action-item" @click="goToRefunds">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%);
              "
            >
              <el-icon :size="28" color="#fff"><Warning /></el-icon>
            </div>
            <span class="action-label">退款申请</span>
          </div>
          <div class="action-item" @click="goToOrders">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #909399 0%, #67c23a 100%);
              "
            >
              <el-icon :size="28" color="#fff"><Document /></el-icon>
            </div>
            <span class="action-label">订单管理</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { statisticsApi } from "@/api";
import { formatDate, getOrderStatusTag } from "@/utils";
import type { LeaderDashboard } from "@/types";
import {
  Wallet,
  Document,
  Goods,
  Coin,
  ArrowRight,
  Plus,
  Warning,
} from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const dashboard = ref<LeaderDashboard | null>(null);

const getStatusTag = (status: string) => {
  return getOrderStatusTag(status);
};

const fetchDashboard = async () => {
  loading.value = true;
  try {
    dashboard.value = await statisticsApi.getLeaderDashboard();
  } catch (error) {
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  } finally {
    loading.value = false;
  }
};

const goToCreateActivity = () => {
  router.push("/leader/activities/create");
};

const goToActivities = () => {
  router.push("/leader/activities");
};

const goToOrders = () => {
  router.push("/leader/orders");
};

const goToRefunds = () => {
  router.push("/leader/refunds");
};

const goToOrderDetail = (id: string) => {
  router.push(`/leader/orders/${id}`);
};

onMounted(() => {
  fetchDashboard();
});
</script>

<style lang="scss" scoped>
.leader-dashboard {
  .page-header {
    margin-bottom: 24px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin: 0 0 8px;
    }

    p {
      font-size: 14px;
      color: #999;
      margin: 0;
    }
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 24px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }

    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }

      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .stat-content {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #333;
          margin: 0 0 4px;
        }

        .stat-label {
          font-size: 14px;
          color: #999;
          margin: 0;
        }
      }
    }
  }

  .dashboard-content {
    .content-section {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        h3 {
          font-size: 16px;
          font-weight: 600;
          color: #333;
          margin: 0;
        }
      }

      .highlight {
        color: #ff6b6b;
        font-weight: 600;
      }

      .danger {
        color: #f56c6c;
      }
    }

    .quick-actions {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      @media (max-width: 1200px) {
        grid-template-columns: repeat(2, 1fr);
      }

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }

      .action-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 24px;
        cursor: pointer;
        border-radius: 12px;
        background: #fafafa;
        transition: all 0.2s ease;

        &:hover {
          background: #f0f7ff;
          transform: translateY(-2px);
        }

        .action-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 12px;
        }

        .action-label {
          font-size: 14px;
          color: #333;
          font-weight: 500;
        }
      }
    }
  }
}
</style>
