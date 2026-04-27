<template>
  <div class="admin-product-form">
    <div class="page-header">
      <el-button type="primary" plain @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h2>{{ isEdit ? "编辑商品" : "添加商品" }}</h2>
    </div>

    <div class="form-container">
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="120px"
        class="product-form"
      >
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>

          <el-form-item label="商品名称" prop="name">
            <el-input
              v-model="productForm.name"
              placeholder="请输入商品名称"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="商品图片" prop="image">
            <div class="image-uploader">
              <el-upload
                class="image-upload"
                drag
                action="#"
                :auto-upload="false"
                :on-change="handleImageChange"
                :limit="1"
                accept="image/*"
              >
                <el-icon class="el-icon--upload"><Upload /></el-icon>
                <div class="el-upload__text">
                  将图片拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 jpg、png 格式，建议尺寸 400x300
                  </div>
                </template>
              </el-upload>

              <div class="image-preview" v-if="previewImage">
                <el-image
                  :src="previewImage"
                  :fit="cover"
                  class="preview-image"
                />
                <el-button
                  type="danger"
                  size="small"
                  plain
                  @click="removeImage"
                >
                  删除
                </el-button>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="商品描述" prop="description">
            <el-input
              v-model="productForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入商品描述"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="商品状态">
            <el-switch
              v-model="productForm.is_active"
              active-text="启用"
              inactive-text="禁用"
            />
            <span class="form-tip">禁用后该商品将无法被选择</span>
          </el-form-item>
        </div>

        <div class="form-section">
          <h3 class="section-title">规格列表</h3>
          <p class="section-desc">
            一个商品可以有多个规格，每个规格有独立的价格和库存
          </p>

          <div class="specs-list" v-if="productForm.specs.length > 0">
            <div
              v-for="(spec, index) in productForm.specs"
              :key="index"
              class="spec-item"
            >
              <div class="spec-header">
                <span class="spec-index">规格 {{ index + 1 }}</span>
                <el-button
                  type="danger"
                  text
                  size="small"
                  @click="removeSpec(index)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>

              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="规格名称">
                    <el-input
                      v-model="spec.name"
                      placeholder="如：500g装、1kg装"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="价格">
                    <el-input-number
                      v-model="spec.price"
                      :min="0"
                      :precision="2"
                      :step="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="库存">
                    <el-input-number
                      v-model="spec.stock"
                      :min="0"
                      :step="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="状态">
                    <el-switch
                      v-model="spec.is_active"
                      active-text="启用"
                      inactive-text="禁用"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </div>

          <el-empty
            v-if="productForm.specs.length === 0"
            description="请添加商品规格"
            :image-size="60"
          />

          <div class="add-spec-btn">
            <el-button type="primary" plain @click="addSpec">
              <el-icon><Plus /></el-icon>
              添加规格
            </el-button>
          </div>
        </div>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button
            type="primary"
            :loading="submitting"
            @click="submitProduct"
          >
            {{ isEdit ? "保存修改" : "添加商品" }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElMessage,
  type FormInstance,
  type FormRules,
  type UploadFile,
} from "element-plus";
import { productApi } from "@/api";
import type { Product, ProductSpec } from "@/types";
import { ArrowLeft, Upload, Delete, Plus } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();

const productFormRef = ref<FormInstance>();
const submitting = ref(false);
const previewImage = ref("");
const imageFile = ref<File | null>(null);

const isEdit = computed(() => !!route.params.id);

const productForm = reactive({
  name: "",
  description: "",
  is_active: true,
  specs: [] as {
    id?: string;
    name: string;
    price: number;
    stock: number;
    is_active: boolean;
  }[],
});

const productRules: FormRules = {
  name: [
    { required: true, message: "请输入商品名称", trigger: "blur" },
    { min: 2, max: 50, message: "商品名称长度为 2-50 个字符", trigger: "blur" },
  ],
  description: [{ required: true, message: "请输入商品描述", trigger: "blur" }],
};

const goBack = () => {
  router.push("/admin/products");
};

