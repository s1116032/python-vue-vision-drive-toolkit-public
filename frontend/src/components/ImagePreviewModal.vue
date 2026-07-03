<template>
  <div v-if="show" class="modal-backdrop-custom" @click.self="close">
    <div class="modal-dialog-custom">
      <div class="modal-content-custom">
        <div class="modal-header-custom">
          <h5 class="modal-title text-truncate">{{ image?.filename }}</h5>
          <button type="button" class="btn-close-custom" @click="close">&times;</button>
        </div>
        <div class="modal-body-custom">
          <img :src="imageUrl" class="img-fluid rounded" alt="Preview">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: Boolean,
  image: Object
});

const emit = defineEmits(['close']);

// 核心：拼接帶有 Query String Token 的圖片 URL
const imageUrl = computed(() => {
  if (!props.image) return '';
  const token = localStorage.getItem('access_token');
  return `/api/images/${props.image.id}/file?token=${token}`;
});

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-dialog-custom {
  max-width: 80%;
  max-height: 90%;
}
.modal-content-custom {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
}
.modal-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}
.btn-close-custom {
  background: none;
  border: none;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
  color: #6c757d;
}
.btn-close-custom:hover {
  color: #000;
}
.modal-body-custom {
  padding: 1rem;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #e9ecef;
}
</style>