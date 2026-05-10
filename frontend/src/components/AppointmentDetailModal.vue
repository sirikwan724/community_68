<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  appointment: Object,
  autoReject: Boolean,
});

const emit = defineEmits(["close", "approve", "reject", "done"]);

const showUserDetail = ref(false);
const showRejectForm = ref(false);
const rejectNote = ref("");

// ต้องวาง watch หลัง ref ทุกตัว เพื่อให้ showRejectForm พร้อมใช้แล้ว
watch(
  () => props.autoReject,
  (val) => {
    if (val) showRejectForm.value = true;
  },
  { immediate: true }
);

const formatDateTH = (dateStr) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("th-TH", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
};

const formatTime = (timeStr) => {
  if (!timeStr) return "-";
  return timeStr.slice(0, 5);
};
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg relative">

      <button
        @click="$emit('close')"
        class="absolute top-3 right-4 text-gray-400 hover:text-gray-700 text-2xl font-bold leading-none"
      >
        &times;
      </button>

      <h2 class="text-xl font-bold mb-4">รายละเอียดการนัดหมาย</h2>

      <p>
        <strong>ผู้ขอนัด:</strong>
        <button
          @click="showUserDetail = !showUserDetail"
          class="text-blue-600 hover:underline ml-1"
        >
          {{ appointment.user_name }}
        </button>
      </p>
      <!-- ข้อมูลผู้ขอนัด (แสดงเมื่อกด) -->
      <div v-if="showUserDetail" class="ml-4 mt-1 mb-2 p-3 bg-gray-50 rounded border text-sm text-gray-700 space-y-1">
        <p><strong>เบอร์โทร:</strong> {{ appointment.user_data?.phone || "-" }}</p>
        <p><strong>ที่อยู่:</strong> {{ appointment.user_data?.address || "-" }}</p>
      </div>
      <p><strong>วันที่:</strong> {{ formatDateTH(appointment.date) }}</p>
      <p><strong>เวลา:</strong> {{ formatTime(appointment.start_time) }} - {{ formatTime(appointment.end_time) }}</p>
      <p class="mt-2"><strong>นัดหมายกับ:</strong> {{ appointment.meet_with_label || "-" }}</p>
      <p class="mt-2"><strong>เหตุผล:</strong> {{ appointment.reason || '-' }}</p>
      <p class="mt-2"><strong>สถานที่นัดหมาย:</strong> {{ appointment.meeting_place_label || "-" }}</p>
      <p class="mt-2"><strong>สถานะ:</strong>
        <!-- แสดงโน้ตจากแอดมิน (ถ้ามี) -->
        <p v-if="appointment.admin_note" class="mt-2">
          <strong>หมายเหตุจากแอดมิน:</strong>
          <span class="text-red-600">{{ appointment.admin_note }}</span>
        </p>
        <span
          class="px-3 py-1 rounded-full text-xs font-semibold"
          :class="{
            'bg-yellow-100 text-yellow-700': appointment.status === 'pending',
            'bg-green-100 text-green-700': appointment.status === 'approved',
            'bg-red-100 text-red-700': appointment.status === 'rejected',
            'bg-blue-100 text-blue-700': appointment.status === 'done',
          }"
        >
          {{ appointment.status_label }}
        </span>
      </p>

      <!-- ปุ่มเฉพาะแอดมิน -->
      <div v-if="appointment.status === 'pending' && !showRejectForm" class="flex gap-3 mt-6">
        <button
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          @click="$emit('approve', appointment.id)"
        >
          ยืนยันนัดหมาย
        </button>

        <button
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          @click="showRejectForm = true"
        >
          ปฏิเสธ
        </button>
      </div>

      <!-- ฟอร์มโน้ตเหตุผลการปฏิเสธ (แยกออกมาอยู่นอก flex) -->
      <div v-if="showRejectForm && appointment.status === 'pending'" class="mt-4">
        <label class="block text-sm font-semibold text-gray-700 mb-1">
          ระบุเหตุผลการปฏิเสธ <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="rejectNote"
          rows="3"
          placeholder="กรุณาระบุเหตุผล..."
          class="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
        ></textarea>
        <div class="flex gap-3 mt-2">
          <button
            @click="() => {
              if (!rejectNote.trim()) { alert('กรุณาระบุเหตุผล'); return; }
              $emit('reject', { id: appointment.id, note: rejectNote });
              showRejectForm = false;
              rejectNote = '';
            }"
            class="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            ยืนยันการปฏิเสธ
          </button>
          <button
            @click="showRejectForm = false; rejectNote = ''"
            class="px-4 py-2 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400"
          >
            ยกเลิก
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
