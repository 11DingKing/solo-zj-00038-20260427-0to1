<template>
  <div class="admin-products">
    <div class="page-header">
      <h2>商品管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品名称"
          clearable
          style="width: 240px"
          @clear="searchProducts"
          @keyup.enter="searchProducts"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="goToCreate">
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>
      </div>
    </div>

    <div class="product-list" v-loading="loading">
      <el-empty
        v-if="products.length === 0 && !loading"
        description="暂无商品"
      />

      <el-table :data="products" style="width: 100%" v-if="products.length > 0">
        <el-table-column label="商品信息" min-width="250">
          <template #default="scope">
            <div class="product-info">
              <el-image
                :src="scope.row.image || getPlaceholderImage()"
                :fit="cover"
                class="product-image"
              />
              <div class="product-detail">
                <p class="product-name">{{ scope.row.name }}</p>
                <p class="product-desc">{{ scope.row.description }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.is_active"
              active-text="启用"
              inactive-text="禁用"
              @change="toggleStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="规格数" width="80">
          <template #default="scope">
            {{ scope.row.specs_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="最低价格" width="120">
          <template #default="scope">
            <span class="highlight"
              >¥{{ (scope.row.min_price || 0).toFixed(2) }}</span
            >
          </template>
        </el-table-column>
        <el-table-column label="总库存" width="100">
          <template #default="scope">
            <span :class="{ 'text-danger': (scope.row.total_stock || 0) < 10 }">
              {{ scope.row.total_stock || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              link
              size="small"
              @click="goToEdit(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              @click="showSpecs(scope.row)"
            >
              规格
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="deleteProduct(scope.row)"
            >
              删除
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

    <el-dialog
      v-model="specDialogVisible"
      :title="`${currentProduct?.name || ''} - 规格管理`"
      width="600px"
    >
      <div class="spec-dialog-content">
        <div class="spec-list">
          <el-empty
            v-if="
              (!currentProduct?.specs || currentProduct.specs.length === 0) &&
              !specsLoading
            "
            description="暂无规格"
          />

          <div
            v-for="spec in currentProduct?.specs || []"
            :key="spec.id"
            class="spec-item"
          >
            <div class="spec-info">
              <p class="spec-name">{{ spec.name }}</p>
              <div class="spec-meta">
                <span class="price">价格: ¥{{ spec.price.toFixed(2) }}</span>
                <span class="stock" :class="{ 'text-danger': spec.stock < 10 }">
                  库存: {{ spec.stock }}
                </span>
                <span class="status">
                  状态:
                  <el-tag
                    :type="spec.is_active ? 'success' : 'info'"
                    size="small"
                  >
                    {{ spec.is_active ? "启用" : "禁用" }}
                  </el-tag>
                </span>
              </div>
            </div>
            <div class="spec-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="editSpec(spec)"
              >
                编辑
              </el-button>
            </div>
          </div>
        </div>

        <el-divider />

        <h4 class="form-title">
          {{ editingSpec ? "编辑规格" : "添加规格" }}
        </h4>
        <el-form :model="specForm" :rules="specRules" label-width="80px">
          <el-form-item label="规格名称" prop="name">
            <el-input
              v-model="specForm.name"
              placeholder="请输入规格名称，如：500g装、1kg装"
            />
          </el-form-item>
          <el-form-item label="价格" prop="price">
            <el-input-number
              v-model="specForm.price"
              :min="0"
              :precision="2"
              :step="1"
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="库存" prop="stock">
            <el-input-number
              v-model="specForm.stock"
              :min="0"
              :step="1"
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-switch
              v-model="specForm.is_active"
              active-text="启用"
              inactive-text="禁用"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="specSubmitting"
              @click="submitSpec"
            >
              {{ editingSpec ? "保存" : "添加" }}
            </el-button>
            <el-button @click="resetSpecForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox, type FormRules } from "element-plus";
import { productApi } from "@/api";
import type { Product, ProductSpec, PaginatedResponse } from "@/types";
import { Search, Plus } from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const products = ref<Product[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const searchKeyword = ref("");

const specDialogVisible = ref(false);
const specsLoading = ref(false);
const specSubmitting = ref(false);
const currentProduct = ref<Product | null>(null);
const editingSpec = ref<ProductSpec | null>(null);

const specForm = reactive({
  name: "",
  price: 0,
  stock: 0,
  is_active: true,
});

const specRules: FormRules = {
  name: [{ required: true, message: "请输入规格名称", trigger: "blur" }],
  price: [{ required: true, message: "请输入价格", trigger: "blur" }],
  stock: [{ required: true, message: "请输入库存", trigger: "blur" }],
};

const getPlaceholderImage = () => {
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60"%3E%3Crect fill="%23f5f5f5" width="60" height="60"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="10" text-anchor="middle" x="30" y="35"%3E暂无图片%3C/text%3E%3C/svg%3E';
};

const fetchProducts = async () => {
  loading.value = true;
  try {
    const res: PaginatedResponse<Product> = await productApi.getProducts({
      page: currentPage.value,
      page_size: pageSize.value,
    });
    products.value = res.results;
    total.value = res.count;
  } catch (error) {
    console.error("获取商品列表失败:", error);
    ElMessage.error("获取商品列表失败");
  } finally {
    loading.value = false;
  }
};

const searchProducts = () => {
  currentPage.value = 1;
  fetchProducts();
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchProducts();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchProducts();
};

const goToCreate = () => {
  router.push("/admin/products/create");
};

const goToEdit = (id: string) => {
  router.push(`/admin/products/${id}/edit`);
};

const toggleStatus = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要${product.is_active ? "禁用" : "启用"}该商品吗？`,
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    const formData = new FormData();
    formData.append("is_active", product.is_active ? "true" : "false");
    await productApi.updateProduct(product.id, formData);
    ElMessage.success("状态更新成功");
  } catch (error) {
    product.is_active = !product.is_active;
  }
};

const deleteProduct = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除商品「${product.name}」吗？删除后无法恢复。`,
      "警告",
      {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await productApi.deleteProduct(product.id);
    ElMessage.success("删除成功");
    fetchProducts();
  } catch (error) {
    // 用户取消
  }
};

const showSpecs = async (product: Product) => {
  currentProduct.value = product;
  editingSpec.value = null;
  resetSpecForm();
  specDialogVisible.value = true;

  try {
    const specs = await productApi.getProductSpecs(product.id);
    currentProduct.value.specs = specs;
  } catch (error) {
    console.error("获取规格列表失败:", error);
  }
};

const editSpec = (spec: ProductSpec) => {
  editingSpec.value = spec;
  specForm.name = spec.name;
  specForm.price = spec.price;
  specForm.stock = spec.stock;
  specForm.is_active = spec.is_active;
};

const resetSpecForm = () => {
  editingSpec.value = null;
  specForm.name = "";
  specForm.price = 0;
  specForm.stock = 0;
  specForm.is_active = true;
};

const submitSpec = async () => {
  if (!currentProduct.value) return;

  specSubmitting.value = true;
  try {
    if (editingSpec.value) {
      await productApi.updateProductSpec(editingSpec.value.id, {
        name: specForm.name,
        price: specForm.price,
        stock: specForm.stock,
        is_active: specForm.is_active,
      });
      ElMessage.success("规格更新成功");
    } else {
      await productApi.createProductSpec({
        product: currentProduct.value.id,
        name: specForm.name,
        price: specForm.price,
        stock: specForm.stock,
        is_active: specForm.is_active,
      });
      ElMessage.success("规格添加成功");
    }

    const specs = await productApi.getProductSpecs(currentProduct.value.id);
    currentProduct.value.specs = specs;
    resetSpecForm();
    fetchProducts();
  } catch (error: any) {
    const errors = error.response?.data;
    if (errors) {
      const errorMessages = Object.values(errors).flat().join("; ");
      ElMessage.error(errorMessages || "操作失败");
    } else {
      ElMessage.error("操作失败");
    }
  } finally {
    specSubmitting.value = false;
  }
};

onMounted(() => {
  fetchProducts();
});
</script>

<style lang="scss" scoped>
.admin-products {
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

  .product-list {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .product-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .product-image {
      width: 60px;
      height: 60px;
      border-radius: 6px;
      flex-shrink: 0;
    }

    .product-detail {
      .product-name {
        font-size: 14px;
        font-weight: 500;
        color: #333;
        margin: 0 0 4px;
      }

      .product-desc {
        font-size: 12px;
        color: #999;
        margin: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 200px;
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

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }

  .spec-dialog-content {
    .spec-list {
      max-height: 300px;
      overflow-y: auto;

      .spec-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        background: #fafafa;
        border-radius: 8px;
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }

        .spec-info {
          .spec-name {
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin: 0 0 6px;
          }

          .spec-meta {
            display: flex;
            gap: 16px;
            font-size: 13px;
            color: #666;

            .price {
              color: #ff6b6b;
              font-weight: 500;
            }
          }
        }
      }
    }

    .form-title {
      font-size: 15px;
      font-weight: 600;
      color: #333;
      margin: 0 0 16px;
    }
  }
}
</style>
