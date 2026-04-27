<template>
  <div class="leader-orders">
    <div class="page-header">
      <h2>订单管理</h2>
      <div class="header-actions">
        <el-select
          v-model="statusFilter"
          placeholder="筛选状态"
          clearable
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="待付款" value="pending" />
          <el-option label="已付款" value="paid" />
          <el-option label="备货中" value="preparing" />
          <el-option label="配送中" value="delivering" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="退款中" value="refunding" />
          <el-option label="已退款" value="refunded" />
        </el-select>
      </div>
    </div>

    <div class="order-list" v-loading="loading">
      <el-empty v-if="orders.length === 0 && !loading" description="暂无订单" />

      <el-table :data="orders" style="width: 100%" v-if="orders.length > 0">
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
        <el-table-column label="配送方式" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.delivery_address ? 'primary' : 'warning'"
              size="small"
            >
              {{ scope.row.delivery_address ? "配送" : "自提" }}
            </el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              link
              size="small"
              @click="goToDetail(scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-if="scope.row.status === 'paid'"
              type="warning"
              link
              size="small"
              @click="updateStatus(scope.row, 'preparing', '开始备货')"
            >
              备货
            </el-button>
            <el-button
              v-if="scope.row.status === 'preparing'"
              type="warning"
              link
              size="small"
              @click="updateStatus(scope.row, 'delivering', '开始配送')"
            >
              配送
            </el-button>
            <el-button
              v-if="scope.row.status === 'delivering'"
              type="success"
              link
              size="small"
              @click="updateStatus(scope.row, 'completed', '确认送达')"
            >
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { orderApi } from "@/api";
import { formatDate, getOrderStatusTag } from "@/utils";
import type { Order, PaginatedResponse } from "@/types";

const router = useRouter();

const loading = ref(false);
const orders = ref<Order[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const statusFilter = ref("");

const getStatusTag = (status: string) => {
  return getOrderStatusTag(status);
};

const fetchOrders = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    };
    if (statusFilter.value) {
      params.status = statusFilter.value;
    }

    const res: PaginatedResponse<Order> = await orderApi.getOrders(params);
    orders.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取订单列表失败:", error);
    ElMessage.error("获取订单列表失败");
  } finally {
    loading.value = false;
  }
};

const handleFilterChange = () => {
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
  router.push(`/leader/orders/${id}`);
};

const updateStatus = async (order: Order, status: string, action: string) => {
  try {
    await ElMessageBox.confirm(`确定要${action}吗？`, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await orderApi.updateOrderStatus(order.id, status);
    ElMessage.success("操作成功");
    fetchOrders();
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  fetchOrders();
});
</script>

<style lang="scss" scoped>
.leader-orders {
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

  .order-list {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .highlight {
    color: #ff6b6b;
    font-weight: 600;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}
</style>
