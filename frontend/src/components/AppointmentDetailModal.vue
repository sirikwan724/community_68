<script setup>
import { computed } from "vue";

// รับ props จาก parent
const props = defineProps({
  appointment: Object,   // ข้อมูลนัดหมาย
});

// ส่งอีเวนต์กลับหน้า Admin หรือ User
const emit = defineEmits(["close", "approve", "reject", "done"]);

// แสดงชื่อสถานะ
const statusLabel = computed(() => {
  switch (props.appointment.status) {
    case "pending":
      return "รอดำเนินการ";
    case "approved":
      return "อนุมัติแล้ว";
    case "rejected":
      return "ถูกยกเลิก";
    case "done":
      return "ดำเนินการเสร็จสิ้น";
    default:
      return props.appointment.status;
  }
});

// รูปแบบสีสถานะ
const statusClass = computed(() => {
  return {
    pending: "bg-yellow-100 text-yellow-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    done: "bg-blue-100 text-blue-700",
  }[props.appointment.status];
});
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center">
    <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg">

      <h2 class="text-xl font-bold mb-4">รายละเอียดการนัดหมาย</h2>

      <p><strong>ผู้ขอนัด:</strong> {{ appointment.user_name }}</p>
      <p><strong>วันที่:</strong> {{ appointment.date }}</p>
      <p><strong>เวลา:</strong> {{ appointment.start_time }} - {{ appointment.end_time }}</p>
      <p class="mt-2"><strong>เหตุผล:</strong> {{ appointment.reason }}</p>
      <p class="mt-2"><strong>สถานที่:</strong> {{ appointment.meeting_place }}</p>
      <p class="mt-2"><strong>สถานะ:</strong> {{ appointment.status }}</p>

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
