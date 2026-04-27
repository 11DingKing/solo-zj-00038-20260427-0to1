<template>
  <div class="leader-activities">
    <div class="page-header">
      <h2>团购管理</h2>
      <div class="header-actions">
        <el-select
          v-model="statusFilter"
          placeholder="筛选状态"
          clearable
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="进行中" value="active" />
          <el-option label="草稿" value="draft" />
          <el-option label="已关闭" value="closed" />
          <el-option label="已结束" value="ended" />
        </el-select>
        <el-button type="primary" @click="goToCreate">
          <el-icon><Plus /></el-icon>
          发起新团购
        </el-button>
      </div>
    </div>

    <div class="activity-list" v-loading="loading">
      <el-empty
        v-if="activities.length === 0 && !loading"
        description="暂无团购活动"
      />

      <div
        v-for="activity in activities"
        :key="activity.id"
        class="activity-card"
      >
        <div class="card-header">
          <div class="activity-title">
            <h3>{{ activity.title }}</h3>
            <el-tag
              :type="getActivityStatusTag(activity.status).type"
              size="small"
            >
              {{ getActivityStatusTag(activity.status).text }}
            </el-tag>
          </div>
          <div class="card-actions">
            <el-button
              type="primary"
              size="small"
              @click="goToDetail(activity.id)"
            >
              详情
            </el-button>
            <el-button
              v-if="activity.status === 'active'"
              type="warning"
              size="small"
              @click="closeActivity(activity)"
            >
              关闭
            </el-button>
            <el-dropdown trigger="click" v-if="activity.status === 'active'">
              <el-button size="small" type="primary" plain>
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="showShare(activity)">
                    <el-icon><Share /></el-icon>
                    分享
                  </el-dropdown-item>
                  <el-dropdown-item @click="exportOrders(activity.id)">
                    <el-icon><Download /></el-icon>
                    导出订单
                  </el-dropdown-item>
                  <el-dropdown-item @click="exportBySpec(activity.id)">
                    <el-icon><Download /></el-icon>
                    按规格导出
                  </el-dropdown-item>
                  <el-dropdown-item @click="exportByMember(activity.id)">
                    <el-icon><Download /></el-icon>
                    按团员导出
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="card-content">
          <p class="description">{{ activity.description }}</p>

          <div class="activity-meta">
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span
                >{{ formatDate(activity.start_time) }} ~
                {{ formatDate(activity.end_time) }}</span
              >
            </div>
            <div class="meta-item">
              <el-icon><Location /></el-icon>
              <span>
                {{ activity.delivery_type === "pickup" ? "自提" : "配送" }}
                <span v-if="activity.delivery_type === 'pickup'"
                  >: {{ activity.pickup_address }}</span
                >
              </span>
            </div>
          </div>

          <div class="activity-stats">
            <div class="stat-item">
              <span class="stat-value">{{ activity.participant_count }}</span>
              <span class="stat-label">参团人数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ activity.total_orders }}</span>
              <span class="stat-label">订单数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value"
                >¥{{ (activity.total_amount || 0).toFixed(2) }}</span
              >
              <span class="stat-label">总金额</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{
                activity.products?.length || 0
              }}</span>
              <span class="stat-label">商品数</span>
            </div>
          </div>
        </div>

        <div class="card-products" v-if="activity.products?.length > 0">
          <h4>商品列表</h4>
          <div class="product-list">
            <div
              v-for="product in activity.products.slice(0, 3)"
              :key="product.id"
              class="product-item"
            >
              <el-image
                :src="product.product_image || getPlaceholderImage()"
                :fit="cover"
                class="product-image"
              />
              <div class="product-info">
                <p class="product-name">{{ product.product_name }}</p>
                <p class="product-spec">{{ product.spec_name }}</p>
              </div>
              <div class="product-price">
                <span class="price">¥{{ product.group_price.toFixed(2) }}</span>
                <span class="stock">库存: {{ product.available_stock }}</span>
              </div>
            </div>
            <div v-if="activity.products.length > 3" class="more-products">
              还有 {{ activity.products.length - 3 }} 件商品...
            </div>
          </div>
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

    <el-dialog v-model="shareDialogVisible" title="分享活动" width="500px">
      <div class="share-content" v-if="currentActivity">
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { activityApi } from "@/api";
import { statisticsApi } from "@/api";
import {
  formatDate,
  getActivityStatusTag,
  generatePoster,
  downloadFile,
} from "@/utils";
import type { GroupBuyActivity } from "@/types";
import {
  Plus,
  More,
  Share,
  Download,
  Clock,
  Location,
  Loading,
} from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const activities = ref<GroupBuyActivity[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const statusFilter = ref("");

const shareDialogVisible = ref(false);
const currentActivity = ref<GroupBuyActivity | null>(null);
const shareLink = ref("");
const posterImage = ref("");
const posterLoading = ref(false);

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60"%3E%3Crect fill="%23f5f5f5" width="60" height="60"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="10" text-anchor="middle" x="30" y="35"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchActivities = async () => {
  loading.value = true;
  try {
    const res = await activityApi.getMyActivities({
      page: currentPage.value,
      page_size: pageSize.value,
    });
    activities.value = res as GroupBuyActivity[];
    total.value = (res as any).count || activities.value.length;
  } catch (error) {
    console.error("获取活动列表失败:", error);
    ElMessage.error("获取活动列表失败");
  } finally {
    loading.value = false;
  }
};

