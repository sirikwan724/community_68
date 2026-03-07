<script setup>
defineProps({
  section: { type: Object, required: true },
});
</script>

<template>
  <div>
    <!-- หัวข้อใหญ่ตัวหนา -->
    <h2 class="text-2xl font-extrabold text-gray-900">
      {{ section.title }}
    </h2>

    <!-- รายละเอียดเรียงลงมา -->
    <div class="mt-3 space-y-2 text-gray-700 leading-relaxed">
      <p v-for="(line, i) in section.content || []" :key="i">
        {{ line }}
      </p>
    </div>

    <!-- รูป (มีหรือไม่มีก็ได้) -->
    <div
      v-if="section.images && section.images.length"
      class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4"
    >
      <img
        v-for="(img, i) in section.images"
        :key="i"
        :src="img.url || img"
        class="w-full h-56 object-cover rounded-lg border"
        alt="section image"
      />
    </div>
  </div>
</template>