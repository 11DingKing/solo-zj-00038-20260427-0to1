<template>
  <div class="activity-detail-page" v-loading="loading">
    <div v-if="activity" class="activity-detail">
      <div class="activity-header">
        <el-image
          :src="activity.products?.[0]?.product_image || getPlaceholderImage()"
          :fit="cover"
          class="header-image"
        >
          <template #placeholder>
            <div class="image-placeholder">
              <el-icon size="64"><Picture /></el-icon>
            </div>
          </template>
        </el-image>

        <div class="header-content">
          <h1 class="activity-title">{{ activity.title }}</h1>
          <p class="activity-description">{{ activity.description }}</p>

          <div class="activity-meta">
            <div class="meta-item">
              <el-icon><UserFilled /></el-icon>
              <span>团长: {{ activity.leader_name }}</span>
            </div>
            <div class="meta-item" v-if="activity.leader_shop_name">
              <el-icon><Shop /></el-icon>
              <span>店铺: {{ activity.leader_shop_name }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span>截止时间: {{ formatDate(activity.end_time) }}</span>
            </div>
            <div class="meta-item" v-if="activity.delivery_type === 'pickup'">
              <el-icon><Location /></el-icon>
              <span>自提点: {{ activity.pickup_address }}</span>
            </div>
          </div>

          <div class="activity-stats">
            <div class="stat-item">
              <span class="stat-value">{{ activity.participant_count }}</span>
              <span class="stat-label">已参团</span>
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
          </div>
        </div>
      </div>

      <div class="activity-section">
        <h3 class="section-title">
          <el-icon><Goods /></el-icon>
          商品列表
        </h3>

        <div class="product-list">
          <div
            v-for="product in activity.products"
            :key="product.id"
            class="product-item"
            :class="{ selected: selectedProductId === product.id }"
            @click="selectProduct(product)"
          >
            <el-image
              :src="product.product_image || getPlaceholderImage()"
              :fit="cover"
              class="product-image"
            />

            <div class="product-info">
              <h4 class="product-name">{{ product.product_name }}</h4>
              <p class="product-spec">规格: {{ product.spec_name }}</p>
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
              <div class="product-stock">
                <span
                  :class="{ 'stock-warning': product.available_stock < 10 }"
                >
                  库存: {{ product.available_stock }}
                </span>
                <span class="sold-count"
                  >已售: {{ product.sold_quantity }}</span
                >
              </div>
            </div>

            <div
              class="product-quantity"
              v-if="selectedProductId === product.id"
            >
              <el-input-number
                v-model="quantityMap[product.id]"
                :min="1"
                :max="product.limit_per_user || product.available_stock"
                size="small"
              />
              <el-button
                type="primary"
                size="small"
                @click.stop="addToCart(product)"
              >
                加入清单
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="activity-section" v-if="cart.length > 0">
        <h3 class="section-title">
          <el-icon><ShoppingCart /></el-icon>
          已选商品
        </h3>

        <div class="cart-list">
          <div v-for="item in cart" :key="item.product_id" class="cart-item">
            <span class="cart-name"
              >{{ item.product_name }} ({{ item.spec_name }})</span
            >
            <span class="cart-price"
              >¥{{ item.unit_price.toFixed(2) }} x {{ item.quantity }}</span
            >
            <el-button
              type="danger"
              size="small"
              plain
              @click="removeFromCart(item.product_id)"
            >
              删除
            </el-button>
          </div>
          <div class="cart-total">
            <span>共计: </span>
            <span class="total-amount">¥{{ cartTotal.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <div class="activity-section">
        <h3 class="section-title">
          <el-icon><List /></el-icon>
          接龙记录 ({{ joinTotal }})
        </h3>

        <div class="join-list" v-loading="joinsLoading">
          <div v-if="joins.length === 0" class="empty-joins">
            <p>暂无接龙记录，快来成为第一个参团的人吧！</p>
          </div>

          <div v-for="join in joins" :key="join.id" class="join-item">
            <div class="join-header">
              <el-avatar :size="28" class="join-avatar">
                {{ join.user_name?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="join-user">{{ join.user_name }}</span>
              <span class="join-time">{{
                formatRelativeTime(join.created_at)
              }}</span>
            </div>
            <div class="join-content">
              购买了 <span class="join-product">{{ join.product_name }}</span>
              <span class="join-spec">({{ join.spec_name }})</span>
              <span class="join-quantity">x {{ join.quantity }}</span>
              <span class="join-price"
                >共 ¥{{ (join.unit_price * join.quantity).toFixed(2) }}</span
              >
            </div>
          </div>
        </div>

        <div class="join-pagination" v-if="joinTotal > pageSize">
          <el-pagination
            v-model:current-page="joinPage"
            :page-size="pageSize"
            :total="joinTotal"
            layout="prev, pager, next"
            @current-change="handleJoinPageChange"
          />
        </div>
      </div>

      <div class="bottom-bar">
        <div class="bar-left">
          <el-button type="primary" plain @click="showShare">
            <el-icon><Share /></el-icon>
            分享
          </el-button>
        </div>
        <div class="bar-center">
          <span v-if="cart.length > 0"
            >已选 {{ cart.length }} 件，共 ¥{{ cartTotal.toFixed(2) }}</span
          >
          <span v-else>请选择商品</span>
        </div>
        <div class="bar-right">
          <el-button
            type="primary"
            :disabled="cart.length === 0"
            @click="showOrderDialog"
          >
            立即下单
          </el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="orderDialogVisible" title="确认订单" width="500px">
      <el-form :model="orderForm" :rules="orderRules" label-width="100px">
        <el-form-item label="收货人" prop="receiver_name">
          <el-input
            v-model="orderForm.receiver_name"
            placeholder="请输入收货人姓名"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="receiver_phone">
          <el-input
            v-model="orderForm.receiver_phone"
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item label="配送方式">
          <el-tag
            :type="activity.delivery_type === 'pickup' ? 'warning' : 'success'"
          >
            {{ activity.delivery_type === "pickup" ? "自提" : "配送" }}
          </el-tag>
        </el-form-item>
        <el-form-item
          label="收货地址"
          prop="delivery_address"
          v-if="activity.delivery_type === 'delivery'"
        >
          <el-input
            v-model="orderForm.delivery_address"
            type="textarea"
            :rows="2"
            placeholder="请输入详细收货地址"
          />
        </el-form-item>
        <el-form-item label="自提地址" v-else>
          <span>{{ activity.pickup_address }}</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="orderForm.remark"
            type="textarea"
            :rows="2"
            placeholder="选填，有什么需要告诉团长的？"
          />
        </el-form-item>
        <el-form-item label="商品清单">
          <div class="order-items">
            <div v-for="item in cart" :key="item.product_id" class="order-item">
              <span>{{ item.product_name }} ({{ item.spec_name }})</span>
              <span
                >¥{{ item.unit_price.toFixed(2) }} x {{ item.quantity }}</span
              >
            </div>
            <div class="order-total">
              <span>订单金额: </span>
              <span class="total-amount">¥{{ cartTotal.toFixed(2) }}</span>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitOrder">
          提交订单
        </el-button>
      </template>
    </el-dialog>

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
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { activityApi, orderApi } from "@/api";
import {
  formatDate,
  formatRelativeTime,
  generatePoster,
  downloadFile,
} from "@/utils";
import type {
  GroupBuyActivity,
  ActivityProduct,
  GroupBuyJoin,
  PaginatedResponse,
} from "@/types";
import {
  Picture,
  UserFilled,
  Shop,
  Clock,
  Location,
  Goods,
  ShoppingCart,
  List,
  Share,
  Loading,
  Download,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const activity = ref<GroupBuyActivity | null>(null);
const selectedProductId = ref<string | null>(null);
const quantityMap = reactive<Record<string, number>>({});
const cart = ref<
  {
    product_id: string;
    activity_product_id: string;
    product_name: string;
    spec_name: string;
    unit_price: number;
    quantity: number;
  }[]
>([]);

const joins = ref<GroupBuyJoin[]>([]);
const joinsLoading = ref(false);
const joinPage = ref(1);
const joinTotal = ref(0);
const pageSize = ref(20);

const orderDialogVisible = ref(false);
const submitting = ref(false);
const orderFormRef = ref<FormInstance>();
const orderForm = reactive({
  receiver_name: "",
  receiver_phone: "",
  delivery_address: "",
  remark: "",
});

const orderRules: FormRules = {
  receiver_name: [
    { required: true, message: "请输入收货人姓名", trigger: "blur" },
  ],
  receiver_phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号",
      trigger: "blur",
    },
  ],
  delivery_address: [
    { required: true, message: "请输入收货地址", trigger: "blur" },
  ],
};

const shareDialogVisible = ref(false);
const shareLink = ref("");
const posterImage = ref("");
const posterLoading = ref(false);

const cartTotal = computed(() => {
  return cart.value.reduce(
    (sum, item) => sum + item.unit_price * item.quantity,
    0,
  );
});

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f5f5f5" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="20" text-anchor="middle" x="200" y="160"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchActivity = async () => {
  const id = route.params.id as string;
  if (!id) return;

  loading.value = true;
  try {
    activity.value = await activityApi.getActivity(id);
  } catch (error) {
    console.error("获取活动详情失败:", error);
    ElMessage.error("获取活动详情失败");
  } finally {
    loading.value = false;
  }
};

const fetchJoins = async () => {
  const id = route.params.id as string;
  if (!id) return;

  joinsLoading.value = true;
  try {
    const res: PaginatedResponse<GroupBuyJoin> =
      await activityApi.getActivityJoins(id, {
        page: joinPage.value,
        page_size: pageSize.value,
      });
    joins.value = res.results;
    joinTotal.value = res.count;
  } catch (error) {
    console.error("获取接龙记录失败:", error);
  } finally {
    joinsLoading.value = false;
  }
};

const selectProduct = (product: ActivityProduct) => {
  selectedProductId.value = product.id;
  if (!quantityMap[product.id]) {
    quantityMap[product.id] = 1;
  }
};

const addToCart = (product: ActivityProduct) => {
  const quantity = quantityMap[product.id] || 1;
  const existingIndex = cart.value.findIndex(
    (item) => item.activity_product_id === product.id,
  );

  if (existingIndex >= 0) {
    cart.value[existingIndex].quantity = quantity;
  } else {
    cart.value.push({
      product_id: product.product,
      activity_product_id: product.id,
      product_name: product.product_name,
      spec_name: product.spec_name,
      unit_price: product.group_price,
      quantity: quantity,
    });
  }

  ElMessage.success("已添加到清单");
};

const removeFromCart = (productId: string) => {
  const index = cart.value.findIndex((item) => item.product_id === productId);
  if (index >= 0) {
    cart.value.splice(index, 1);
  }
};

const showOrderDialog = () => {
  if (cart.value.length === 0) {
    ElMessage.warning("请先选择商品");
    return;
  }
  orderDialogVisible.value = true;
};

const submitOrder = async () => {
  if (!orderFormRef.value) return;
  if (!activity.value) return;

  await orderFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const order = await orderApi.createOrder({
          activity_id: activity.value.id,
          items: cart.value.map((item) => ({
            activity_product_id: item.activity_product_id,
            quantity: item.quantity,
          })),
          receiver_name: orderForm.receiver_name,
          receiver_phone: orderForm.receiver_phone,
          delivery_address: orderForm.delivery_address || undefined,
          remark: orderForm.remark || undefined,
        });

        ElMessage.success("订单创建成功！");
        orderDialogVisible.value = false;

        ElMessageBox.confirm("订单创建成功！是否立即支付？", "提示", {
          confirmButtonText: "立即支付",
          cancelButtonText: "稍后支付",
          type: "success",
        })
          .then(async () => {
            try {
              await orderApi.payOrder(order.id);
              ElMessage.success("支付成功！");
              router.push(`/orders/${order.id}`);
            } catch (error: any) {
              ElMessage.error(error.response?.data?.detail || "支付失败");
            }
          })
          .catch(() => {
            router.push("/orders");
          });
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || "下单失败");
      } finally {
        submitting.value = false;
      }
    }
  });
};

