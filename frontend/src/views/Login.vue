<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card shadow-sm">
        <div class="card-body p-4">
          <h3 class="card-title text-center mb-4">登入系統</h3>
          
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <!-- 如果網址列帶有 ?verified=true，顯示成功提示 -->
          <div v-if="$route.query.verified" class="alert alert-success">
            Email 驗證成功！請登入。
          </div>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="email" required>
            </div>
            <div class="mb-3">
              <label class="form-label">密碼</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-success w-100" :disabled="loading">
              {{ loading ? '登入中...' : '登入' }}
            </button>
          </form>
          
          <p class="text-center mt-3 mb-0">
            還沒有帳號？ <router-link to="/register">前往註冊</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { loginUser } from '../services/auth';

const router = useRouter();
const route = useRoute();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    const res = await loginUser(email.value, password.value);
    // 儲存 Token
    localStorage.setItem('access_token', res.data.access_token);
    // 跳轉到 Dashboard
    router.push('/dashboard');
  } catch (err) {
    error.value = err.response?.data?.detail || '登入失敗，請檢查帳密或是否已驗證 Email';
  } finally {
    loading.value = false;
  }
};
</script>