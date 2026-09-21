<template>
  <!-- 外層限制最大寬度 1200px 並置中 -->
  <div style="max-width: 1200px; margin: 0 auto; width: 100%;">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>圖片管理 (Dashboard)</h2>
      <div>
        <label class="btn btn-primary me-2" :class="{ disabled: uploading }">
          {{ uploading ? '上傳處理中...' : '上傳圖片/影片' }}
          <input type="file" multiple hidden @change="handleUpload" accept="image/*,video/*">
        </label>
        <button class="btn btn-warning me-2" @click="enterAnnotateMode" :disabled="selectedForAnnotate.length === 0">
          🏷️ 進入標記 ({{ selectedForAnnotate.length }})
        </button>
        <router-link to="/tasks" class="btn btn-outline-secondary me-2">查看任務</router-link>
        <router-link to="/train" class="btn btn-success">下一步 (訓練模型)</router-link>
      </div>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2">載入圖片列表中...</p>
    </div>

    <div v-else-if="images.length === 0" class="alert alert-info text-center">
      目前沒有任何圖片，請點擊上方按鈕上傳圖片或影片！
    </div>

    <!-- 圖片列表 -->
    <ul v-else class="list-group shadow-sm">
      <li class="list-group-item d-flex justify-content-between align-items-center" v-for="img in images" :key="img.id">
        <div class="d-flex align-items-center flex-grow-1 me-2">
          <input type="checkbox" class="form-check-input me-3" :checked="selectedForAnnotate.includes(img.id)" @change="toggleSelection(img.id)">
          
          <span class="text-truncate text-primary" style="cursor: pointer;" @click="openModal(img)">
            📄 {{ img.filename }}
          </span>
          
          <span v-if="img.is_annotated" class="badge bg-success ms-2">已標記 ({{ img.annotation_count }})</span>
          <span v-else class="badge bg-secondary ms-2">未標記</span>
        </div>
        
        <button class="btn btn-danger btn-sm" @click="handleDelete(img.id)" :disabled="deletingId === img.id">
          {{ deletingId === img.id ? '刪除中...' : '✕' }}
        </button>
      </li>
    </ul>

    <ImagePreviewModal :show="showModal" :image="selectedImage" @close="closeModal" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getImages, uploadImages, deleteImage } from '../services/images';
import ImagePreviewModal from '../components/ImagePreviewModal.vue';

const router = useRouter();

const images = ref([]);
const loading = ref(false);
const uploading = ref(false);
const deletingId = ref(null);

const showModal = ref(false);
const selectedImage = ref(null);

const selectedForAnnotate = ref([]);

const fetchImages = async () => {
  loading.value = true;
  try {
    const res = await getImages();
    images.value = res.data;
  } catch (err) {
    console.error(err);
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
    await fetchImages();
    alert('上傳成功！\n(注意：如果您上傳的是影片，後端正在背景進行 3 秒抽幀，請稍後重新整理頁面或稍等幾秒後查看新圖片。)');
  } catch (err) {
    let errorMsg = '未知錯誤，請查看 Console 取得詳細資訊';
    
    if (err.response) {
      const data = err.response.data;
      if (typeof data === 'string') {
        errorMsg = `伺服器錯誤 (${err.response.status})`;
      } else if (data && data.detail) {
        errorMsg = data.detail;
      }
    } else if (err.request) {
      errorMsg = '無法連線到伺服器，請檢查後端是否啟動';
    } else {
      errorMsg = err.message;
    }

    alert('上傳失敗: ' + errorMsg);
    console.error(err);
  } finally {
    uploading.value = false;
    event.target.value = '';
  }
};

const handleDelete = async (id) => {
  if (!confirm('確定要刪除這張圖片嗎？')) return;
  
  deletingId.value = id;
  try {
    await deleteImage(id);
    images.value = images.value.filter(img => img.id !== id);
    selectedForAnnotate.value = selectedForAnnotate.value.filter(imgId => imgId !== id);
  } catch (err) {
    alert('刪除失敗');
    console.error(err);
  } finally {
    deletingId.value = null;
  }
};

const toggleSelection = (id) => {
  const index = selectedForAnnotate.value.indexOf(id);
  if (index > -1) {
    selectedForAnnotate.value.splice(index, 1);
  } else {
    selectedForAnnotate.value.push(id);
  }
};

const enterAnnotateMode = () => {
  if (selectedForAnnotate.value.length === 0) {
    alert('請至少勾選一張圖片！');
    return;
  }
  router.push({ path: '/annotate', query: { ids: selectedForAnnotate.value.join(',') } });
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