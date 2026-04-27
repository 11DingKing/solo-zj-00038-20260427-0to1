<template>
  <div class="create-activity">
    <div class="page-header">
      <h2>发起新团购</h2>
      <p>创建新的团购活动，吸引更多团员参与</p>
    </div>

    <el-form
      ref="activityFormRef"
      :model="activityForm"
      :rules="activityRules"
      label-width="120px"
      class="activity-form"
    >
      <div class="form-section">
        <h3 class="section-title">基本信息</h3>

        <el-form-item label="活动标题" prop="title">
          <el-input
            v-model="activityForm.title"
            placeholder="请输入活动标题"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="活动描述" prop="description">
          <el-input
            v-model="activityForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入活动描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            :disabled-date="disabledStartDate"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="截止时间" prop="end_time">
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择截止时间"
            :disabled-date="disabledEndDate"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="配送方式" prop="delivery_type">
          <el-radio-group v-model="activityForm.delivery_type">
            <el-radio value="pickup">自提</el-radio>
            <el-radio value="delivery">配送</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="activityForm.delivery_type === 'pickup'"
          label="自提点地址"
          prop="pickup_address"
        >
          <el-input
            v-model="activityForm.pickup_address"
            type="textarea"
            :rows="2"
            placeholder="请输入自提点地址"
          />
        </el-form-item>

        <el-form-item label="起购金额" prop="min_order_amount">
          <el-input-number
            v-model="activityForm.min_order_amount"
            :min="0"
            :precision="2"
            placeholder="最低起购金额，0表示不限制"
            style="width: 200px"
          />
          <span class="form-tip">元（0表示不限制）</span>
        </el-form-item>
      </div>

      <div class="form-section">
        <h3 class="section-title">选择商品</h3>
        <p class="section-desc">
          从商品库中选择要团购的商品，设置团购价格和限购数量
        </p>

        <div class="product-selector">
          <div class="selector-header">
            <el-input
              v-model="productSearch"
              placeholder="搜索商品名称"
              style="width: 300px"
              clearable
              @clear="searchProducts"
              @keyup.enter="searchProducts"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="searchProducts"> 搜索 </el-button>
          </div>

          <div class="available-products" v-loading="productsLoading">
            <div
              v-for="product in availableProducts"
              :key="product.id"
              class="product-item"
            >
              <el-image
                :src="product.image || getPlaceholderImage()"
                :fit="cover"
                class="product-image"
              />
              <div class="product-info">
                <h4 class="product-name">{{ product.name }}</h4>
                <p class="product-desc">{{ product.description }}</p>
                <div class="spec-list">
                  <div
                    v-for="spec in product.specs"
                    :key="spec.id"
                    class="spec-item"
                    :class="{
                      selected: isProductSelected(product.id, spec.id),
                    }"
                  >
                    <span class="spec-name">{{ spec.name }}</span>
                    <span class="spec-price">¥{{ spec.price.toFixed(2) }}</span>
                    <span class="spec-stock">库存: {{ spec.stock }}</span>
                    <el-button
                      v-if="!isProductSelected(product.id, spec.id)"
                      type="primary"
                      size="small"
                      :disabled="spec.stock <= 0"
                      @click="addProduct(product, spec)"
                    >
                      添加
                    </el-button>
                    <el-button
                      v-else
                      type="danger"
                      size="small"
                      text
                      @click="removeProduct(product.id, spec.id)"
                    >
                      移除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="selected-products" v-if="activityForm.products.length > 0">
          <h4 class="selected-title">
            已选商品 ({{ activityForm.products.length }})
          </h4>
          <div class="selected-list">
            <div
              v-for="(item, index) in activityForm.products"
              :key="`${item.product}_${item.product_spec}`"
              class="selected-item"
            >
              <div class="item-info">
                <el-image
                  :src="
                    getSelectedProductImage(item.product, item.product_spec)
                  "
                  :fit="cover"
                  class="item-image"
                />
                <div class="item-detail">
                  <p class="item-name">
                    {{
                      getSelectedProductName(item.product, item.product_spec)
                    }}
                  </p>
                  <p class="item-spec">
                    {{ getSelectedSpecName(item.product_spec) }}
                  </p>
                </div>
              </div>
              <div class="item-settings">
                <el-form-item
                  label="团购价"
                  :prop="`products.${index}.group_price`"
                >
                  <el-input-number
                    v-model="item.group_price"
                    :min="0"
                    :precision="2"
                    :step="1"
                    style="width: 150px"
                  />
                </el-form-item>
                <el-form-item
                  label="限购数量"
                  :prop="`products.${index}.limit_per_user`"
                >
                  <el-input-number
                    v-model="item.limit_per_user"
                    :min="0"
                    :step="1"
                    placeholder="0表示不限"
                    style="width: 150px"
                  />
                  <span class="form-tip">（0表示不限）</span>
                </el-form-item>
              </div>
              <el-button
                type="danger"
                size="small"
                text
                @click="removeProduct(item.product, item.product_spec)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <el-button @click="resetForm">重置</el-button>
        <el-button type="primary" :loading="submitting" @click="submitActivity">
          发布活动
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ElMessage,
  type FormInstance,
  type FormRules,
  type FormRulesMap,
} from "element-plus";
import { activityApi, productApi } from "@/api";
import type { Product, ProductSpec } from "@/types";
import { Search, Delete } from "@element-plus/icons-vue";
import dayjs from "dayjs";

