<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const slides = [
  { id: 1, image: "/src/assets/slider/Q1.jpg" },
  { id: 2, image: "/src/assets/slider/A17.jpg" },
  { id: 3, image: "/src/assets/slider/A7.jpg" },
  { id: 4, image: "/src/assets/slider/B2.jpg" },
];

const current = ref(0);

let interval = null;

onMounted(() => {
  interval = setInterval(() => {
    current.value = (current.value + 1) % slides.length;
  }, 4000);
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>

<template>
  <div class="w-full bg-brand-softYellow py-6">
    <div class="max-w-5xl mx-auto relative overflow-hidden rounded-xl shadow">
      <!-- Slide -->
      <img
        :src="slides[current].image"
        class="w-full h-72 object-cover transition-all"
      />

      <!-- Dots -->
      <div class="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2">
        <span
          v-for="(s, index) in slides"
          :key="index"
          class="w-3 h-3 rounded-full cursor-pointer"
          :class="index === current ? 'bg-white' : 'bg-white/50'"
          @click="current = index"
        ></span>
      </div>
    </div>
  </div>
</template>
