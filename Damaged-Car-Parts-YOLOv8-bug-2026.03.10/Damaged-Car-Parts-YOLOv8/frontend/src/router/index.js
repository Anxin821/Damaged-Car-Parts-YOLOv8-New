import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'WechatHome',
    component: () => import('../pages/WechatHome.vue')
  },
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('../pages/WechatAIDetection.vue')
  },
  {
    path: '/pre-repair',
    name: 'PreRepairAnalysis',
    component: () => import('../pages/WechatPreRepairAnalysis.vue')
  },
  {
    path: '/wechat-dashboard',
    name: 'WechatDashboard',
    component: () => import('../pages/WechatDashboard.vue')
  },
  {
    path: '/wechat-repair-dashboard',
    name: 'WechatRepairDashboard',
    component: () => import('../pages/WechatRepairDashboard.vue')
  },
  {
    path: '/feedback',
    name: 'WechatFeedback',
    component: () => import('../pages/WechatFeedback.vue')
  },
  {
    path: '/damage-detail/:taskId',
    name: 'DamageDetail',
    component: () => import('../pages/WechatDamageDetail.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router