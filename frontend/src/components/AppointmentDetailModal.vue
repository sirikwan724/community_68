<script setup>
import { computed } from "vue";

// รับ props จาก parent
const props = defineProps({
  appointment: Object,   // ข้อมูลนัดหมาย
});

// ส่งอีเวนต์กลับหน้า Admin หรือ User
const emit = defineEmits(["close", "approve", "reject", "done"]);

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
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg">

      <h2 class="text-xl font-bold mb-4">รายละเอียดการนัดหมาย</h2>

      <p><strong>ผู้ขอนัด:</strong> {{ appointment.user_name }}</p>
      <p><strong>วันที่:</strong> {{ formatDateTH(appointment.date) }}</p>
      <p><strong>เวลา:</strong> {{ formatTime(appointment.start_time) }} - {{ formatTime(appointment.end_time) }}</p>
      <p class="mt-2"><strong>นัดหมายกับ:</strong> {{ appointment.meet_with_label || "-" }}</p>
      <p class="mt-2"><strong>เหตุผล:</strong> {{ appointment.reason || '-' }}</p>
      <p class="mt-2"><strong>สถานที่นัดหมาย:</strong> {{ appointment.meeting_place_label || "-" }}</p>
      <p class="mt-2"><strong>สถานะ:</strong>
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
      <div class="flex justify-between mt-6">

        <!-- ปุ่มอนุมัติ -->
        <button
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          @click="$emit('approve', appointment.id)"
        >
          ยืนยันนัดหมาย
        </button>

        <!-- ปุ่มปฏิเสธ -->
        <button
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          @click="$emit('reject', appointment.id)"
        >
          ปฏิเสธ
        </button>

        <!-- ปุ่มปิด -->
        <button
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          @click="$emit('close')"
        >
          ปิด
        </button>

      </div>
    </div>
  </div>
</template>
