<template>
  <div class="leader-activity-detail" v-loading="loading">
    <div v-if="activity" class="detail-content">
      <div class="page-header">
        <el-button type="primary" plain @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <div class="header-actions">
          <el-button
            v-if="activity.status === 'active'"
            type="warning"
            @click="closeActivity"
          >
            关闭活动
          </el-button>
          <el-button
            v-if="activity.status === 'active'"
            type="primary"
            @click="showShare"
          >
            <el-icon><Share /></el-icon>
            分享
          </el-button>
          <el-dropdown trigger="click" v-if="activity.status === 'active'">
            <el-button type="primary" plain>
              <el-icon><More /></el-icon>
              更多操作
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="exportOrders">
                  <el-icon><Download /></el-icon>
                  导出订单
                </el-dropdown-item>
                <el-dropdown-item @click="exportBySpec">
                  <el-icon><Download /></el-icon>
                  按规格导出
                </el-dropdown-item>
                <el-dropdown-item @click="exportByMember">
                  <el-icon><Download /></el-icon>
                  按团员导出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div class="info-section">
        <h3 class="section-title">活动信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="活动标题">
            {{ activity.title }}
          </el-descriptions-item>
          <el-descriptions-item label="活动状态">
            <el-tag
              :type="getActivityStatusTag(activity.status).type"
              size="small"
            >
              {{ getActivityStatusTag(activity.status).text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="活动描述">
            {{ activity.description }}
          </el-descriptions-item>
          <el-descriptions-item label="配送方式">
            <el-tag
              :type="
                activity.delivery_type === 'pickup' ? 'warning' : 'primary'
              "
              size="small"
            >
              {{ activity.delivery_type_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(activity.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="截止时间">
            {{ formatDate(activity.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item
            label="起购金额"
            v-if="activity.min_order_amount > 0"
          >
            ¥{{ activity.min_order_amount.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item
            label="自提点地址"
            v-if="activity.delivery_type === 'pickup'"
          >
            {{ activity.pickup_address }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="info-section">
        <h3 class="section-title">统计数据</h3>
        <div class="stats-cards">
          <div class="stat-card">
            <p class="stat-value">{{ activity.participant_count }}</p>
            <p class="stat-label">参团人数</p>
          </div>
          <div class="stat-card">
            <p class="stat-value">{{ activity.total_orders }}</p>
            <p class="stat-label">订单数</p>
          </div>
          <div class="stat-card">
            <p class="stat-value">
              ¥{{ (activity.total_amount || 0).toFixed(2) }}
            </p>
            <p class="stat-label">总金额</p>
          </div>
          <div class="stat-card">
            <p class="stat-value">{{ activity.products?.length || 0 }}</p>
            <p class="stat-label">商品数</p>
          </div>
        </div>
      </div>

      <div class="info-section">
        <h3 class="section-title">商品列表</h3>
        <el-table :data="activity.products || []" style="width: 100%">
          <el-table-column
            prop="product_name"
            label="商品名称"
            min-width="150"
          />
          <el-table-column prop="spec_name" label="规格" width="120" />
          <el-table-column label="原价" width="100">
            <template #default="scope">
              ¥{{ scope.row.original_price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="团购价" width="100">
            <template #default="scope">
              <span class="highlight"
                >¥{{ scope.row.group_price.toFixed(2) }}</span
              >
            </template>
          </el-table-column>
          <el-table-column label="库存" width="100">
            <template #default="scope">
              <span :class="{ 'text-danger': scope.row.available_stock < 10 }">
                {{ scope.row.available_stock }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="已售" width="80">
            <template #default="scope">
              {{ scope.row.sold_quantity }}
            </template>
          </el-table-column>
          <el-table-column label="限购" width="80">
            <template #default="scope">
              {{ scope.row.limit_per_user || "不限" }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="info-section" v-if="summaryBySpec.length > 0">
        <h3 class="section-title">按规格汇总</h3>
        <el-table :data="summaryBySpec" style="width: 100%">
          <el-table-column
            prop="product_name"
            label="商品名称"
            min-width="150"
          />
          <el-table-column prop="spec_name" label="规格" width="120" />
          <el-table-column label="总数量" width="100">
            <template #default="scope">
              <span class="highlight">{{ scope.row.total_quantity }}</span>
            </template>
          </el-table-column>
          <el-table-column label="总金额" width="120">
            <template #default="scope">
              <span class="highlight"
                >¥{{ scope.row.total_amount.toFixed(2) }}</span
              >
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="info-section" v-if="summaryByMember.length > 0">
        <h3 class="section-title">按团员汇总</h3>
        <div class="member-list">
          <div
            v-for="member in summaryByMember"
            :key="member.user_id"
            class="member-item"
          >
            <div class="member-header">
              <span class="member-name">{{ member.user_name }}</span>
              <span class="member-phone">{{ member.receiver_phone }}</span>
              <el-tag type="primary" size="small">
                {{ member.total_quantity }}件商品 / ¥{{
                  member.total_amount.toFixed(2)
                }}
              </el-tag>
            </div>
            <div class="member-address" v-if="member.delivery_address">
              <el-icon><Location /></el-icon>
              {{ member.delivery_address }}
            </div>
            <div class="member-items">
              <div
                v-for="item in member.items"
                :key="`${item.product_name}-${item.spec_name}`"
                class="item-row"
              >
                <span class="item-name">{{ item.product_name }}</span>
                <span class="item-spec">({{ item.spec_name }})</span>
                <span class="item-quantity">x {{ item.quantity }}</span>
                <span class="item-price">¥{{ item.subtotal.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="shareDialogVisible" title="分享活动" width="500px">
      <div class="share-content">
        <div class="share-link">
          <span>分享链接: </span>
          <el-input v-model="shareLink" readonly class="link-input" />
          <el-button type="primary" @click="copyLink">复制链接</el-button>
        </div>

        <div class="share-poster" v-if="posterLoading">
          <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
          <p>正在生成海报...</p>
        </div>

        <div class="share-poster" v-else-if="posterImage">
          <el-image :src="posterImage" :fit="contain" class="poster-image" />
          <div class="poster-actions">
            <el-button type="primary" @click="downloadPoster">
              <el-icon><Download /></el-icon>
              保存海报
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { activityApi, orderApi, statisticsApi } from "@/api";
import {
  formatDate,
  getActivityStatusTag,
  generatePoster,
  downloadFile,
} from "@/utils";
import type {
  GroupBuyActivity,
  OrderSummaryBySpec,
  OrderSummaryByMember,
} from "@/types";
import {
  ArrowLeft,
  Share,
  More,
  Download,
  Loading,
  Location,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const activity = ref<GroupBuyActivity | null>(null);
const summaryBySpec = ref<OrderSummaryBySpec[]>([]);
const summaryByMember = ref<OrderSummaryByMember[]>([]);

const shareDialogVisible = ref(false);
const shareLink = ref("");
const posterImage = ref("");
const posterLoading = ref(false);

const goBack = () => {
  router.push("/leader/activities");
};

const fetchActivity = async () => {
  const id = route.params.id as string;
  if (!id) return;

  loading.value = true;
  try {
    activity.value = await activityApi.getActivity(id);

    if (activity.value?.status !== "draft") {
      try {
        summaryBySpec.value = await orderApi.getSummaryBySpec(id);
        summaryByMember.value = await orderApi.getSummaryByMember(id);
      } catch (e) {
        console.log("获取汇总数据失败:", e);
      }
    }
  } catch (error) {
    console.error("获取活动详情失败:", error);
    ElMessage.error("获取活动详情失败");
  } finally {
    loading.value = false;
  }
};

const closeActivity = async () => {
  if (!activity.value) return;

  try {
    await ElMessageBox.confirm(
      "确定要关闭这个团购活动吗？关闭后将无法继续下单。",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await activityApi.closeActivity(activity.value.id);
    ElMessage.success("活动已关闭");
    fetchActivity();
  } catch (error) {
    // 用户取消
  }
};

const showShare = async () => {
  if (!activity.value) return;

  shareDialogVisible.value = true;
  shareLink.value = `${window.location.origin}/share/${activity.value.share_code}`;
  posterImage.value = "";

  posterLoading.value = true;
  try {
    const shareInfo = await activityApi.getShareInfo(activity.value.id);
    posterImage.value = await generatePoster({
      title: shareInfo.title,
      coverImage: shareInfo.cover_image || "",
      minPrice: shareInfo.min_price,
      participantCount: shareInfo.participant_count,
      endTime: formatDate(shareInfo.end_time),
      leaderName: shareInfo.leader_name,
      shopName: shareInfo.shop_name || "",
      shareLink: shareInfo.share_link,
    });
  } catch (error) {
    console.error("生成海报失败:", error);
  } finally {
    posterLoading.value = false;
  }
};

const copyLink = () => {
  navigator.clipboard
    .writeText(shareLink.value)
    .then(() => {
      ElMessage.success("链接已复制");
    })
    .catch(() => {
      ElMessage.error("复制失败，请手动复制");
    });
};

const downloadPoster = () => {
  if (posterImage.value && activity.value) {
    downloadFile(posterImage.value, `团购海报-${activity.value.title}.png`);
  }
};

const exportOrders = () => {
  if (!activity.value) return;
  const url = statisticsApi.exportOrdersCsv(activity.value.id);
  window.open(url, "_blank");
};

const exportBySpec = () => {
  if (!activity.value) return;
  const url = statisticsApi.exportSummaryBySpecCsv(activity.value.id);
  window.open(url, "_blank");
};

const exportByMember = () => {
  if (!activity.value) return;
  const url = statisticsApi.exportSummaryByMemberCsv(activity.value.id);
  window.open(url, "_blank");
};

onMounted(() => {
  fetchActivity();
});
</script>

<style lang="scss" scoped>
.leader-activity-detail {
  .detail-content {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .header-actions {
      display: flex;
      gap: 12px;
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

    .stats-cards {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      @media (max-width: 768px) {
        grid-template-columns: repeat(2, 1fr);
      }

      .stat-card {
        text-align: center;
        padding: 20px;
        background: #fafafa;
        border-radius: 8px;

        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #ff6b6b;
          margin: 0 0 4px;
        }

        .stat-label {
          font-size: 13px;
          color: #999;
          margin: 0;
        }
      }
    }
  }

  .highlight {
    color: #ff6b6b;
    font-weight: 600;
  }

  .text-danger {
    color: #f56c6c;
  }

  .member-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .member-item {
      padding: 16px;
      background: #fafafa;
      border-radius: 8px;

      .member-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;

        .member-name {
          font-size: 15px;
          font-weight: 500;
          color: #333;
        }

        .member-phone {
          font-size: 14px;
          color: #666;
        }
      }

      .member-address {
        font-size: 13px;
        color: #666;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .member-items {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .item-row {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 8px 12px;
          background: #fff;
          border-radius: 6px;
          font-size: 13px;

          .item-name {
            color: #333;
          }

          .item-spec {
            color: #999;
          }

          .item-quantity {
            color: #ff6b6b;
            font-weight: 500;
          }

          .item-price {
            color: #ff6b6b;
            font-weight: 500;
            margin-left: 4px;
          }
        }
      }
    }
  }

  .share-content {
    .share-link {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;

      .link-input {
        flex: 1;
      }
    }

    .share-poster {
      text-align: center;
      padding: 20px;

      .loading-icon {
        animation: spin 1s linear infinite;
        color: #ff6b6b;
      }

      .poster-image {
        max-width: 100%;
        max-height: 400px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .poster-actions {
        margin-top: 16px;
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
