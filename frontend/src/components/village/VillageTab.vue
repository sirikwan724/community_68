<script setup>
defineProps({
  isAdmin: Boolean,
});
</script>

<template>
  <section>
    <h2 class="text-xl font-semibold mb-2">ข้อมูลหมู่บ้าน</h2>
    <p class="text-gray-600">
      แสดงข้อมูลพื้นฐาน ประวัติ ความเป็นมา และรายละเอียดของหมู่บ้าน
    </p>

    <button
      v-if="isAdmin"
      class="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
    >
      แก้ไขข้อมูลหมู่บ้าน
    </button>
  </section>
</template>
