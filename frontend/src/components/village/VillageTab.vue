<script setup>
import RichSection from "./sections/RichSection.vue";
import PlacesSection from "./sections/PlacesSection.vue";

defineProps({
  isAdmin: { type: Boolean, default: false },
  sections: { type: Array, default: () => [] },
});

defineEmits(["create-section", "edit-section", "delete-section", "refresh"]);
</script>

<template>
  <section class="space-y-8">

    <div v-if="!sections.length" class="text-gray-500">
      ยังไม่มีข้อมูลหัวข้อหมู่บ้าน
    </div>

    <div v-for="sec in sections" :key="sec.id" class="border-b pb-8">

      <!-- ปุ่ม admin อยู่มุมขวาบนของแต่ละหัวข้อ -->
      <div v-if="isAdmin" class="flex justify-end gap-2 mb-3">
        <button
          class="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
          @click="$emit('edit-section', sec)"
        >แก้ไขหัวข้อ</button>
        <button
          class="px-3 py-1 text-sm bg-red-50 text-red-600 rounded hover:bg-red-100"
          @click="$emit('delete-section', sec)"
        >ลบหัวข้อ</button>
      </div>

      <RichSection
        v-if="sec.type === 'RICH'"
        :section="sec"
        :isAdmin="isAdmin"
        @refresh="$emit('refresh')"
      />
      <PlacesSection v-else-if="sec.type === 'PLACES'" :section="sec" />

      <div v-else class="text-red-500">
        ไม่รองรับประเภทหัวข้อ: {{ sec.type }}
      </div>

    </div>
  </section>
</template>