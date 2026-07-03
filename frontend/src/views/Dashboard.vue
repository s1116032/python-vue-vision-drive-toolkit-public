<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>圖片管理 (Dashboard)</h2>
      <div>
        <!-- 上傳按鈕 (隱藏原生 input，用 label 觸發) -->
        <label class="btn btn-primary me-2" :class="{ disabled: uploading }">
          {{ uploading ? '上傳處理中...' : '上傳圖片/影片' }}
          <input type="file" multiple hidden @change="handleUpload" accept="image/*,video/*">
        </label>
        <router-link to="/tasks" class="btn btn-outline-secondary me-2">查看任務</router-link>
        <router-link to="/train" class="btn btn-success">下一步 (訓練模型)</router-link>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">載入圖片列表中...</p>
    </div>

    <!-- 空狀態 -->
    <div v-else-if="images.length === 0" class="alert alert-info text-center">
      目前沒有任何圖片，請點擊上方按鈕上傳圖片或影片！
    </div>

    <!-- 圖片列表 (不顯示縮圖，僅顯示檔名) -->
    <ul v-else class="list-group shadow-sm">
      <li class="list-group-item d-flex justify-content-between align-items-center" v-for="img in images" :key="img.id">
        <!-- 點擊檔名開啟 Modal -->
        <span class="text-truncate me-2 text-primary" style="cursor: pointer;" @click="openModal(img)">
          📄 {{ img.filename }}
        </span>
        <!-- 刪除按鈕 -->
        <button class="btn btn-danger btn-sm" @click="handleDelete(img.id)" :disabled="deletingId === img.id">
          {{ deletingId === img.id ? '刪除中...' : '✕' }}
        </button>
      </li>
    </ul>

    <!-- 掛載圖片預覽 Modal -->
    <ImagePreviewModal 
      :show="showModal" 
      :image="selectedImage" 
      @close="closeModal" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getImages, uploadImages, deleteImage } from '../services/images';
import ImagePreviewModal from '../components/ImagePreviewModal.vue';

const images = ref([]);
const loading = ref(false);
const uploading = ref(false);
const deletingId = ref(null);

const showModal = ref(false);
const selectedImage = ref(null);

const fetchImages = async () => {
  loading.value = true;
  try {
    const res = await getImages();
    images.value = res.data;
  } catch (err) {
    console.error('獲取圖片失敗', err);
  } finally {
    loading.value = false;
  }
};

const handleUpload = async (event) => {
  const files = event.target.files;
  if (!files || files.length === 0) return;
  
  uploading.value = true;
  try {
    await uploadImages(files);
    await fetchImages(); // 上傳成功後重新載入列表
    
    // 提示使用者關於影片抽幀的非同步特性
    alert('上傳成功！\n(注意：如果您上傳的是影片，後端正在背景進行 3 秒抽幀，請稍後重新整理頁面或稍等幾秒後查看新圖片。)');
  } catch (err) {
    // 1. 在 Console 印出完整的錯誤物件，方便開發者除錯
    console.error('=== 上傳失敗，完整錯誤物件 ===', err);
    
    // 2. 嘗試各種可能的錯誤路徑來取得詳細訊息
    let errorMsg = '未知錯誤，請查看 Console (F12) 取得詳細資訊';
    
    if (err.response) {
      // 情況 A: 伺服器有回應 (狀態碼 4xx, 5xx)
      const data = err.response.data;
      if (typeof data === 'string') {
        // 有時候後端崩潰 (500) 會回傳 HTML 字串或純文字，而非 JSON
        errorMsg = `伺服器錯誤 (${err.response.status}): ${data.substring(0, 100)}...`;
      } else if (data && data.detail) {
        // FastAPI 標準的 HTTPException 錯誤
        errorMsg = data.detail;
      } else {
        errorMsg = `伺服器錯誤 (${err.response.status})，但無詳細 JSON 訊息`;
      }
    } else if (err.request) {
      // 情況 B: 請求已發出但沒有收到回應 (例如 CORS 錯誤、後端沒啟動)
      errorMsg = '無法連線到伺服器，請檢查後端是否啟動或有 CORS 問題 (請看 Console 紅色錯誤)';
    } else {
      // 情況 C: 設定請求時發生的錯誤
      errorMsg = err.message;
    }

    alert('上傳失敗: ' + errorMsg);
  } finally {
    uploading.value = false;
    event.target.value = ''; // 清空 input 以便重複選擇相同檔案
  }
};

const handleDelete = async (id) => {
  if (!confirm('確定要刪除這張圖片嗎？')) return;
  
  deletingId.value = id;
  try {
    await deleteImage(id);
    // 從前端陣列中移除，不用重新打 API
    images.value = images.value.filter(img => img.id !== id);
  } catch (err) {
    alert('刪除失敗');
  } finally {
    deletingId.value = null;
  }
};

const openModal = (img) => {
  selectedImage.value = img;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedImage.value = null;
};

onMounted(() => {
  fetchImages();
});
</script>