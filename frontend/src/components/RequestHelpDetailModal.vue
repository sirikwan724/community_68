<template>
  <div 
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 relative">

      <!-- close -->
      <button
        @click="emit('close')"
        class="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
      >
        ✖
      </button>

      <h2 class="text-2xl font-bold text-center mb-4">
        รายละเอียดคำขอความอนุเคราะห์
      </h2>

      <div class="space-y-3">
        <p><strong>ประเภท:</strong> {{ data.request_type }}</p>
        <p><strong>วันเวลาเริ่ม:</strong> {{ formatDate(data.start_datetime) }}</p>
        <p><strong>วันเวลาสิ้นสุด:</strong> {{ formatDate(data.end_datetime) }}</p>
        <p><strong>สถานที่:</strong> {{ data.area }}</p>
        <p><strong>รายละเอียด:</strong> {{ data.detail }}</p>

        <div v-if="data.file">
          <p class="font-semibold mt-2">รูปภาพประกอบ:</p>
          <img :src="fileUrl + data.file" class="rounded border max-h-60 mt-2" />
        </div>
      </div>

      <!-- action -->
      <div class="flex justify-between mt-6">
        <button
          @click="emit('approve', data.id)"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          ✔ อนุมัติ
        </button>

        <button
          @click="rejectMode = true"
          class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
        >
          ❌ ปฏิเสธ
        </button>
      </div>

      <!-- reason reject -->
      <div v-if="rejectMode" class="mt-4">
        <textarea
          v-model="rejectReason"
          rows="3"
          placeholder="ระบุเหตุผลการปฏิเสธ..."
          class="w-full border p-2 rounded"
        ></textarea>

        <button
          @click="emit('reject', { id: data.id, reason: rejectReason })"
          class="w-full bg-red-600 text-white p-2 rounded mt-3 hover:bg-red-700"
        >
          ส่งเหตุผลปฏิเสธ
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  show: Boolean,
  data: Object,
  fileUrl: { type: String, default: "http://localhost:8000" }
});

const emit = defineEmits(["close", "approve", "reject"]);

const rejectMode = ref(false);
const rejectReason = ref("");

const formatDate = (d) => {
  return new Date(d).toLocaleString("th-TH", {
    dateStyle: "long",
    timeStyle: "short",
  });
};
</script>