const handleImageChange = (file: UploadFile) => {
  if (file.raw) {
    imageFile.value = file.raw;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.value = e.target?.result as string;
    };
    reader.readAsDataURL(file.raw);
  }
};

const removeImage = () => {
  previewImage.value = "";
  imageFile.value = null;
};

const addSpec = () => {
  productForm.specs.push({
    name: "",
    price: 0,
    stock: 0,
    is_active: true,
  });
};

const removeSpec = (index: number) => {
  productForm.specs.splice(index, 1);
};

const fetchProduct = async () => {
  const id = route.params.id as string;
  if (!id) return;

  try {
    const product: Product = await productApi.getProduct(id);
    productForm.name = product.name;
    productForm.description = product.description;
    productForm.is_active = product.is_active;
    previewImage.value = product.image || "";

    if (product.specs && product.specs.length > 0) {
      productForm.specs = product.specs.map((spec: ProductSpec) => ({
        id: spec.id,
        name: spec.name,
        price: spec.price,
        stock: spec.stock,
        is_active: spec.is_active,
      }));
    }
  } catch (error) {
    console.error("获取商品详情失败:", error);
    ElMessage.error("获取商品详情失败");
    goBack();
  }
};

const validateForm = (): boolean => {
  if (productForm.specs.length === 0) {
    ElMessage.warning("请至少添加一个商品规格");
    return false;
  }

  const invalidSpec = productForm.specs.find(
    (spec) => !spec.name || spec.price < 0,
  );
  if (invalidSpec) {
    ElMessage.warning("请完善规格信息");
    return false;
  }

  return true;
};

const submitProduct = async () => {
  if (!productFormRef.value) return;

  await productFormRef.value.validate(async (valid) => {
    if (!valid || !validateForm()) return;

    submitting.value = true;
    try {
      const formData = new FormData();
      formData.append("name", productForm.name);
      formData.append("description", productForm.description);
      formData.append("is_active", productForm.is_active ? "true" : "false");

      if (imageFile.value) {
        formData.append("image", imageFile.value);
      }

      const specsJson = productForm.specs.map((spec) => ({
        id: spec.id,
        name: spec.name,
        price: spec.price,
        stock: spec.stock,
        is_active: spec.is_active,
      }));
      formData.append("specs", JSON.stringify(specsJson));

      if (isEdit.value) {
        await productApi.updateProduct(route.params.id as string, formData);
        ElMessage.success("商品更新成功");
      } else {
        await productApi.createProduct(formData);
        ElMessage.success("商品添加成功");
      }

      goBack();
    } catch (error: any) {
      const errors = error.response?.data;
      if (errors) {
        const errorMessages = Object.values(errors).flat().join("; ");
        ElMessage.error(errorMessages || "操作失败");
      } else {
        ElMessage.error("操作失败");
      }
    } finally {
      submitting.value = false;
    }
  });
};

onMounted(() => {
  if (isEdit.value) {
    fetchProduct();
  }
});
</script>

<style lang="scss" scoped>
.admin-product-form {
  .page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .form-container {
    max-width: 900px;

    .product-form {
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
          margin: 0 0 8px;
          padding-bottom: 12px;
          border-bottom: 2px solid #f0f0f0;
        }

        .section-desc {
          font-size: 13px;
          color: #999;
          margin: -4px 0 20px;
        }

        .form-tip {
          font-size: 13px;
          color: #999;
          margin-left: 12px;
        }
      }

      .image-uploader {
        display: flex;
        gap: 20px;

        .image-upload {
          width: 200px;

          :deep(.el-upload-dragger) {
            width: 200px;
            height: 150px;
          }
        }

        .image-preview {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;

          .preview-image {
            width: 200px;
            height: 150px;
            border-radius: 8px;
            border: 1px solid #e8e8e8;
          }
        }
      }

      .specs-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 16px;

        .spec-item {
          padding: 16px;
          background: #fafafa;
          border-radius: 8px;
          border: 1px solid #e8e8e8;

          .spec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e8e8e8;

            .spec-index {
              font-size: 14px;
              font-weight: 500;
              color: #333;
            }
          }
        }
      }

      .add-spec-btn {
        text-align: center;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
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
}
</style>
