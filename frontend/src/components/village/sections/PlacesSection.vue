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

    <!-- รายละเอียดหัวข้อ -->
    <p v-if="section.description" class="mt-2 text-gray-700">
      {{ section.description }}
    </p>

    <!-- ไม่มีรายการ -->
    <div v-if="!section.items || !section.items.length" class="mt-4 text-gray-500">
      ยังไม่มีรายการสถานที่
    </div>

    <!-- มีรายการสถานที่ -->
    <div v-else class="mt-4 space-y-6">
      <div
        v-for="place in section.items"
        :key="place.id"
        class="p-4 rounded-lg border bg-gray-50"
      >
        <!-- ชื่อสถานที่ (ตัวหนาเล็กกว่าหัวข้อหลัก) -->
        <h3 class="text-lg font-bold text-gray-900">
          {{ place.name }}
        </h3>

        <!-- รายละเอียดสถานที่ -->
        <p v-if="place.detail" class="mt-2 text-gray-700">
          {{ place.detail }}
        </p>

        <!-- รูปของสถานที่ -->
        <div
          v-if="place.images && place.images.length"
          class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3"
        >
          <img
            v-for="(img, i) in place.images"
            :key="i"
            :src="img.url || img"
            class="w-full h-44 object-cover rounded-lg border"
            alt="place image"
          />
        </div>
      </div>
    </div>
  </div>
</template>