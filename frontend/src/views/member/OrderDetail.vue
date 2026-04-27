<template>
  <div class="order-detail-page" v-loading="loading">
    <div v-if="order" class="order-detail">
      <div class="status-section">
        <div class="status-badge">
          <el-icon :size="48" :color="statusIconColor">
            <component :is="statusIconComponent" />
          </el-icon>
        </div>
        <div class="status-info">
          <h2 class="status-text">{{ getStatusTag(order.status).text }}</h2>
          <p class="status-desc" v-if="statusDesc">{{ statusDesc }}</p>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <el-icon><Location /></el-icon>
          <span>收货信息</span>
        </div>
        <div class="info-content">
          <p class="receiver">
            <span>{{ order.receiver_name }}</span>
            <span class="phone">{{ order.receiver_phone }}</span>
          </p>
          <p class="address" v-if="order.delivery_address">
            {{ order.delivery_address }}
          </p>
          <p class="pickup-info" v-else>
            <el-icon><Shop /></el-icon>
            自提，请联系团长确认自提时间
          </p>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <el-icon><Shop /></el-icon>
          <span>活动信息</span>
        </div>
        <div class="info-content">
          <p class="leader-info">
            团长: <span class="highlight">{{ order.leader_name }}</span>
          </p>
          <p class="activity-title">{{ order.activity_title }}</p>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <el-icon><Goods /></el-icon>
          <span>商品信息</span>
        </div>
        <div class="items-list">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <el-image
              :src="item.product_image || getPlaceholderImage()"
              :fit="cover"
              class="item-image"
            />
            <div class="item-info">
              <p class="item-name">{{ item.product_name }}</p>
              <p class="item-spec">{{ item.spec_name }}</p>
            </div>
            <div class="item-price">
              <span class="price">¥{{ item.unit_price.toFixed(2) }}</span>
              <span class="quantity">x {{ item.quantity }}</span>
              <span class="subtotal">¥{{ item.subtotal.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="section-header">
          <el-icon><Ticket /></el-icon>
          <span>订单信息</span>
        </div>
        <div class="order-info-list">
          <div class="info-row">
            <span class="label">订单编号</span>
            <span class="value">{{ order.order_no }}</span>
          </div>
          <div class="info-row">
            <span class="label">创建时间</span>
            <span class="value">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="info-row" v-if="order.paid_at">
            <span class="label">支付时间</span>
            <span class="value">{{ formatDate(order.paid_at) }}</span>
          </div>
          <div class="info-row" v-if="order.delivered_at">
            <span class="label">配送时间</span>
            <span class="value">{{ formatDate(order.delivered_at) }}</span>
          </div>
          <div class="info-row" v-if="order.completed_at">
            <span class="label">完成时间</span>
            <span class="value">{{ formatDate(order.completed_at) }}</span>
          </div>
          <div class="info-row" v-if="order.remark">
            <span class="label">备注</span>
            <span class="value">{{ order.remark }}</span>
          </div>
        </div>
      </div>

      <div class="info-section" v-if="statusLogs.length > 0">
        <div class="section-header">
          <el-icon><Clock /></el-icon>
          <span>状态日志</span>
        </div>
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

      <div class="price-section">
        <div class="price-row">
          <span>商品金额</span>
          <span>¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
        <div class="price-row">
          <span>运费</span>
          <span>¥0.00</span>
        </div>
        <div class="price-row total">
          <span>实付金额</span>
          <span class="total-price">¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
      </div>

      <div class="bottom-bar">
        <el-button v-if="order.can_cancel" @click="cancelOrder">
          取消订单
        </el-button>
        <el-button v-if="order.can_pay" type="primary" @click="payOrder">
          立即支付
        </el-button>
        <el-button v-if="order.can_apply_refund" @click="applyRefund">
          申请退款
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElMessage,
  ElMessageBox,
  type ElMessageBoxOptions,
} from "element-plus";
import { orderApi } from "@/api";
import { formatDate, getOrderStatusTag } from "@/utils";
import type { Order, OrderStatusLog } from "@/types";
import {
  Location,
  Shop,
  Goods,
  Ticket,
  Clock,
  CircleCheck,
  Clock as ClockIcon,
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
  preparing: ClockIcon,
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
      return "请在30分钟内完成支付，超时订单将自动取消";
    case "paid":
      return "团长正在备货，请耐心等待";
    case "preparing":
      return "团长正在备货中，即将为您配送";
    case "delivering":
      return "商品正在配送中，请保持电话畅通";
    case "completed":
      return "订单已完成，感谢您的购买";
    case "refunding":
      return "退款申请已提交，请等待团长审核";
    case "refunded":
      return "退款已完成";
    default:
      return "";
  }
});

