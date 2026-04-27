<template>
  <div class="activity-list-page">
    <div class="page-header">
      <h2>团购活动</h2>
      <p>精选好物，超值团购</p>
    </div>

    <div class="activity-list" v-loading="loading">
      <el-empty
        v-if="activities.length === 0 && !loading"
        description="暂无进行中的团购活动"
      />

      <div
        v-for="activity in activities"
        :key="activity.id"
        class="activity-card"
        @click="goToDetail(activity.id)"
      >
        <div class="card-image">
          <el-image
            :src="
              activity.products?.[0]?.product_image || getPlaceholderImage()
            "
            :fit="cover"
            class="activity-image"
          >
            <template #placeholder>
              <div class="image-placeholder">
                <el-icon size="48"><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </div>

        <div class="card-content">
          <h3 class="activity-title">{{ activity.title }}</h3>
          <p class="activity-desc">{{ activity.description }}</p>

          <div class="card-footer">
            <div class="price-info">
              <span class="min-price">¥{{ getMinPrice(activity) }}</span>
              <span class="participants"
                >{{ activity.participant_count }}人已参团</span
              >
            </div>

            <div class="time-info">
              <el-tag
                v-if="activity.status === 'active'"
                type="success"
                size="small"
                >进行中</el-tag
              >
              <el-tag
                v-else
                :type="getActivityStatusTag(activity.status).type"
                size="small"
              >
                {{ getActivityStatusTag(activity.status).text }}
              </el-tag>
              <span class="end-time"
                >截止: {{ formatEndTime(activity.end_time) }}</span
              >
            </div>
          </div>
        </div>

        <div class="card-extra">
          <div class="leader-info">
            <el-avatar :size="24" class="leader-avatar">
              {{ activity.leader_name?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="leader-name">{{ activity.leader_name }}</span>
          </div>
          <el-button
            type="primary"
            size="small"
            @click.stop="goToDetail(activity.id)"
          >
            立即参团
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
import { useRouter } from "vue-router";
import { activityApi } from "@/api";
import { formatDate, getActivityStatusTag } from "@/utils";
import type { GroupBuyActivity, ActivityProduct } from "@/types";
import { Picture } from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const activities = ref<GroupBuyActivity[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const fetchActivities = async () => {
  loading.value = true;
  try {
    const res = await activityApi.getActiveActivities({
      page: currentPage.value,
      page_size: pageSize.value,
    });
    activities.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取活动列表失败:", error);
  } finally {
    loading.value = false;
  }
};

const getMinPrice = (activity: GroupBuyActivity) => {
  if (!activity.products || activity.products.length === 0) return "0.00";
  const minPrice = Math.min(
    ...activity.products.map((p: ActivityProduct) => p.group_price),
  );
  return minPrice.toFixed(2);
};

const formatEndTime = (endTime: string) => {
  return formatDate(endTime, "MM-DD HH:mm");
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f5f5f5" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="20" text-anchor="middle" x="200" y="160"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const goToDetail = (id: string) => {
  router.push(`/activities/${id}`);
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

onMounted(() => {
  fetchActivities();
});
</script>

<style lang="scss" scoped>
.activity-list-page {
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

  .activity-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }

  .activity-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .card-image {
      height: 200px;
      overflow: hidden;

      .activity-image {
        width: 100%;
        height: 100%;
      }

      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        color: #ccc;
      }
    }

    .card-content {
      padding: 16px;

      .activity-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin: 0 0 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .activity-desc {
        font-size: 14px;
        color: #666;
        margin: 0 0 16px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .card-footer {
        .price-info {
          display: flex;
          align-items: baseline;
          margin-bottom: 12px;

          .min-price {
            font-size: 20px;
            font-weight: 600;
            color: #ff6b6b;
          }

          .participants {
            font-size: 12px;
            color: #999;
            margin-left: 12px;
          }
        }

        .time-info {
          display: flex;
          align-items: center;
          gap: 12px;

          .end-time {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }

    .card-extra {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-top: 1px solid #f0f0f0;

      .leader-info {
        display: flex;
        align-items: center;
        gap: 8px;

        .leader-avatar {
          background: linear-gradient(135deg, #ff6b6b, #ff8e53);
          color: #fff;
          font-size: 12px;
        }

        .leader-name {
          font-size: 12px;
          color: #666;
        }
      }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 32px;
  }
}
</style>
