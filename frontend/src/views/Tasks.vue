<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>任務列表 (Tasks)</h2>
      <div>
        <button class="btn btn-outline-primary me-2" @click="fetchTasks" :disabled="loading">
          🔄 重新整理狀態
        </button>
        <router-link to="/train" class="btn btn-success">建立新任務</router-link>
      </div>
    </div>

    <div v-if="loading && tasks.length === 0" class="text-center my-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="tasks.length === 0" class="alert alert-info text-center">
      目前沒有任何訓練任務。
    </div>

    <div v-else class="card shadow-sm">
      <ul class="list-group list-group-flush">
        <li class="list-group-item d-flex justify-content-between align-items-center" v-for="task in tasks" :key="task.id">
          <div>
            <strong>任務 #{{ task.id }}</strong>
            <br>
            <small class="text-muted">建立時間: {{ formatDate(task.created_at) }}</small>
          </div>
          
          <div class="d-flex align-items-center gap-3">
            <!-- 狀態 Badge -->
            <span class="badge" :class="statusClass(task.status)">
              {{ statusText(task.status) }}
            </span>
            
            <!-- 下載按鈕 (僅在完成時顯示) -->
            <button 
              v-if="task.status === 'completed'" 
              class="btn btn-sm btn-primary" 
              @click="handleDownload(task)"
            >
              ⬇️ 下載模型
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getTasks, downloadModel } from '../services/tasks';

const tasks = ref([]);
const loading = ref(false);

const fetchTasks = async () => {
  loading.value = true;
  try {
    const res = await getTasks();
    tasks.value = res.data;
  } catch (err) {
    console.error('獲取任務失敗', err);
  } finally {
    loading.value = false;
  }
};

const handleDownload = async (task) => {
  try {
    const res = await downloadModel(task.id);
    // 將 Blob 轉換為可供瀏覽器下載的 URL
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'self_driving_model.txt'); // 設定預設下載檔名
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url); // 釋放記憶體
  } catch (err) {
    alert('下載失敗，請確認任務狀態或查看 Console');
    console.error('下載錯誤:', err);
  }
};

// 輔助函數：狀態對應的 Bootstrap 顏色
const statusClass = (status) => {
  switch(status) {
    case 'pending': return 'bg-warning text-dark';
    case 'processing': return 'bg-info text-dark';
    case 'completed': return 'bg-success';
    case 'failed': return 'bg-danger';
    default: return 'bg-secondary';
  }
};

// 輔助函數：狀態對應的中文文字
const statusText = (status) => {
  switch(status) {
    case 'pending': return '等待中';
    case 'processing': return '訓練中...';
    case 'completed': return '已完成';
    case 'failed': return '失敗';
    default: return status;
  }
};

// 輔助函數：格式化時間
const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString();
};

onMounted(() => {
  fetchTasks();
});
</script>