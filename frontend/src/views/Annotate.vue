<template>
  <div class="bg-dark d-flex flex-column" style="height: 100vh; overflow: hidden;">
    
    <!-- 頂部工具列-->
    <div class="px-3 bg-secondary text-white d-flex justify-content-between align-items-center border-bottom border-dark" style="height: 56px; flex-shrink: 0;">
      <h5 class="mb-0">標記工作區 ({{ currentIndex + 1 }} / {{ imageIds.length }})</h5>
      <div>
        <button class="btn btn-sm btn-outline-light me-2" @click="prevImage" :disabled="currentIndex === 0">⬅️ 上一張</button>
        <button class="btn btn-sm btn-outline-light me-2" @click="nextImage" :disabled="currentIndex === imageIds.length - 1">下一張 ➡️</button>
        <button class="btn btn-sm btn-outline-warning me-2" @click="cancelCurrentDrawing" v-if="isDrawing || tempPoints.length > 0">✖️ 取消繪製 (Esc)</button>
        <button class="btn btn-sm btn-success" @click="saveAndExit">💾 儲存並離開</button>
      </div>
    </div>

    <!-- 主體內容區 -->
    <div class="d-flex w-100" style="height: calc(100vh - 56px); overflow: hidden;">
      
      <!-- 左側畫布 -->
      <div class="flex-grow-1 bg-dark d-flex align-items-center justify-content-center" style="height: 100%; overflow: hidden; padding: 1.5rem; box-sizing: border-box;">
        
        <div v-if="loadingImg" class="text-white position-absolute" style="z-index: 10; font-size: 1.5rem;">
          <div class="spinner-border text-light me-2" role="status"></div> 載入圖片中...
        </div>
        
        <div v-if="imgError" class="text-danger position-absolute" style="z-index: 10; font-size: 1.5rem;">
          ⚠️ 圖片載入失敗
        </div>

        <div class="position-relative" style="max-width: 100%; max-height: 100%; line-height: 0;">
          <img 
            ref="imgRef" :src="imgSrc" 
            :style="{ opacity: loadingImg || imgError ? 0 : 1, transition: 'opacity 0.2s' }"
            style="display: block; max-width: 100%; max-height: calc(100vh - 56px - 3rem); object-fit: contain;"
            @load="onImageLoad" @error="onImageError" @mousedown="preventDrag"
          >
          
          <!-- SVG 覆蓋層 -->
          <svg 
            v-if="!loadingImg && !imgError" ref="svgRef"
            class="position-absolute top-0 start-0 w-100 h-100"
            @mousedown="onSvgMouseDown" @mousemove="onSvgMouseMove" @mouseup="onSvgMouseUp"
            style="cursor: crosshair;"
          >
            <!-- 已存在的標記 -->
            <g v-for="ann in annotations" :key="ann.id" @mousedown.stop="selectAnnotation(ann)">
              <rect v-if="ann.type === 'bbox'"
                :x="ann.x * displayWidth" :y="ann.y * displayHeight" 
                :width="ann.w * displayWidth" :height="ann.h * displayHeight"
                :fill="selectedAnnId === ann.id ? 'rgba(255, 255, 0, 0.3)' : 'rgba(0, 255, 0, 0.2)'"
                stroke="lime" stroke-width="2" style="cursor: pointer;"
              />
              <polygon v-if="ann.type === 'polygon'"
                :points="ann.points.map(p => `${p[0]*displayWidth},${p[1]*displayHeight}`).join(' ')"
                :fill="selectedAnnId === ann.id ? 'rgba(255, 255, 0, 0.3)' : 'rgba(0, 128, 255, 0.3)'"
                stroke="cyan" stroke-width="2" style="cursor: pointer;"
              />
              <text 
                :x="(ann.type === 'bbox' ? ann.x : ann.points[0][0]) * displayWidth" 
                :y="(ann.type === 'bbox' ? ann.y : ann.points[0][1]) * displayHeight - 5" 
                fill="white" font-size="14" 
                style="pointer-events: none; text-shadow: 1px 1px 2px black;"
              >
                {{ ann.category_name }}
              </text>
            </g>

            <!-- 2. 繪製中的 BBox -->
            <rect v-if="isDrawing && tempBox"
              :x="tempBox.x * displayWidth" :y="tempBox.y * displayHeight" 
              :width="tempBox.w * displayWidth" :height="tempBox.h * displayHeight"
              fill="rgba(255, 255, 255, 0.2)" stroke="white" stroke-width="2" stroke-dasharray="5,5"
            />

            <!-- 3. 繪製中的 Polygon -->
            <g v-if="currentTool === 'polygon' && tempPoints.length > 0">
              <polyline 
                :points="tempPoints.map(p => `${p.x*displayWidth},${p.y*displayHeight}`).join(' ')" 
                fill="none" stroke="cyan" stroke-width="2" stroke-dasharray="5,5"
              />
              <circle v-for="(p, index) in tempPoints" :key="index"
                :cx="p.x * displayWidth" :cy="p.y * displayHeight" r="4" fill="white" stroke="cyan" stroke-width="2"
              />
              <line v-if="mousePos"
                :x1="tempPoints[tempPoints.length - 1].x * displayWidth" 
                :y1="tempPoints[tempPoints.length - 1].y * displayHeight"
                :x2="mousePos.x * displayWidth" :y2="mousePos.y * displayHeight"
                stroke="cyan" stroke-width="2" stroke-dasharray="5,5" style="pointer-events: none;"
              />
            </g>
          </svg>
        </div>
      </div>

      <!-- 右側工具列 -->
      <div class="bg-light p-3 overflow-auto border-start" style="width: 300px; flex-shrink: 0; height: 100%;">
        <h5>工具</h5>
        <div class="btn-group w-100 mb-3">
          <button class="btn" :class="currentTool === 'bbox' ? 'btn-primary' : 'btn-outline-primary'" @click="switchTool('bbox')">🟩 BBox</button>
          <button class="btn" :class="currentTool === 'polygon' ? 'btn-primary' : 'btn-outline-primary'" @click="switchTool('polygon')">🔷 Polygon</button>
        </div>

        <h5>目前類別 (Sticky)</h5>
        <select class="form-select mb-3" v-model="selectedCategoryId" @change="onCategoryChange">
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>

        <hr>
        <h5 class="d-flex justify-content-between">
          標記列表 ({{ annotations.length }})
          <button class="btn btn-sm btn-outline-danger" @click="clearAllAnnotations" :disabled="annotations.length === 0">清空</button>
        </h5>
        <ul class="list-group">
          <li class="list-group-item d-flex justify-content-between align-items-center" 
              v-for="ann in annotations" :key="ann.id"
              :class="{ 'active': selectedAnnId === ann.id }"
              @click="selectAnnotation(ann)" style="cursor: pointer;">
            <span class="text-truncate">{{ ann.type === 'bbox' ? '🟩' : '🔷' }} {{ ann.category_name }}</span>
            <button class="btn btn-sm btn-danger" @click.stop="deleteAnnotation(ann.id)">✕</button>
          </li>
        </ul>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { v4 as uuidv4 } from 'uuid';
