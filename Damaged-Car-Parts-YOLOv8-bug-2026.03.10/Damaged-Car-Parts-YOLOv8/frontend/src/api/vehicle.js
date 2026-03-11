import api from './request'

export const vehicleApi = {
  // 获取车型列表
  getCarModels: (params = {}) => api.get('/vehicles', { params }),
  
  // 获取车型详情
  getCarModelDetail: (id) => api.get(`/vehicles/${id}`),
  
  // 添加新车型（管理端）
  createCarModel: (data) => api.post('/vehicles', data),
  
  // 更新车型信息（管理端）
  updateCarModel: (id, data) => api.put(`/vehicles/${id}`, data),
  
  // 删除车型（管理端）
  deleteCarModel: (id) => api.delete(`/vehicles/${id}`),
  
  // 获取所有品牌列表
  getBrands: () => api.get('/vehicles/brands/list'),
  
  // 获取所有车型类型列表
  getCarTypes: () => api.get('/vehicles/types/list')
}
