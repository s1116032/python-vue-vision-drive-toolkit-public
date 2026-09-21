<template>
  <!-- 最外層強制 100% 寬度 -->
  <div id="app" 
    :style="route.meta.fullscreen 
      ? 'height: 100vh; overflow: hidden; width: 100%; display: flex; flex-direction: column;' 
      : 'min-height: 100vh; width: 100%; display: flex; flex-direction: column;'"
  >
    
    <!-- 導覽列 -->
    <nav v-if="!route.meta.hideNavbar" class="navbar navbar-expand-lg navbar-dark bg-dark mb-4" style="width: 100%;">
      <div class="px-4 w-100 d-flex align-items-center justify-content-between">
        <router-link class="navbar-brand" to="/">Vision Drive Toolkit</router-link>
        <div class="d-flex align-items-center">
          <ul class="navbar-nav me-3 d-flex flex-row gap-3" v-if="isLoggedIn">
            <li class="nav-item"><router-link class="nav-link" to="/dashboard">圖片管理</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/train">模型訓練</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/tasks">任務列表</router-link></li>
          </ul>
          <button class="btn btn-outline-light btn-sm" v-if="isLoggedIn" @click="logout">登出</button>
        </div>
      </div>
    </nav>

    <!-- 頁面內容區 -->
    <div 
      :style="route.meta.fullscreen 
        ? 'flex-grow: 1; width: 100%; padding: 0; margin: 0; overflow: hidden;' 
        : 'flex-grow: 1; width: 100%; padding: 2rem;'"
    >
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'; 
import { useRouter, useRoute } from 'vue-router'; 

const router = useRouter();
const route = useRoute(); 

const isLoggedIn = ref(!!localStorage.getItem('access_token'));

watch(() => route.path, () => {
  isLoggedIn.value = !!localStorage.getItem('access_token');
});

const logout = () => {
  localStorage.removeItem('access_token');
  isLoggedIn.value = false; 
  router.push('/login');
};
</script>

<style>
body { background-color: #f8f9fa; }
html, body, #app { margin: 0; padding: 0; height: 100%; }
</style>