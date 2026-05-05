<script setup>
import { ref, computed } from "vue";
import api from "@/services/api";

const props = defineProps({
  section: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false },
});

const emit = defineEmits(["refresh"]);

const paragraphs = computed(() => {
  const c = props.section?.content;
  if (Array.isArray(c)) return c;
  if (typeof c === "string") return c.split("\n").map((s) => s.trim()).filter(Boolean);
  return [];
});

const images = computed(() => props.section?.images ?? []);
const useSlider = computed(() => images.value.length >= 3);
const current = ref(0);

const prev = () => { current.value = (current.value - 1 + images.value.length) % images.value.length; };
const next = () => { current.value = (current.value + 1) % images.value.length; };

const deleteImage = async (img) => {
  if (!confirm("ต้องการลบรูปนี้ใช่ไหม?")) return;
  try {
    await api.delete(`/admin/village/section-images/${img.id}/`);
    emit("refresh");
  } catch {
    alert("ลบรูปไม่สำเร็จ");
  }
};
</script>

<template>
  <div>
    <h2 class="text-2xl font-extrabold text-gray-900">{{ section.title }}</h2>

    <div class="mt-3 space-y-2 text-gray-700 leading-relaxed">
      <p v-for="(line, i) in paragraphs" :key="i">{{ line }}</p>
    </div>

    <!-- Grid (1-2 รูป) -->
    <div v-if="images.length && !useSlider" class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-for="img in images" :key="img.id" class="flex flex-col gap-1">
        <img :src="img.url || img" class="w-full h-56 object-cover rounded-lg border" alt="" />
        <p v-if="img.caption" class="text-sm text-gray-500 text-center">{{ img.caption }}</p>
        <button
          v-if="isAdmin"
          class="text-xs text-red-500 hover:text-red-700 text-center"
          @click="deleteImage(img)"
        >ลบรูปนี้</button>
      </div>
    </div>

    <!-- Slider (3+ รูป) -->
    <div v-else-if="images.length" class="mt-4">
      <div class="relative rounded-xl overflow-hidden border bg-gray-100" style="height: 320px;">
        <img :src="images[current].url || images[current]" class="w-full h-full object-cover" alt="" />
        <button
          class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 text-white rounded-full w-9 h-9 flex items-center justify-center text-xl"
          @click="prev"
        >‹</button>
        <button
          class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 text-white rounded-full w-9 h-9 flex items-center justify-center text-xl"
          @click="next"
        >›</button>
      </div>
      <p v-if="images[current].caption" class="text-sm text-gray-500 text-center mt-2">
        {{ images[current].caption }}
      </p>
      <div class="flex justify-center gap-2 mt-2">
        <button
          v-for="(_, i) in images"
          :key="i"
          class="w-2 h-2 rounded-full transition-colors"
          :class="i === current ? 'bg-blue-600' : 'bg-gray-300'"
          @click="current = i"
        />
      </div>
      <div v-if="isAdmin" class="flex justify-center mt-2">
        <button class="text-xs text-red-500 hover:text-red-700" @click="deleteImage(images[current])">
          ลบรูปนี้
        </button>
      </div>
    </div>
  </div>
</template>