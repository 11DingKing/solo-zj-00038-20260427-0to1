<template>
  <div class="leader-order-detail" v-loading="loading">
    <div v-if="order" class="detail-content">
      <div class="page-header">
        <el-button type="primary" plain @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>

      <div class="status-section">
        <div class="status-badge">
          <el-icon :size="40" :color="statusIconColor">
            <component :is="statusIconComponent" />
          </el-icon>
        </div>
        <div class="status-info">
          <h2 class="status-text">{{ getStatusTag(order.status).text }}</h2>
          <p class="status-desc" v-if="statusDesc">{{ statusDesc }}</p>
        </div>
      </div>

      <div class="info-section">
        <h3 class="section-title">收货信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="收货人">
            {{ order.receiver_name }}
          </el-descriptions-item>
          <el-descriptions-item label="手机号">
            {{ order.receiver_phone }}
          </el-descriptions-item>
          <el-descriptions-item
            label="收货地址"
            :span="2"
            v-if="order.delivery_address"
          >
            {{ order.delivery_address }}
          </el-descriptions-item>
          <el-descriptions-item label="配送方式" :span="2" v-else>
            <el-tag type="warning" size="small">自提</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2" v-if="order.remark">
            {{ order.remark }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="info-section">
        <h3 class="section-title">商品信息</h3>
        <el-table :data="order.items" style="width: 100%">
          <el-table-column label="商品" min-width="200">
            <template #default="scope">
              <div class="product-info">
                <el-image
                  :src="scope.row.product_image || getPlaceholderImage()"
                  :fit="cover"
                  class="product-image"
                />
                <div class="product-detail">
                  <p class="product-name">{{ scope.row.product_name }}</p>
                  <p class="product-spec">{{ scope.row.spec_name }}</p>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="100">
            <template #default="scope">
              ¥{{ scope.row.unit_price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="数量" width="80">
            <template #default="scope">
              {{ scope.row.quantity }}
            </template>
          </el-table-column>
          <el-table-column label="小计" width="100">
            <template #default="scope">
              <span class="highlight"
                >¥{{ scope.row.subtotal.toFixed(2) }}</span
              >
            </template>
          </el-table-column>
        </el-table>

        <div class="order-total">
          <div class="total-row">
            <span>商品金额:</span>
            <span>¥{{ order.total_amount.toFixed(2) }}</span>
          </div>
          <div class="total-row">
            <span>运费:</span>
            <span>¥0.00</span>
          </div>
          <div class="total-row final">
            <span>实付金额:</span>
            <span class="total-amount"
              >¥{{ order.total_amount.toFixed(2) }}</span
            >
          </div>
        </div>
      </div>

      <div class="info-section">
        <h3 class="section-title">订单信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">
            {{ order.order_no }}
          </el-descriptions-item>
          <el-descriptions-item label="下单时间">
            {{ formatDate(order.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="支付时间" v-if="order.paid_at">
            {{ formatDate(order.paid_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="配送时间" v-if="order.delivered_at">
            {{ formatDate(order.delivered_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间" v-if="order.completed_at">
            {{ formatDate(order.completed_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="info-section" v-if="statusLogs.length > 0">
        <h3 class="section-title">状态日志</h3>
        <div class="status-timeline">
          <div
            v-for="(log, index) in statusLogs"
            :key="log.id"
            class="timeline-item"
            :class="{ first: index === 0 }"
          >
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-status">
                <el-tag :type="getStatusTag(log.to_status).type" size="small">
                  {{ log.to_status_display }}
                </el-tag>
              </div>
              <div class="timeline-info">
                <span class="operator">{{ log.operator_name }}</span>
                <span class="time">{{ formatDate(log.created_at) }}</span>
              </div>
              <p v-if="log.remark" class="timeline-remark">{{ log.remark }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="action-section" v-if="showActions">
        <el-button
          v-if="order.status === 'paid'"
          type="warning"
          size="large"
          @click="updateStatus('preparing', '开始备货')"
        >
          开始备货
        </el-button>
        <el-button
          v-if="order.status === 'preparing'"
          type="warning"
          size="large"
          @click="updateStatus('delivering', '开始配送')"
        >
          开始配送
        </el-button>
        <el-button
          v-if="order.status === 'delivering'"
          type="success"
          size="large"
          @click="updateStatus('completed', '确认送达')"
        >
          确认送达
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { orderApi } from "@/api";
import { formatDate, getOrderStatusTag } from "@/utils";
import type { Order, OrderStatusLog } from "@/types";
import {
  ArrowLeft,
  CircleCheck,
  Clock,
  ShoppingCart,
  Warning,
  CircleClose,
  Coin,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const order = ref<Order | null>(null);
const statusLogs = ref<OrderStatusLog[]>([]);

const statusIconMap: Record<string, any> = {
  pending: Coin,
  paid: CircleCheck,
  preparing: Clock,
  delivering: ShoppingCart,
  completed: CircleCheck,
  cancelled: CircleClose,
  refunding: Warning,
  refunded: CircleClose,
};

const statusIconComponent = computed(() => {
  if (!order.value) return Coin;
  return statusIconMap[order.value.status] || Coin;
});

const statusIconColor = computed(() => {
  if (!order.value) return "#999";
  const tag = getStatusTag(order.value.status);
  switch (tag.type) {
    case "success":
      return "#67C23A";
    case "warning":
      return "#E6A23C";
    case "danger":
      return "#F56C6C";
    default:
      return "#909399";
  }
});

const statusDesc = computed(() => {
  if (!order.value) return "";
  switch (order.value.status) {
    case "pending":
      return "等待团员支付";
    case "paid":
      return "团员已付款，请尽快备货";
    case "preparing":
      return "正在备货中";
    case "delivering":
      return "商品正在配送中";
    case "completed":
      return "订单已完成";
    default:
      return "";
  }
});

const showActions = computed(() => {
  if (!order.value) return false;
  return ["paid", "preparing", "delivering"].includes(order.value.status);
});

const getStatusTag = (status: string) => {
  return getOrderStatusTag(status);
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60"%3E%3Crect fill="%23f5f5f5" width="60" height="60"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="10" text-anchor="middle" x="30" y="35"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const goBack = () => {
  router.push("/leader/orders");
};

const fetchOrder = async () => {
  const id = route.params.id as string;
  if (!id) return;

  loading.value = true;
  try {
    order.value = await orderApi.getOrder(id);
    statusLogs.value = await orderApi.getOrderStatusLogs(id);
  } catch (error) {
    console.error("获取订单详情失败:", error);
    ElMessage.error("获取订单详情失败");
  } finally {
    loading.value = false;
  }
};

const updateStatus = async (status: string, action: string) => {
  if (!order.value) return;

  try {
    await ElMessageBox.confirm(`确定要${action}吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await orderApi.updateOrderStatus(order.value.id, status);
    ElMessage.success("操作成功");
    fetchOrder();
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  fetchOrder();
});
</script>

<style lang="scss" scoped>
.leader-order-detail {
  .detail-content {
    max-width: 800px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 24px;
  }

  .status-section {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;
    background: #fff;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .status-badge {
      width: 80px;
      height: 80px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 50%;
    }

    .status-info {
      .status-text {
        font-size: 20px;
        font-weight: 600;
        color: #333;
        margin: 0 0 8px;
      }

      .status-desc {
        font-size: 14px;
        color: #999;
        margin: 0;
      }
    }
  }

  .info-section {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0 0 16px;
    }

    .product-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .product-image {
        width: 60px;
        height: 60px;
        border-radius: 6px;
        flex-shrink: 0;
      }

      .product-detail {
        .product-name {
          font-size: 14px;
          color: #333;
          margin: 0 0 4px;
        }

        .product-spec {
          font-size: 12px;
          color: #999;
          margin: 0;
        }
      }
    }

    .order-total {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;

      .total-row {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-bottom: 8px;
        font-size: 14px;
        color: #666;

        &:last-child {
          margin-bottom: 0;
        }

        &.final {
          font-size: 16px;
          font-weight: 500;
          color: #333;
        }

        span:first-child {
          margin-right: 20px;
        }
      }

      .total-amount {
        font-size: 20px;
        font-weight: 600;
        color: #ff6b6b;
      }
    }
  }

  .highlight {
    color: #ff6b6b;
    font-weight: 600;
  }

  .status-timeline {
    position: relative;
    padding-left: 20px;

    &::before {
      content: "";
      position: absolute;
      left: 7px;
      top: 8px;
      bottom: 8px;
      width: 2px;
      background: #e8e8e8;
    }

    .timeline-item {
      position: relative;
      padding-bottom: 20px;

      &.first {
        .timeline-dot {
          background: #ff6b6b;
          border-color: #ff6b6b;
        }
      }

      &:last-child {
        padding-bottom: 0;
      }

      .timeline-dot {
        position: absolute;
        left: -20px;
        top: 4px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #e8e8e8;
        border: 3px solid #fff;
        box-shadow: 0 0 0 2px #e8e8e8;
      }

      .timeline-content {
        .timeline-status {
          margin-bottom: 4px;
        }

        .timeline-info {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .timeline-remark {
          font-size: 13px;
          color: #666;
          margin: 0;
          padding: 8px;
          background: #f5f5f5;
          border-radius: 4px;
        }
      }
    }
  }

  .action-section {
    display: flex;
    justify-content: center;
    gap: 12px;
    padding: 20px;
  }
}
</style>
