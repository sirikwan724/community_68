<template>
  <div
    v-if="show && data"
    class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 relative max-h-[90vh] overflow-y-auto">

      <!-- ปุ่มปิด -->
      <button
        @click="handleClose"
        class="absolute right-3 top-3 text-gray-500 hover:text-gray-700 text-xl"
      >
        ✕
      </button>

      <h2 class="text-xl font-bold mb-4">รายละเอียดคำขอความอนุเคราะห์</h2>

      <!-- รายละเอียดคำขอ -->
      <div class="space-y-2">
        <p class="mb-4">
          <strong>ผู้ส่งคำขอ:</strong>
          <button
            @click="showUserInfo = !showUserInfo"
            class="ml-1 text-blue-600 hover:underline font-medium"
          >
            {{ data.user_data?.full_name ?? '-' }}
          </button>
        </p>
        <div v-if="showUserInfo" class="bg-blue-50 border border-blue-200 rounded p-3 mb-4 space-y-1 text-sm">
          <p class="text-blue-700 font-semibold mb-1">ข้อมูลผู้ส่งคำขอ</p>
          <p><strong>ชื่อ-นามสกุล:</strong> {{ data.user_data?.full_name ?? '-' }}</p>
          <p><strong>เบอร์โทร:</strong> {{ data.user_data?.phone ?? '-' }}</p>
          <p><strong>ที่อยู่:</strong> {{ data.user_data?.address ?? '-' }}</p>
        </div>
        <p><strong>ประเภท:</strong> {{ data.request_type }}</p>
        <p><strong>วันเวลาเริ่ม:</strong> {{ formatDate(data.start_datetime) }}</p>
        <p><strong>วันเวลาสิ้นสุด:</strong> {{ formatDate(data.end_datetime) }}</p>
        <p><strong>สถานที่:</strong> {{ data.area }}</p>
        <p><strong>รายละเอียด:</strong> {{ data.detail }}</p>
        <p><strong>วันที่ส่งคำขอ:</strong> {{ formatDate(data.created_at) }}</p>

        <!-- สถานะ badge -->
        <p>
          <strong>สถานะ:</strong>
          <span
            class="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold"
            :class="{
              'bg-yellow-100 text-yellow-700': data.status === 'pending',
              'bg-green-100 text-green-700': data.status === 'approved',
              'bg-red-100 text-red-700': data.status === 'rejected',
              'bg-blue-100 text-blue-700': data.status === 'done',
              'bg-gray-100 text-gray-500': data.status === 'canceled',
            }"
          >
            {{
              data.status === 'pending' ? 'รอดำเนินการ'
              : data.status === 'approved' ? 'อนุมัติแล้ว'
              : data.status === 'rejected' ? 'ปฏิเสธ'
              : data.status === 'done' ? 'ดำเนินการเสร็จสิ้น'
              : 'ยกเลิกโดยผู้ใช้'
            }}
          </span>
        </p>
      </div>

      <!-- ไฟล์แนบ -->
      <div v-if="data.file" class="mt-4">
        <p class="font-semibold mb-2">ไฟล์/รูปภาพประกอบ:</p>
        <img :src="fileUrl + data.file" class="rounded border max-h-60 w-full object-cover" />
      </div>

      <!-- เหตุผลปฏิเสธ -->
      <div v-if="data.status === 'rejected' && data.reject_reason" class="mt-4 p-3 bg-red-50 border border-red-200 rounded">
        <p class="text-red-700 font-semibold">เหตุผลการปฏิเสธ:</p>
        <p class="text-red-600 mt-1">{{ data.reject_reason }}</p>
      </div>

      <!-- ปุ่ม action เฉพาะ pending -->
      <div v-if="data.status === 'pending'" class="flex justify-between mt-6">
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

      <!-- กล่องเหตุผลปฏิเสธ -->
      <div v-if="data.status === 'pending' && rejectMode" class="mt-4">
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
import { ref, watch } from "vue";

const props = defineProps({
  show: Boolean,
  data: Object,
  fileUrl: { type: String, default: "http://localhost:8000" }
});

const emit = defineEmits(["close", "approve", "reject"]);

const rejectMode = ref(false);
const rejectReason = ref("");
const showUserInfo = ref(false);

watch(() => props.show, (val) => {
  if (!val) {
    rejectMode.value = false;
    rejectReason.value = "";
    showUserInfo.value = false;
  }
});

const handleClose = () => {
  rejectMode.value = false;
  rejectReason.value = "";
  emit("close");
};

const formatDate = (d) => {
  if (!d) return "-";
  return new Date(d).toLocaleString("th-TH", {
    dateStyle: "long",
    timeStyle: "short",
  });
};
</script>