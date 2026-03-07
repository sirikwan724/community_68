<script setup>
import RichSection from "./sections/RichSection.vue";
import PlacesSection from "./sections/PlacesSection.vue";

defineProps({
  isAdmin: { type: Boolean, default: false },
  sections: { type: Array, default: () => [] },
});

defineEmits(["create-section", "edit-section"]);
</script>

<template>
  <section class="space-y-8">
    <div v-if="isAdmin" class="flex justify-end">
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        @click="$emit('create-section')"
      >
        + เพิ่มหัวข้อ
      </button>
    </div>

    <div v-if="!sections.length" class="text-gray-500">
      ยังไม่มีข้อมูลหัวข้อหมู่บ้าน
    </div>

    <div v-for="sec in sections" :key="sec.id" class="border-b pb-8">
      <RichSection v-if="sec.type === 'RICH'" :section="sec" />
      <PlacesSection v-else-if="sec.type === 'PLACES'" :section="sec" />

      <div v-else class="text-red-500">
        ไม่รองรับประเภทหัวข้อ: {{ sec.type }}
      </div>

      <div v-if="isAdmin" class="mt-4">
        <button
          class="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200"
          @click="$emit('edit-section', sec)"
        >
          แก้ไขหัวข้อนี้
        </button>
      </div>
    </div>
  </section>
</template>