import { getImages, getAnnotations, updateAnnotations, getCategories } from '../services/images';

const route = useRoute();
const router = useRouter();

const imageIds = ref([]);
const currentIndex = ref(0);
const imgSrc = ref('');
const annotations = ref([]);
const categories = ref([]);
const selectedCategoryId = ref(0);
const currentTool = ref('bbox');
const selectedAnnId = ref(null);

const imgRef = ref(null);
const svgRef = ref(null);
const displayWidth = ref(0);
const displayHeight = ref(0);
const loadingImg = ref(true);
const imgError = ref(false);

const isDrawing = ref(false);
const startPoint = ref({ x: 0, y: 0 });
const tempBox = ref(null);

const tempPoints = ref([]);
const mousePos = ref(null);

const handleResize = () => {
  if (imgRef.value) onImageLoad();
};

onMounted(async () => {
  window.addEventListener('resize', handleResize);
  
  window.addEventListener('keydown', handleKeydown);

  const catRes = await getCategories();
  categories.value = catRes.data;
  if (categories.value.length > 0) selectedCategoryId.value = categories.value[0].id;

  const idsQuery = route.query.ids;
  if (idsQuery) {
    imageIds.value = idsQuery.split(',').map(id => parseInt(id));
  } else {
    const imgRes = await getImages();
    imageIds.value = imgRes.data.map(img => img.id);
  }
  
  if (imageIds.value.length > 0) await loadImageAndAnnotations();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('keydown', handleKeydown);
});

const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    cancelCurrentDrawing();
  } else if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectedAnnId.value) {
      deleteAnnotation(selectedAnnId.value);
    }
  }
};

// --- 核心邏輯 ---
const loadImageAndAnnotations = async () => {
  loadingImg.value = true;
  imgError.value = false;
  cancelCurrentDrawing(); // 切換圖片時清空暫存狀態
  
  const currentId = imageIds.value[currentIndex.value];
  const token = localStorage.getItem('access_token');
  imgSrc.value = `/api/images/${currentId}/file?token=${token}`;
  
  const annRes = await getAnnotations(currentId);
  annotations.value = annRes.data.annotations;
  selectedAnnId.value = null;
};

const onImageLoad = () => {
  if (imgRef.value) {
    displayWidth.value = imgRef.value.clientWidth;
    displayHeight.value = imgRef.value.clientHeight;
  }
  loadingImg.value = false;
};

