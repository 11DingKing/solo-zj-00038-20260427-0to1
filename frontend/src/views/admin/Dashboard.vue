<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h2>数据统计</h2>
      <p>平台整体运营数据概览</p>
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
            ¥{{ dashboard?.total_amount?.toFixed(2) || "0.00" }}
          </p>
          <p class="stat-label">平台总成交额</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #409eff 0%, #67c23a 100%)"
        >
          <el-icon :size="32" color="#fff"><UserFilled /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ dashboard?.active_leaders || 0 }}</p>
          <p class="stat-label">活跃团长数</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%)"
        >
          <el-icon :size="32" color="#fff"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ dashboard?.total_orders || 0 }}</p>
          <p class="stat-label">总订单数</p>
        </div>
      </div>

      <div class="stat-card">
        <div
          class="stat-icon"
          style="background: linear-gradient(135deg, #909399 0%, #67c23a 100%)"
        >
          <el-icon :size="32" color="#fff"><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ dashboard?.last_30_days_orders || 0 }}</p>
          <p class="stat-label">近30天订单</p>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div
        class="content-section warning-section"
        v-if="
          dashboard?.pending_leader_count && dashboard.pending_leader_count > 0
        "
      >
        <div class="warning-content" @click="goToLeaders">
          <el-icon :size="24" color="#E6A23C"><Warning /></el-icon>
          <span
            >有
            <span class="highlight">{{ dashboard.pending_leader_count }}</span>
            位团长待审核，请及时处理</span
          >
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="content-section">
        <div class="section-header">
          <h3>近30天交易趋势</h3>
        </div>
        <div class="trend-chart" v-if="dashboard?.trading_trend?.length > 0">
          <div class="chart-header">
            <span class="chart-title">订单数趋势</span>
          </div>
          <div class="chart-bars">
            <div
              v-for="(item, index) in dashboard.trading_trend"
              :key="index"
              class="bar-item"
            >
              <div class="bar-wrapper">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(item.order_count) + '%' }"
                >
                  <span class="bar-value">{{ item.order_count }}</span>
                </div>
              </div>
              <span class="bar-label">{{ item.date.slice(5) }}</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无交易数据" :image-size="60" />
      </div>

      <div class="content-section">
        <div class="section-header">
          <h3>热门商品排行</h3>
        </div>
        <div class="hot-products" v-if="dashboard?.hot_products?.length > 0">
          <div
            v-for="(product, index) in dashboard.hot_products"
            :key="`${product.product_name}-${product.spec_name}`"
            class="product-item"
          >
            <div class="rank" :class="'rank-' + (index + 1)">
              {{ index + 1 }}
            </div>
            <div class="product-info">
              <p class="product-name">{{ product.product_name }}</p>
              <p class="product-spec">{{ product.spec_name }}</p>
            </div>
            <div class="product-stats">
              <div class="stat">
                <span class="stat-value">{{ product.total_quantity }}</span>
                <span class="stat-label">销量</span>
              </div>
              <div class="stat">
                <span class="stat-value highlight"
                  >¥{{ product.total_amount.toFixed(2) }}</span
                >
                <span class="stat-label">销售额</span>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无销售数据" :image-size="60" />
      </div>

      <div class="content-section">
        <div class="section-header">
          <h3>快捷操作</h3>
        </div>
        <div class="quick-actions">
          <div class="action-item" @click="goToProducts">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
              "
            >
              <el-icon :size="28" color="#fff"><Goods /></el-icon>
            </div>
            <span class="action-label">商品管理</span>
          </div>
          <div class="action-item" @click="goToLeaders">
            <div
              class="action-icon"
              style="
                background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
              "
            >
              <el-icon :size="28" color="#fff"><UserFilled /></el-icon>
            </div>
            <span class="action-label">团长审核</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { statisticsApi } from "@/api";
import type { AdminDashboard } from "@/types";
import {
  Wallet,
  UserFilled,
  Document,
  Clock,
  Warning,
  ArrowRight,
  Goods,
} from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const dashboard = ref<AdminDashboard | null>(null);

const maxOrderCount = computed(() => {
  if (!dashboard.value?.trading_trend?.length) return 0;
  return Math.max(
    ...dashboard.value.trading_trend.map((t) => t.order_count),
    1,
  );
});

const getBarHeight = (count: number) => {
  if (maxOrderCount.value === 0) return 0;
  return (count / maxOrderCount.value) * 80 + 5;
};

const fetchDashboard = async () => {
  loading.value = true;
  try {
    dashboard.value = await statisticsApi.getAdminDashboard();
  } catch (error) {
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  } finally {
    loading.value = false;
  }
};

const goToProducts = () => {
  router.push("/admin/products");
};

const goToLeaders = () => {
  router.push("/admin/leaders");
};

onMounted(() => {
  fetchDashboard();
});
</script>

<style lang="scss" scoped>
.admin-dashboard {
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
    .warning-section {
      background: #fffbeb;
      border: 1px solid #e6a23c;
      border-radius: 8px;
      margin-bottom: 20px;

      .warning-content {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        cursor: pointer;

        &:hover {
          background: rgba(230, 162, 60, 0.05);
        }

        .highlight {
          color: #e6a23c;
          font-weight: 600;
          font-size: 16px;
        }
      }
    }

    .content-section {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

      .section-header {
        margin-bottom: 20px;

        h3 {
          font-size: 16px;
          font-weight: 600;
          color: #333;
          margin: 0;
        }
      }
    }

    .trend-chart {
      .chart-header {
        margin-bottom: 20px;

        .chart-title {
          font-size: 14px;
          color: #666;
        }
      }

      .chart-bars {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 8px;
        height: 200px;
        padding: 0 10px;

        .bar-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100%;

          .bar-wrapper {
            flex: 1;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            width: 100%;
          }

          .bar {
            width: 24px;
            background: linear-gradient(180deg, #409eff 0%, #67c23a 100%);
            border-radius: 4px 4px 0 0;
            position: relative;
            transition: height 0.3s ease;
            min-height: 8px;

            .bar-value {
              position: absolute;
              top: -22px;
              left: 50%;
              transform: translateX(-50%);
              font-size: 12px;
              color: #666;
              white-space: nowrap;
            }
          }

          .bar-label {
            font-size: 11px;
            color: #999;
            margin-top: 8px;
          }
        }
      }
    }

    .hot-products {
      display: flex;
      flex-direction: column;
      gap: 16px;

      .product-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px;
        background: #fafafa;
        border-radius: 8px;

        .rank {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
          flex-shrink: 0;

          &.rank-1 {
            background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
            color: #fff;
          }

          &.rank-2 {
            background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
            color: #fff;
          }

          &.rank-3 {
            background: linear-gradient(135deg, #cd7f32 0%, #8b4513 100%);
            color: #fff;
          }

          &:not(.rank-1):not(.rank-2):not(.rank-3) {
            background: #e8e8e8;
            color: #666;
          }
        }

        .product-info {
          flex: 1;

          .product-name {
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin: 0 0 4px;
          }

          .product-spec {
            font-size: 12px;
            color: #999;
            margin: 0;
          }
        }

        .product-stats {
          display: flex;
          gap: 32px;

          .stat {
            text-align: right;

            .stat-value {
              display: block;
              font-size: 16px;
              font-weight: 500;
              color: #333;
            }

            .stat-label {
              font-size: 12px;
              color: #999;
            }

            .highlight {
              color: #ff6b6b;
            }
          }
        }
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

  .highlight {
    color: #ff6b6b;
    font-weight: 600;
  }
}
</style>