const getStatusTag = (status: string) => {
  return getOrderStatusTag(status);
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect fill="%23f5f5f5" width="80" height="80"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="12" text-anchor="middle" x="40" y="45"%3E暂无图片%3C/text%3E%3C/svg%3E';
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

const cancelOrder = async () => {
  if (!order.value) return;

  try {
    await ElMessageBox.confirm("确定要取消这个订单吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await orderApi.cancelOrder(order.value.id);
    ElMessage.success("订单已取消");
    fetchOrder();
  } catch (error) {
    // 用户取消
  }
};

const payOrder = async () => {
  if (!order.value) return;

  try {
    await ElMessageBox.confirm(
      `订单金额: ¥${order.value.total_amount.toFixed(2)}\n确定要支付吗？`,
      "模拟支付",
      {
        confirmButtonText: "立即支付",
        cancelButtonText: "取消",
        type: "info",
      },
    );

    await orderApi.payOrder(order.value.id);
    ElMessage.success("支付成功！");
    fetchOrder();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.response?.data?.detail || "支付失败");
    }
  }
};

const applyRefund = async () => {
  if (!order.value) return;

  try {
    const { value: reason } = await ElMessageBox.prompt(
      "请输入退款原因",
      "申请退款",
      {
        confirmButtonText: "提交申请",
        cancelButtonText: "取消",
        inputPlaceholder: "请输入退款原因（选填）",
      } as ElMessageBoxOptions,
    );

    await orderApi.applyRefund(order.value.id, reason);
    ElMessage.success("退款申请已提交，请等待团长审核");
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
.order-detail-page {
  padding-bottom: 80px;

  .order-detail {
    max-width: 600px;
    margin: 0 auto;
  }

  .status-section {
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
    padding: 32px 20px;
    border-radius: 12px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 20px;

    .status-badge {
      width: 80px;
      height: 80px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .status-info {
      flex: 1;
      color: #fff;

      .status-text {
        font-size: 24px;
        font-weight: 600;
        margin: 0 0 8px;
      }

      .status-desc {
        font-size: 14px;
        margin: 0;
        opacity: 0.9;
      }
    }
  }

  .info-section {
    background: #fff;
    border-radius: 12px;
    margin-bottom: 16px;
    padding: 16px 20px;

    .section-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;
    }

    .info-content {
      .receiver {
        font-size: 16px;
        font-weight: 500;
        color: #333;
        margin: 0 0 8px;

        .phone {
          font-size: 14px;
          color: #666;
          margin-left: 16px;
        }
      }

      .address,
      .pickup-info {
        font-size: 14px;
        color: #666;
        margin: 0;
        line-height: 1.6;

        .highlight {
          color: #ff6b6b;
        }
      }

      .leader-info {
        font-size: 14px;
        color: #666;
        margin: 0 0 8px;

        .highlight {
          color: #333;
          font-weight: 500;
        }
      }

      .activity-title {
        font-size: 14px;
        color: #333;
        margin: 0;
      }
    }
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .order-item {
      display: flex;
      align-items: center;
      padding: 8px 0;

      .item-image {
        width: 64px;
        height: 64px;
        border-radius: 6px;
        flex-shrink: 0;
      }

      .item-info {
        flex: 1;
        margin-left: 12px;

        .item-name {
          font-size: 14px;
          color: #333;
          margin: 0 0 4px;
        }

        .item-spec {
          font-size: 12px;
          color: #999;
          margin: 0;
        }
      }

      .item-price {
        text-align: right;

        .price {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .quantity {
          font-size: 12px;
          color: #999;
        }

        .subtotal {
          display: block;
          font-size: 15px;
          font-weight: 600;
          color: #ff6b6b;
          margin-top: 4px;
        }
      }
    }
  }

  .order-info-list {
    .info-row {
      display: flex;
      padding: 8px 0;
      font-size: 14px;

      .label {
        width: 80px;
        color: #999;
        flex-shrink: 0;
      }

      .value {
        flex: 1;
        color: #333;
      }
    }
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

  .price-section {
    background: #fff;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;

    .price-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      font-size: 14px;
      color: #666;

      &.total {
        padding-top: 12px;
        margin-top: 8px;
        border-top: 1px solid #f0f0f0;
        font-size: 15px;
        font-weight: 500;
        color: #333;

        .total-price {
          font-size: 20px;
          font-weight: 600;
          color: #ff6b6b;
        }
      }
    }
  }

  .bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: #fff;
    box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 0 20px;
    gap: 12px;
    z-index: 100;
  }
}
</style>
