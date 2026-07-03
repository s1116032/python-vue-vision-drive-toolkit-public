<template>
  <div id="app">
    <!-- 導覽列 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container">
        <router-link class="navbar-brand" to="/">Vision Drive Toolkit</router-link>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto" v-if="isLoggedIn">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">圖片管理</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/train">模型訓練</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/tasks">任務列表</router-link>
            </li>
          </ul>
          <button class="btn btn-outline-light btn-sm" v-if="isLoggedIn" @click="logout">登出</button>
        </div>
      </div>
    </nav>

    <!-- 頁面內容區 -->
    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'; 
import { useRouter, useRoute } from 'vue-router'; 

const router = useRouter();
const route = useRoute(); // 取得當前路由物件

// 使用 ref 儲存狀態，並在初始化時讀取一次
const isLoggedIn = ref(!!localStorage.getItem('access_token'));

watch(() => route.path, () => {
  // 每次 URL 改變時 (例如登入成功跳轉、登出跳轉)，重新檢查 Token 並更新狀態
  isLoggedIn.value = !!localStorage.getItem('access_token');
});

const logout = () => {
  localStorage.removeItem('access_token');
  isLoggedIn.value = false; // 登出時更新狀態
  router.push('/login');
};
</script>

<style>
/* 可以加一些全域樣式 */
body {
  background-color: #f8f9fa;
}
</style>