const router = useRouter();

const activityFormRef = ref<FormInstance>();
const submitting = ref(false);
const productsLoading = ref(false);
const productSearch = ref("");

const availableProducts = ref<Product[]>([]);
const allProducts = ref<Product[]>([]);

const activityForm = reactive({
  title: "",
  description: "",
  start_time: dayjs().add(1, "hour").format("YYYY-MM-DD HH:mm:ss"),
  end_time: dayjs().add(7, "day").format("YYYY-MM-DD HH:mm:ss"),
  delivery_type: "pickup" as "pickup" | "delivery",
  pickup_address: "",
  min_order_amount: 0,
  products: [] as {
    product: string;
    product_spec: string;
    group_price: number;
    limit_per_user: number;
    original_price: number;
  }[],
});

const validateProducts = (rule: any, value: any, callback: any) => {
  if (activityForm.products.length === 0) {
    callback(new Error("请至少选择一个商品"));
  } else {
    const invalidPrice = activityForm.products.some((p) => p.group_price <= 0);
    if (invalidPrice) {
      callback(new Error("请设置有效的团购价格"));
    } else {
      callback();
    }
  }
};

const validateEndTime = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error("请选择截止时间"));
  } else if (dayjs(value).isBefore(dayjs(activityForm.start_time))) {
    callback(new Error("截止时间必须晚于开始时间"));
  } else {
    callback();
  }
};

const activityRules: FormRules = {
  title: [
    { required: true, message: "请输入活动标题", trigger: "blur" },
    { min: 2, max: 50, message: "标题长度为 2-50 个字符", trigger: "blur" },
  ],
  description: [{ required: true, message: "请输入活动描述", trigger: "blur" }],
  start_time: [
    { required: true, message: "请选择开始时间", trigger: "change" },
  ],
  end_time: [
    { required: true, message: "请选择截止时间", trigger: "change" },
    { validator: validateEndTime, trigger: "change" },
  ],
  delivery_type: [
    { required: true, message: "请选择配送方式", trigger: "change" },
  ],
  pickup_address: [
    { required: true, message: "请输入自提点地址", trigger: "blur" },
  ],
  products: [{ validator: validateProducts, trigger: "change" }],
};

const disabledStartDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7;
};

const disabledEndDate = (time: Date) => {
  return time.getTime() < dayjs(activityForm.start_time).valueOf();
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect fill="%23f5f5f5" width="80" height="80"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="12" text-anchor="middle" x="40" y="45"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchProducts = async () => {
  productsLoading.value = true;
  try {
    const res = await productApi.getProducts({
      is_active: true,
      page_size: 100,
    });
    allProducts.value = res.results;
    availableProducts.value = res.results;
  } catch (error) {
    console.error("获取商品列表失败:", error);
    ElMessage.error("获取商品列表失败");
  } finally {
    productsLoading.value = false;
  }
};

const searchProducts = () => {
  if (!productSearch.value) {
    availableProducts.value = allProducts.value;
    return;
  }
  const keyword = productSearch.value.toLowerCase();
  availableProducts.value = allProducts.value.filter(
    (p) =>
      p.name.toLowerCase().includes(keyword) ||
      p.description.toLowerCase().includes(keyword),
  );
};

const isProductSelected = (productId: string, specId: string) => {
  return activityForm.products.some(
    (p) => p.product === productId && p.product_spec === specId,
  );
};

const addProduct = (product: Product, spec: ProductSpec) => {
  if (isProductSelected(product.id, spec.id)) return;

  activityForm.products.push({
    product: product.id,
    product_spec: spec.id,
    group_price: spec.price,
    limit_per_user: 0,
    original_price: spec.price,
  });
};

const removeProduct = (productId: string, specId: string) => {
  const index = activityForm.products.findIndex(
    (p) => p.product === productId && p.product_spec === specId,
  );
  if (index >= 0) {
    activityForm.products.splice(index, 1);
  }
};

const getSelectedProductImage = (productId: string, specId: string) => {
  const product = allProducts.value.find((p) => p.id === productId);
  return product?.image || getPlaceholderImage();
};

const getSelectedProductName = (productId: string, specId: string) => {
  const product = allProducts.value.find((p) => p.id === productId);
  return product?.name || "未知商品";
};

const getSelectedSpecName = (specId: string) => {
  for (const product of allProducts.value) {
    const spec = product.specs?.find((s) => s.id === specId);
    if (spec) return spec.name;
  }
  return "未知规格";
};

const resetForm = () => {
  activityForm.title = "";
  activityForm.description = "";
  activityForm.start_time = dayjs()
    .add(1, "hour")
    .format("YYYY-MM-DD HH:mm:ss");
  activityForm.end_time = dayjs().add(7, "day").format("YYYY-MM-DD HH:mm:ss");
  activityForm.delivery_type = "pickup";
  activityForm.pickup_address = "";
  activityForm.min_order_amount = 0;
  activityForm.products = [];
};

const submitActivity = async () => {
  if (!activityFormRef.value) return;

  await activityFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const data = {
          title: activityForm.title,
          description: activityForm.description,
          start_time: activityForm.start_time,
          end_time: activityForm.end_time,
          delivery_type: activityForm.delivery_type,
          pickup_address: activityForm.pickup_address,
          min_order_amount: activityForm.min_order_amount,
          products: activityForm.products.map((p) => ({
            product: p.product,
            product_spec: p.product_spec,
            group_price: p.group_price,
            limit_per_user: p.limit_per_user > 0 ? p.limit_per_user : undefined,
          })),
        };

        const activity = await activityApi.createActivity(data);

        ElMessage.success("活动创建成功！正在发布...");

        const publishRes = await activityApi.publishActivity(activity.id);

        ElMessage.success("活动发布成功！");
        router.push("/leader/activities");
      } catch (error: any) {
        const errors = error.response?.data;
        if (errors) {
          const errorMessages = Object.values(errors).flat().join("; ");
          ElMessage.error(errorMessages || "创建活动失败");
        } else {
          ElMessage.error("创建活动失败");
        }
      } finally {
        submitting.value = false;
      }
    }
  });
};

