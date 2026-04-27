<template>
  <div class="share-page">
    <div v-if="activity" class="share-content">
      <div class="share-header">
        <div class="leader-info">
          <el-avatar :size="40" class="leader-avatar">
            {{ activity.leader_name?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="leader-detail">
            <p class="leader-name">{{ activity.leader_name }}</p>
            <p class="shop-name">
              {{ activity.leader_shop_name || "社区团购" }}
            </p>
          </div>
        </div>
        <el-button type="primary" size="small" @click="goToLogin">
          立即参团
        </el-button>
      </div>

      <div class="activity-cover">
        <el-image
          :src="activity.products?.[0]?.product_image || getPlaceholderImage()"
          :fit="cover"
          class="cover-image"
        />
      </div>

      <div class="activity-info">
        <h1 class="activity-title">{{ activity.title }}</h1>
        <p class="activity-desc">{{ activity.description }}</p>

        <div class="price-row">
          <span class="min-price">¥{{ getMinPrice(activity) }}</span>
          <span class="price-label">起</span>
          <span class="participants"
            >{{ activity.participant_count }}人已参团</span
          >
        </div>

        <div class="meta-row">
          <div class="meta-item">
            <el-icon><Clock /></el-icon>
            <span>截止时间: {{ formatDate(activity.end_time) }}</span>
          </div>
          <div class="meta-item" v-if="activity.delivery_type === 'pickup'">
            <el-icon><Location /></el-icon>
            <span>自提: {{ activity.pickup_address }}</span>
          </div>
          <div class="meta-item" v-else>
            <el-icon><Van /></el-icon>
            <span>配送上门</span>
          </div>
        </div>
      </div>

      <div class="product-section">
        <h3 class="section-title">团购商品</h3>
        <div class="product-list">
          <div
            v-for="product in activity.products"
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
              <div class="product-price">
                <span class="current-price"
                  >¥{{ product.group_price.toFixed(2) }}</span
                >
                <span
                  class="original-price"
                  v-if="product.original_price > product.group_price"
                >
                  ¥{{ product.original_price.toFixed(2) }}
                </span>
              </div>
            </div>
            <div class="product-status">
              <span
                class="stock"
                :class="{ low: product.available_stock < 10 }"
              >
                库存: {{ product.available_stock }}
              </span>
              <span class="sold">已售: {{ product.sold_quantity }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="join-section" v-if="joins.length > 0">
        <h3 class="section-title">接龙记录 ({{ joinTotal }})</h3>
        <div class="join-list">
          <div v-for="join in joins" :key="join.id" class="join-item">
            <el-avatar :size="28" class="join-avatar">
              {{ join.user_name?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div class="join-content">
              <span class="join-user">{{ join.user_name }}</span>
              <span class="join-action">购买了</span>
              <span class="join-product">{{ join.product_name }}</span>
              <span class="join-spec">({{ join.spec_name }})</span>
              <span class="join-quantity">x {{ join.quantity }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-bar">
        <div class="bar-info">
          <span class="status-text" v-if="activity.status === 'active'">
            正在火热团购中
          </span>
          <span class="status-text" v-else>
            {{ getActivityStatusTag(activity.status).text }}
          </span>
        </div>
        <el-button
          type="primary"
          size="large"
          :disabled="activity.status !== 'active'"
          @click="goToLogin"
        >
          立即参团
        </el-button>
      </div>
    </div>

    <el-empty v-else-if="!loading" description="活动不存在或已结束" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { activityApi } from "@/api";
import { formatDate, getActivityStatusTag } from "@/utils";
import type { GroupBuyActivity, GroupBuyJoin, ActivityProduct } from "@/types";
import { Clock, Location, Van } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const activity = ref<GroupBuyActivity | null>(null);
const joins = ref<GroupBuyJoin[]>([]);
const joinTotal = ref(0);

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f5f5f5" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="20" text-anchor="middle" x="200" y="160"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const getMinPrice = (act: GroupBuyActivity) => {
  if (!act.products || act.products.length === 0) return "0.00";
  const minPrice = Math.min(
    ...act.products.map((p: ActivityProduct) => p.group_price),
  );
  return minPrice.toFixed(2);
};

const fetchActivity = async () => {
  const code = route.params.code as string;
  if (!code) return;

  loading.value = true;
  try {
    activity.value = await activityApi.getActivityByShareCode(code);

    if (activity.value) {
      const joinRes = await activityApi.getActivityJoins(activity.value.id, {
        page: 1,
        page_size: 10,
      });
      joins.value = joinRes.results;
      joinTotal.value = joinRes.count;
    }
  } catch (error) {
    console.error("获取活动详情失败:", error);
    ElMessage.error("活动不存在或已结束");
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  if (!activity.value) return;

  const redirect = `/activities/${activity.value.id}`;
  router.push({
    name: "Login",
    query: { redirect },
  });
};

onMounted(() => {
  fetchActivity();
});
</script>

<style lang="scss" scoped>
.share-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 80px;

  .share-content {
    max-width: 480px;
    margin: 0 auto;
  }

  .share-header {
    background: #fff;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

    .leader-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .leader-avatar {
        background: linear-gradient(135deg, #ff6b6b, #ff8e53);
        color: #fff;
        font-weight: 600;
      }

      .leader-detail {
        .leader-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
          margin: 0;
        }

        .shop-name {
          font-size: 12px;
          color: #999;
          margin: 0;
        }
      }
    }
  }

  .activity-cover {
    background: #fff;
    padding: 0;

    .cover-image {
      width: 100%;
      height: 280px;
    }
  }

  .activity-info {
    background: #fff;
    padding: 16px;
    margin-bottom: 10px;

    .activity-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0 0 8px;
      line-height: 1.4;
    }

    .activity-desc {
      font-size: 14px;
      color: #666;
      margin: 0 0 16px;
      line-height: 1.6;
    }

    .price-row {
      display: flex;
      align-items: baseline;
      margin-bottom: 12px;

      .min-price {
        font-size: 28px;
        font-weight: 600;
        color: #ff6b6b;
      }

      .price-label {
        font-size: 14px;
        color: #999;
        margin-left: 4px;
      }

      .participants {
        font-size: 14px;
        color: #666;
        margin-left: auto;
      }
    }

    .meta-row {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #f0f0f0;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #666;
      }
    }
  }

  .product-section,
  .join-section {
    background: #fff;
    padding: 16px;
    margin-bottom: 10px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0 0 16px;
    }
  }

  .product-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .product-item {
      display: flex;
      padding: 12px;
      background: #fafafa;
      border-radius: 8px;

      .product-image {
        width: 80px;
        height: 80px;
        border-radius: 6px;
        flex-shrink: 0;
      }

      .product-info {
        flex: 1;
        margin-left: 12px;

        .product-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
          margin: 0 0 4px;
        }

        .product-spec {
          font-size: 12px;
          color: #999;
          margin: 0 0 6px;
        }

        .product-price {
          display: flex;
          align-items: baseline;
          gap: 8px;

          .current-price {
            font-size: 16px;
            font-weight: 600;
            color: #ff6b6b;
          }

          .original-price {
            font-size: 12px;
            color: #999;
            text-decoration: line-through;
          }
        }
      }

      .product-status {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        gap: 4px;
        font-size: 12px;

        .stock {
          color: #666;

          &.low {
            color: #ff6b6b;
          }
        }

        .sold {
          color: #999;
        }
      }
    }
  }

  .join-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .join-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .join-avatar {
        background: linear-gradient(135deg, #ff6b6b, #ff8e53);
        color: #fff;
        font-size: 12px;
        flex-shrink: 0;
      }

      .join-content {
        font-size: 14px;
        line-height: 1.5;

        .join-user {
          color: #333;
          font-weight: 500;
        }

        .join-action {
          color: #666;
          margin: 0 4px;
        }

        .join-product {
          color: #333;
        }

        .join-spec {
          color: #999;
          font-size: 12px;
        }

        .join-quantity {
          color: #ff6b6b;
          font-weight: 500;
          margin-left: 4px;
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
    justify-content: space-between;
    padding: 0 20px;
    z-index: 100;

    .bar-info {
      .status-text {
        font-size: 14px;
        color: #666;
      }
    }
  }
}
</style>
