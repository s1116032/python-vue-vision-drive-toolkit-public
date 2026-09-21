import { createRouter, createWebHistory } from 'vue-router';

// 懶載入 (Lazy load) 頁面元件，增進效能
const Login = () => import('../views/Login.vue');
const Register = () => import('../views/Register.vue');
const Dashboard = () => import('../views/Dashboard.vue');
const Train = () => import('../views/Train.vue');
const Tasks = () => import('../views/Tasks.vue');
const Annotate = () => import('../views/Annotate.vue');

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true } // 標記需要驗證
  },
  {
    path: '/train',
    name: 'Train',
    component: Train,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks,
    meta: { requiresAuth: true }
  },
  {
    path: '/annotate',
    name: 'Annotate',
    component: Annotate,
    meta: { requiresAuth: true, 
            hideNavbar: true, 
            fullscreen: true
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// ==========================================
// 全域路由守衛 (Navigation Guards)
// ==========================================
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !token) {
    // 需要驗證但沒有 Token，踢回登入頁
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // 已經登入但試圖訪問登入/註冊頁，直接導向首頁
    next('/dashboard');
  } else {
    next();
  }
});

export default router;