onMounted(() => {
  fetchProducts();
});
</script>

<style lang="scss" scoped>
.create-activity {
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

  .activity-form {
    max-width: 900px;

    .form-section {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin: 0 0 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #f0f0f0;
      }

      .section-desc {
        font-size: 13px;
        color: #999;
        margin: -12px 0 20px;
      }

      .form-tip {
        font-size: 13px;
        color: #999;
        margin-left: 8px;
      }
    }

    .product-selector {
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      overflow: hidden;

      .selector-header {
        display: flex;
        gap: 12px;
        padding: 16px;
        background: #fafafa;
        border-bottom: 1px solid #e8e8e8;
      }

      .available-products {
        max-height: 400px;
        overflow-y: auto;

        .product-item {
          display: flex;
          padding: 16px;
          border-bottom: 1px solid #f0f0f0;

          &:last-child {
            border-bottom: none;
          }

          .product-image {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            flex-shrink: 0;
          }

          .product-info {
            flex: 1;
            margin-left: 16px;

            .product-name {
              font-size: 15px;
              font-weight: 500;
              color: #333;
              margin: 0 0 4px;
            }

            .product-desc {
              font-size: 13px;
              color: #999;
              margin: 0 0 8px;
            }

            .spec-list {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;

              .spec-item {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: #fafafa;
                border-radius: 6px;
                font-size: 13px;
                border: 1px solid #f0f0f0;

                &.selected {
                  background: #fff5f5;
                  border-color: #ff6b6b;
                }

                .spec-name {
                  font-weight: 500;
                }

                .spec-price {
                  color: #ff6b6b;
                  font-weight: 500;
                }

                .spec-stock {
                  color: #999;
                }
              }
            }
          }
        }
      }
    }

    .selected-products {
      margin-top: 20px;

      .selected-title {
        font-size: 15px;
        font-weight: 600;
        color: #333;
        margin: 0 0 12px;
      }

      .selected-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .selected-item {
          display: flex;
          align-items: center;
          padding: 16px;
          background: #fafafa;
          border-radius: 8px;

          .item-info {
            display: flex;
            align-items: center;
            gap: 12px;

            .item-image {
              width: 60px;
              height: 60px;
              border-radius: 6px;
            }

            .item-detail {
              .item-name {
                font-size: 14px;
                font-weight: 500;
                color: #333;
                margin: 0 0 4px;
              }

              .item-spec {
                font-size: 12px;
                color: #999;
                margin: 0;
              }
            }
          }

          .item-settings {
            flex: 1;
            display: flex;
            gap: 20px;
            margin-left: 20px;

            .el-form-item {
              margin-bottom: 0;

              .el-form-item__label {
                font-size: 13px;
                padding: 0 8px 0 0;
                line-height: 32px;
              }
            }

            .form-tip {
              font-size: 12px;
              color: #999;
            }
          }
        }
      }
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 20px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
  }
}
</style>
