<template>
  <div class="leader-refunds">
    <div class="page-header">
      <h2>退款管理</h2>
      <p>处理团员的退款申请</p>
    </div>

    <div class="refund-list" v-loading="loading">
      <el-empty
        v-if="refunds.length === 0 && !loading"
        description="暂无退款申请"
      />

      <div v-for="order in refunds" :key="order.id" class="refund-card">
        <div class="card-header">
          <div class="order-info">
            <span class="order-no">订单号: {{ order.order_no }}</span>
            <el-tag type="danger" size="small">退款中</el-tag>
          </div>
          <span class="apply-time"
            >申请时间: {{ formatDate(order.created_at) }}</span
          >
        </div>

        <div class="card-content">
          <div class="receiver-info">
            <h4>申请人信息</h4>
            <p>
              <span class="label">姓名:</span>
              <span>{{ order.receiver_name }}</span>
            </p>
            <p>
              <span class="label">电话:</span>
              <span>{{ order.receiver_phone }}</span>
            </p>
            <p v-if="order.delivery_address">
              <span class="label">地址:</span>
              <span>{{ order.delivery_address }}</span>
            </p>
          </div>

          <div class="order-items">
            <h4>商品信息</h4>
            <div class="items-list">
              <div v-for="item in order.items" :key="item.id" class="item-row">
                <el-image
                  :src="item.product_image || getPlaceholderImage()"
                  :fit="cover"
                  class="item-image"
                />
                <div class="item-detail">
                  <p class="item-name">{{ item.product_name }}</p>
                  <p class="item-spec">{{ item.spec_name }}</p>
                </div>
                <div class="item-price">
                  <span>¥{{ item.unit_price.toFixed(2) }}</span>
                  <span class="quantity">x {{ item.quantity }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="order-amount">
            <span>订单金额: </span>
            <span class="amount">¥{{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>

        <div class="card-actions">
          <el-button type="success" size="small" @click="approveRefund(order)">
            <el-icon><CircleCheck /></el-icon>
            同意退款
          </el-button>
          <el-button type="danger" size="small" @click="rejectRefund(order)">
            <el-icon><CircleClose /></el-icon>
            拒绝退款
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
import { ref, onMounted } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type ElMessageBoxOptions,
} from "element-plus";
import { orderApi } from "@/api";
import { formatDate } from "@/utils";
import type { Order, PaginatedResponse } from "@/types";
import { CircleCheck, CircleClose } from "@element-plus/icons-vue";

const loading = ref(false);
const refunds = ref<Order[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60"%3E%3Crect fill="%23f5f5f5" width="60" height="60"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="10" text-anchor="middle" x="30" y="35"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchRefunds = async () => {
  loading.value = true;
  try {
    const res: PaginatedResponse<Order> = await orderApi.getOrders({
      page: currentPage.value,
      page_size: pageSize.value,
      status: "refunding",
    });
    refunds.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取退款列表失败:", error);
    ElMessage.error("获取退款列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchRefunds();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchRefunds();
};

const approveRefund = async (order: Order) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      "请输入处理备注（选填）",
      "同意退款",
      {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        inputPlaceholder: "请输入备注（选填）",
      } as ElMessageBoxOptions,
    );

    await orderApi.processRefund(order.id, "approve", reason);
    ElMessage.success("退款已处理");
    fetchRefunds();
  } catch (error) {
    // 用户取消
  }
};

const rejectRefund = async (order: Order) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      "请输入拒绝原因",
      "拒绝退款",
      {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        inputPlaceholder: "请输入拒绝原因",
      } as ElMessageBoxOptions,
    );

    if (!reason || reason.trim() === "") {
      ElMessage.warning("请输入拒绝原因");
      return;
    }

    await orderApi.processRefund(order.id, "reject", reason);
    ElMessage.success("已拒绝退款申请");
    fetchRefunds();
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  fetchRefunds();
});
</script>

<style lang="scss" scoped>
.leader-refunds {
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

  .refund-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .refund-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border-left: 4px solid #f56c6c;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: #fff5f5;
      border-bottom: 1px solid #ffe4e4;

      .order-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .order-no {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }
      }

      .apply-time {
        font-size: 13px;
        color: #999;
      }
    }

    .card-content {
      padding: 20px;

      .receiver-info,
      .order-items {
        margin-bottom: 20px;

        h4 {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          margin: 0 0 12px;
        }

        p {
          font-size: 14px;
          color: #666;
          margin: 0 0 6px;

          .label {
            color: #999;
          }
        }
      }

      .items-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .item-row {
          display: flex;
          align-items: center;
          padding: 12px;
          background: #fafafa;
          border-radius: 8px;

          .item-image {
            width: 50px;
            height: 50px;
            border-radius: 6px;
            flex-shrink: 0;
          }

          .item-detail {
            flex: 1;
            margin-left: 12px;

            .item-name {
              font-size: 14px;
              color: #333;
              margin: 0 0 2px;
            }

            .item-spec {
              font-size: 12px;
              color: #999;
              margin: 0;
            }
          }

          .item-price {
            text-align: right;

            span {
              font-size: 14px;
              color: #333;
              font-weight: 500;
            }

            .quantity {
              color: #999;
              font-weight: normal;
              margin-left: 8px;
            }
          }
        }
      }

      .order-amount {
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
        font-size: 14px;
        color: #666;
        text-align: right;

        .amount {
          font-size: 18px;
          font-weight: 600;
          color: #ff6b6b;
        }
      }
    }

    .card-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 20px;
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