const onImageError = () => {
  loadingImg.value = false;
  imgError.value = true;
};

const preventDrag = (e) => e.preventDefault();

const getNormCoords = (e) => {
  const rect = svgRef.value.getBoundingClientRect();
  let x = (e.clientX - rect.left) / rect.width;
  let y = (e.clientY - rect.top) / rect.height;
  
  return {
    x: Math.max(0, Math.min(1, x)),
    y: Math.max(0, Math.min(1, y))
  };

};

// --- 工具切換 ---
const switchTool = (tool) => {
  cancelCurrentDrawing(); // 切換工具時取消正在畫的圖
  currentTool.value = tool;
};

const cancelCurrentDrawing = () => {
  isDrawing.value = false;
  tempBox.value = null;
  tempPoints.value = [];
  mousePos.value = null;
};

// --- SVG 滑鼠事件 ---
const onSvgMouseDown = (e) => {
  if (e.target.style.cursor === 'pointer') return;

  const pos = getNormCoords(e);

  if (currentTool.value === 'bbox') {
    isDrawing.value = true;
    startPoint.value = pos;
    tempBox.value = { x: pos.x, y: pos.y, w: 0, h: 0 };
  } 
  else if (currentTool.value === 'polygon') {
    if (tempPoints.value.length >= 3) {
      const firstPoint = tempPoints.value[0];
      const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);
      if (distance < 0.02) { // 歸一化距離小於 0.02 視為點擊到起點
        finishPolygon();
        return;
      }
    }
    tempPoints.value.push({ x: pos.x, y: pos.y });
  }
};

const onSvgMouseMove = (e) => {
  const pos = getNormCoords(e);
  mousePos.value = pos; 

  if (isDrawing.value && tempBox.value) {
    const x = Math.min(startPoint.value.x, pos.x);
    const y = Math.min(startPoint.value.y, pos.y);
    const w = Math.abs(pos.x - startPoint.value.x);
    const h = Math.abs(pos.y - startPoint.value.y);
    tempBox.value = { x, y, w, h };
  }
};

const onSvgMouseUp = () => {
  if (isDrawing.value && tempBox.value) {
    if (tempBox.value.w > 0.01 && tempBox.value.h > 0.01) {
      addAnnotation({
        type: 'bbox',
        x: tempBox.value.x, y: tempBox.value.y,
        w: tempBox.value.w, h: tempBox.value.h
      });
    }
    isDrawing.value = false;
    tempBox.value = null;
  }
};

const finishPolygon = () => {
  if (tempPoints.value.length >= 3) {
    addAnnotation({
      type: 'polygon',
      points: tempPoints.value.map(p => [p.x, p.y]) // 轉為後端需要的 [[x,y], [x,y]] 格式
    });
  }
  tempPoints.value = [];
  mousePos.value = null;
};

// --- 標記 CRUD ---
const addAnnotation = (data) => {
  const cat = categories.value.find(c => c.id === selectedCategoryId.value);
  annotations.value.push({
    id: uuidv4(),
    category_id: cat.id,
    category_name: cat.name,
    ...data
  });
};

const selectAnnotation = (ann) => {
  selectedAnnId.value = ann.id;
  selectedCategoryId.value = ann.category_id;
};

const deleteAnnotation = (id) => {
  annotations.value = annotations.value.filter(a => a.id !== id);
  if (selectedAnnId.value === id) selectedAnnId.value = null;
};

const clearAllAnnotations = () => {
  if (confirm('確定要清空這張圖片的所有標記嗎？')) {
    annotations.value = [];
    selectedAnnId.value = null;
  }
};

const onCategoryChange = () => {
  if (selectedAnnId.value) {
    const ann = annotations.value.find(a => a.id === selectedAnnId.value);
    const cat = categories.value.find(c => c.id === selectedCategoryId.value);
    if (ann && cat) {
      ann.category_id = cat.id;
      ann.category_name = cat.name;
    }
  }
};

// --- 導航與儲存 ---
const autoSave = async () => {
  const currentId = imageIds.value[currentIndex.value];
  const cleanAnnotations = annotations.value.map(({ id, ...rest }) => rest);
  await updateAnnotations(currentId, cleanAnnotations);
};

const nextImage = async () => {
  if (currentIndex.value < imageIds.value.length - 1) {
    await autoSave();
    currentIndex.value++;
    await loadImageAndAnnotations();
  }
};

const prevImage = async () => {
  if (currentIndex.value > 0) {
    await autoSave();
    currentIndex.value--;
    await loadImageAndAnnotations();
  }
};

const saveAndExit = async () => {
  await autoSave();
  router.push('/dashboard');
};
</script>

<style scoped>
.image-wrapper {
  max-width: 100%;
  max-height: 100%;
}
.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}
</style>