const handleFilterChange = () => {
  currentPage.value = 1;
  fetchActivities();
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchActivities();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchActivities();
};

const goToCreate = () => {
  router.push("/leader/activities/create");
};

const goToDetail = (id: string) => {
  router.push(`/leader/activities/${id}`);
};

const closeActivity = async (activity: GroupBuyActivity) => {
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

    await activityApi.closeActivity(activity.id);
    ElMessage.success("活动已关闭");
    fetchActivities();
  } catch (error) {
    // 用户取消
  }
};

const showShare = async (activity: GroupBuyActivity) => {
  currentActivity.value = activity;
  shareDialogVisible.value = true;
  shareLink.value = `${window.location.origin}/share/${activity.share_code}`;
  posterImage.value = "";

  posterLoading.value = true;
  try {
    const shareInfo = await activityApi.getShareInfo(activity.id);
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
  if (posterImage.value && currentActivity.value) {
    downloadFile(
      posterImage.value,
      `团购海报-${currentActivity.value.title}.png`,
    );
  }
};

const exportOrders = (activityId: string) => {
  const url = statisticsApi.exportOrdersCsv(activityId);
  window.open(url, "_blank");
};

const exportBySpec = (activityId: string) => {
  const url = statisticsApi.exportSummaryBySpecCsv(activityId);
  window.open(url, "_blank");
};

const exportByMember = (activityId: string) => {
  const url = statisticsApi.exportSummaryByMemberCsv(activityId);
  window.open(url, "_blank");
};

onMounted(() => {
  fetchActivities();
});
</script>

<style lang="scss" scoped>
.leader-activities {
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

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .activity-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      border-bottom: 1px solid #f0f0f0;

      .activity-title {
        display: flex;
        align-items: center;
        gap: 12px;

        h3 {
          font-size: 16px;
          font-weight: 600;
          color: #333;
          margin: 0;
        }
      }

      .card-actions {
        display: flex;
        gap: 8px;
      }
    }

    .card-content {
      padding: 16px 20px;

      .description {
        font-size: 14px;
        color: #666;
        margin: 0 0 16px;
        line-height: 1.6;
      }

      .activity-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 16px;
        font-size: 13px;
        color: #666;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }
      }

      .activity-stats {
        display: flex;
        gap: 40px;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;

        .stat-item {
          text-align: center;

          .stat-value {
            display: block;
            font-size: 20px;
            font-weight: 600;
            color: #ff6b6b;
          }

          .stat-label {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }

    .card-products {
      padding: 0 20px 16px;

      h4 {
        font-size: 14px;
        font-weight: 600;
        color: #333;
        margin: 0 0 12px;
      }

      .product-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .product-item {
          display: flex;
          align-items: center;
          padding: 10px;
          background: #fafafa;
          border-radius: 8px;

          .product-image {
            width: 50px;
            height: 50px;
            border-radius: 6px;
            flex-shrink: 0;
          }

          .product-info {
            flex: 1;
            margin-left: 10px;

            .product-name {
              font-size: 14px;
              color: #333;
              margin: 0 0 2px;
            }

            .product-spec {
              font-size: 12px;
              color: #999;
              margin: 0;
            }
          }

          .product-price {
            text-align: right;

            .price {
              display: block;
              font-size: 15px;
              font-weight: 600;
              color: #ff6b6b;
            }

            .stock {
              font-size: 12px;
              color: #999;
            }
          }
        }

        .more-products {
          text-align: center;
          font-size: 13px;
          color: #666;
          padding: 8px;
        }
      }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
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
