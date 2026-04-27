<template>
  <div class="order-list-page">
    <div class="page-header">
      <h2>我的订单</h2>
      <el-tabs
        v-model="activeTab"
        class="order-tabs"
        @tab-change="handleTabChange"
      >
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待付款" name="pending" />
        <el-tab-pane label="已付款" name="paid" />
        <el-tab-pane label="待收货" name="delivering" />
        <el-tab-pane label="已完成" name="completed" />
        <el-tab-pane label="退款/售后" name="refund" />
      </el-tabs>
    </div>

    <div class="order-list" v-loading="loading">
      <el-empty v-if="orders.length === 0 && !loading" description="暂无订单" />

      <div
        v-for="order in orders"
        :key="order.id"
        class="order-card"
        @click="goToDetail(order.id)"
      >
        <div class="card-header">
          <span class="order-no">订单号: {{ order.order_no }}</span>
          <el-tag :type="getStatusTag(order.status).type" size="small">
            {{ getStatusTag(order.status).text }}
          </el-tag>
        </div>

        <div class="card-content">
          <div class="activity-info">
            <el-icon><Shop /></el-icon>
            <span class="leader-name">{{ order.leader_name }}</span>
            <span class="separator">|</span>
            <span class="activity-title">{{ order.activity_title }}</span>
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
              </div>
            </div>
          </div>

          <div class="card-footer">
            <span class="create-time">{{ formatDate(order.created_at) }}</span>
            <div class="order-total">
              <span>共 {{ order.items.length }} 件商品，订单金额: </span>
              <span class="total-amount"
                >¥{{ order.total_amount.toFixed(2) }}</span
              >
            </div>
          </div>
        </div>

        <div class="card-actions" @click.stop>
          <el-button
            v-if="order.can_cancel"
            size="small"
            @click="cancelOrder(order)"
          >
            取消订单
          </el-button>
          <el-button
            v-if="order.can_pay"
            type="primary"
            size="small"
            @click="payOrder(order)"
          >
            立即支付
          </el-button>
          <el-button
            v-if="order.can_apply_refund"
            size="small"
            @click="applyRefund(order)"
          >
            申请退款
          </el-button>
          <el-button size="small" @click="goToDetail(order.id)">
            查看详情
          </el-button>
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
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  ElMessage,
  ElMessageBox,
  type ElMessageBoxOptions,
} from "element-plus";
import { orderApi } from "@/api";
import { formatDate, getOrderStatusTag } from "@/utils";
import type { Order, PaginatedResponse } from "@/types";
import { Shop } from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

const loading = ref(false);
const orders = ref<Order[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const activeTab = ref("all");

const statusMap: Record<string, string | undefined> = {
  all: undefined,
  pending: "pending",
  paid: "paid",
  delivering: "delivering",
  completed: "completed",
  refund: "refunding",
};

const getStatusTag = (status: string) => {
  return getOrderStatusTag(status);
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect fill="%23f5f5f5" width="80" height="80"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="12" text-anchor="middle" x="40" y="45"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchOrders = async () => {
  loading.value = true;
  try {
    const res: PaginatedResponse<Order> = await orderApi.getMyOrders({
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusMap[activeTab.value],
    });
    orders.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取订单列表失败:", error);
    ElMessage.error("获取订单列表失败");
  } finally {
    loading.value = false;
  }
};

const handleTabChange = () => {
  currentPage.value = 1;
  fetchOrders();
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchOrders();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchOrders();
};

const goToDetail = (id: string) => {
  router.push(`/orders/${id}`);
};

const cancelOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm("确定要取消这个订单吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await orderApi.cancelOrder(order.id);
    ElMessage.success("订单已取消");
    fetchOrders();
  } catch (error) {
    // 用户取消
  }
};

const payOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      `订单金额: ¥${order.total_amount.toFixed(2)}\n确定要支付吗？`,
      "模拟支付",
      {
        confirmButtonText: "立即支付",
        cancelButtonText: "取消",
        type: "info",
      },
    );

    const res = await orderApi.payOrder(order.id);
    ElMessage.success("支付成功！");
    fetchOrders();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.response?.data?.detail || "支付失败");
    }
  }
};

const applyRefund = async (order: Order) => {
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

    await orderApi.applyRefund(order.id, reason);
    ElMessage.success("退款申请已提交，请等待团长审核");
    fetchOrders();
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  const status = route.query.status as string;
  if (status && statusMap[status]) {
    activeTab.value = status;
  }
  fetchOrders();
});
</script>

<style lang="scss" scoped>
.order-list-page {
  .page-header {
    margin-bottom: 20px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin: 0 0 16px;
    }

    .order-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 0;
      }
    }
  }

  .order-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .order-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #fafafa;
      border-bottom: 1px solid #f0f0f0;

      .order-no {
        font-size: 13px;
        color: #666;
      }
    }

    .card-content {
      padding: 16px;

      .activity-info {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-size: 13px;
        color: #666;

        .leader-name {
          font-weight: 500;
          color: #333;
        }

        .separator {
          color: #ddd;
        }

        .activity-title {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .items-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 12px;

        .order-item {
          display: flex;
          align-items: center;

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
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
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
              color: #ff6b6b;
            }

            .quantity {
              font-size: 12px;
              color: #999;
            }
          }
        }
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid #f0f0f0;

        .create-time {
          font-size: 12px;
          color: #999;
        }

        .order-total {
          font-size: 13px;
          color: #666;

          .total-amount {
            font-size: 18px;
            font-weight: 600;
            color: #ff6b6b;
          }
        }
      }
    }

    .card-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding: 12px 16px;
      background: #fafafa;
      border-top: 1px solid #f0f0f0;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}
</style>
