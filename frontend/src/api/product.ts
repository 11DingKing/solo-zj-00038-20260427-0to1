import { request } from '@/utils/request'
import type { Product, ProductSpec, PaginatedResponse } from '@/types'

export const productApi = {
  getProducts: (params?: { page?: number; page_size?: number; is_active?: boolean }) =>
    request.get<PaginatedResponse<Product>>('/products/', { params }),
  
  getProduct: (id: string) => request.get<Product>(`/products/${id}/`),
  
  createProduct: (data: FormData) => request.post<Product>('/products/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  updateProduct: (id: string, data: FormData) => request.put<Product>(`/products/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  deleteProduct: (id: string) => request.delete(`/products/${id}/`),
  
  getProductSpecs: (productId?: string) => 
    request.get<ProductSpec[]>('/products/specs/', { params: { product: productId } }),
  
  createProductSpec: (data: Partial<ProductSpec>) => 
    request.post<ProductSpec>('/products/specs/', data),
  
  updateProductSpec: (id: string, data: Partial<ProductSpec>) => 
    request.put<ProductSpec>(`/products/specs/${id}/`, data),
  
  deleteProductSpec: (id: string) => request.delete(`/products/specs/${id}/`),
}