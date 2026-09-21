<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>模型訓練 (Train)</h2>
      <router-link to="/dashboard" class="btn btn-outline-secondary">返回圖片管理</router-link>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-2">載入圖片列表中...</p>
    </div>

    <div v-else-if="images.length === 0" class="alert alert-warning text-center">
      沒有可用的圖片，請先至 <router-link to="/dashboard">圖片管理</router-link> 上傳檔案。
    </div>

    <div v-else>
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-light d-flex justify-content-between align-items-center">
          <span>請勾選要參與訓練的圖片 (共 {{ images.length }} 張)</span>
          <button class="btn btn-sm btn-outline-primary" @click="toggleSelectAll">
            {{ isAllSelected ? '取消全選' : '全選' }}
          </button>
        </div>
        <ul class="list-group list-group-flush">
          <li class="list-group-item d-flex align-items-center" v-for="img in images" :key="img.id">
            <input 
              class="form-check-input me-3" 
              type="checkbox" 
              :value="img.id" 
              v-model="selectedIds"
            >
            <span class="text-truncate me-2 text-primary flex-grow-1" style="cursor: pointer;" @click="openModal(img)">
              📄 {{ img.filename }}
            </span>
            <!-- 加入標記狀態 Badge -->
            <span v-if="img.is_annotated" class="badge bg-success ms-2">已標記 ({{ img.annotation_count }})</span>
            <span v-else class="badge bg-warning text-dark ms-2">未標記</span>
          </li>
        </ul>
      </div>

      <div class="d-grid gap-2">
        <button 
          class="btn btn-success btn-lg" 
          @click="handleTrain" 
          :disabled="selectedIds.length === 0 || submitting"
        >
          {{ submitting ? '提交中...' : `開始訓練 (已選 ${selectedIds.length} 張)` }}
        </button>
      </div>
    </div>

    <!-- 掛載圖片預覽 Modal -->
    <ImagePreviewModal 
      :show="showModal" 
      :image="selectedImage" 
      @close="closeModal" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getImages } from '../services/images';
import { createTask } from '../services/tasks';
import ImagePreviewModal from '../components/ImagePreviewModal.vue';

const router = useRouter();

const images = ref([]);
const selectedIds = ref([]);
const loading = ref(false);
const submitting = ref(false);

const showModal = ref(false);
const selectedImage = ref(null);

// 計算是否全選
const isAllSelected = computed(() => images.value.length > 0 && selectedIds.value.length === images.value.length);

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

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = [];
  } else {
    selectedIds.value = images.value.map(img => img.id);
  }
};

const handleTrain = async () => {
  if (selectedIds.value.length === 0) return;
  
  // 檢查是否包含未標記的圖片
  const selectedImages = images.value.filter(img => selectedIds.value.includes(img.id));
  const unannotatedCount = selectedImages.filter(img => !img.is_annotated).length;
  
  if (unannotatedCount > 0) {
    if (!confirm(`您選取的圖片中有 ${unannotatedCount} 張「未標記」，這些圖片將不會產生 YOLO 標籤檔。確定要繼續嗎？`)) {
      return;
    }
  }
  
  submitting.value = true;
  try {
    await createTask(selectedIds.value);
    alert('任務已送出，正在背景轉換 YOLO 格式並打包！即將為您跳轉至任務列表...');
    router.push('/tasks');
  } catch (err) {
    alert('提交失敗: ' + (err.response?.data?.detail || '未知錯誤'));
  } finally {
    submitting.value = false;
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