const handleJoinPageChange = (page: number) => {
  joinPage.value = page;
  fetchJoins();
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
  if (posterImage.value) {
    downloadFile(posterImage.value, `团购海报-${activity.value?.title}.png`);
  }
};

onMounted(() => {
  fetchActivity();
  fetchJoins();
});
</script>

<style lang="scss" scoped>
.activity-detail-page {
  padding-bottom: 80px;

  .activity-detail {
    max-width: 900px;
    margin: 0 auto;
  }

  .activity-header {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;

    .header-image {
      width: 100%;
      height: 300px;

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

    .header-content {
      padding: 20px;

      .activity-title {
        font-size: 22px;
        font-weight: 600;
        color: #333;
        margin: 0 0 12px;
      }

      .activity-description {
        font-size: 14px;
        color: #666;
        margin: 0 0 16px;
        line-height: 1.6;
      }

      .activity-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 20px;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #666;
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
            font-size: 24px;
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
  }

  .activity-section {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
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
      align-items: center;
      padding: 12px;
      border: 2px solid #f0f0f0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;

      &.selected {
        border-color: #ff6b6b;
        background: #fff5f5;
      }

      .product-image {
        width: 80px;
        height: 80px;
        border-radius: 8px;
        flex-shrink: 0;
      }

      .product-info {
        flex: 1;
        margin-left: 12px;

        .product-name {
          font-size: 15px;
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
          margin-bottom: 4px;

          .current-price {
            font-size: 18px;
            font-weight: 600;
            color: #ff6b6b;
          }

          .original-price {
            font-size: 12px;
            color: #999;
            text-decoration: line-through;
          }
        }

        .product-stock {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #666;

          .stock-warning {
            color: #ff6b6b;
          }
        }
      }

      .product-quantity {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
      }
    }
  }

  .cart-list {
    .cart-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      .cart-name {
        flex: 1;
        font-size: 14px;
        color: #333;
      }

      .cart-price {
        font-size: 14px;
        color: #ff6b6b;
        margin-right: 16px;
      }
    }

    .cart-total {
      text-align: right;
      padding: 16px 0 0;
      font-size: 16px;
      font-weight: 500;

      .total-amount {
        color: #ff6b6b;
        font-size: 20px;
        font-weight: 600;
      }
    }
  }

  .join-list {
    .empty-joins {
      text-align: center;
      padding: 40px 0;
      color: #999;
    }

    .join-item {
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .join-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .join-avatar {
          background: linear-gradient(135deg, #ff6b6b, #ff8e53);
          color: #fff;
          font-size: 12px;
        }

        .join-user {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .join-time {
          font-size: 12px;
          color: #999;
          margin-left: auto;
        }
      }

      .join-content {
        font-size: 14px;
        color: #666;
        padding-left: 36px;

        .join-product {
          color: #333;
          font-weight: 500;
        }

        .join-spec {
          color: #999;
        }

        .join-quantity {
          color: #ff6b6b;
        }

        .join-price {
          color: #ff6b6b;
          font-weight: 500;
          margin-left: 8px;
        }
      }
    }
  }

  .join-pagination {
    display: flex;
    justify-content: center;
    margin-top: 16px;
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
    padding: 0 20px;
    z-index: 100;

    .bar-left {
      margin-right: 16px;
    }

    .bar-center {
      flex: 1;
      font-size: 14px;
      color: #666;

      .total-amount {
        font-size: 20px;
        font-weight: 600;
        color: #ff6b6b;
      }
    }

    .bar-right {
      margin-left: 16px;
    }
  }

  .order-items {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 12px;

    .order-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      font-size: 14px;
    }

    .order-total {
      display: flex;
      justify-content: flex-end;
      align-items: baseline;
      padding-top: 12px;
      border-top: 1px solid #e8e8e8;
      font-size: 14px;

      .total-amount {
        font-size: 20px;
        font-weight: 600;
        color: #ff6b6b;
        margin-left: 8px;
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
