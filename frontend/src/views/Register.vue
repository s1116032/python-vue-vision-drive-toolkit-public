<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card shadow-sm">
        <div class="card-body p-4">
          <h3 class="card-title text-center mb-4">建立帳號</h3>
          
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">
            註冊成功！請至後端終端機 (Terminal) 查看並點擊 Email 驗證連結。
          </div>

          <form @submit.prevent="handleRegister">
            <div class="mb-3">
              <label class="form-label">姓名</label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="form.email" required>
            </div>
            <div class="mb-3">
              <label class="form-label">密碼</label>
              <input type="password" class="form-control" v-model="form.password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              {{ loading ? '註冊中...' : '註冊' }}
            </button>
          </form>
          
          <p class="text-center mt-3 mb-0">
            已經有帳號了？ <router-link to="/login">前往登入</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { registerUser } from '../services/auth';

const form = reactive({ name: '', email: '', password: '' });
const loading = ref(false);
const error = ref('');
const success = ref(false);

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  success.value = false;
  try {
    await registerUser(form);
    success.value = true;
    form.name = '';
    form.email = '';
    form.password = '';
  } catch (err) {
    error.value = err.response?.data?.detail || '註冊失敗，請稍後再試';
  } finally {
    loading.value = false;
  }
};
</script>