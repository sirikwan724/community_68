<script setup>
import { ref, onMounted, computed } from "vue";
import { BorrowService } from "@/services/borrow.service";

const borrows = ref([]);
const loading = ref(true);

const showRejectModal = ref(false);
const rejectingId = ref(null);
const rejectNote = ref("");

const expandedProfileId = ref(null);

const toggleProfile = (id) => {
  expandedProfileId.value = expandedProfileId.value === id ? null : id;
};

const filterMonth = ref("all");   // 1–12 หรือ all
const filterYear = ref("all");    // 2568 / 2569 หรือ all
const filterStatus = ref("all");  // pending / approved / ...

const loadBorrows = async () => {
  loading.value = true;
  const res = await BorrowService.adminList();
  borrows.value = res.data;
  loading.value = false;
};

const thaiMonths = [
  "", // index 0 ไม่ใช้
  "มกราคม",
  "กุมภาพันธ์",
  "มีนาคม",
  "เมษายน",
  "พฤษภาคม",
  "มิถุนายน",
  "กรกฎาคม",
  "สิงหาคม",
  "กันยายน",
  "ตุลาคม",
  "พฤศจิกายน",
  "ธันวาคม",
];

const statusLabel = {
  pending: "รอดำเนินการ",
  approved: "อนุมัติแล้ว",
  rejected: "ปฏิเสธ",
  return_requested: "รอรับคืน",
  returned: "คืนแล้ว",
};

const statusClass = {
  pending: "bg-yellow-200 text-yellow-800",
  approved: "bg-green-200 text-green-800",
  rejected: "bg-red-200 text-red-800",
  return_requested: "bg-orange-200 text-orange-800",
  returned: "bg-green-300 text-green-900",
};

const filteredBorrows = computed(() => {
  return borrows.value.filter((b) => {
    const d = new Date(b.created_at);
    const month = d.getMonth() + 1;
    const year = d.getFullYear() + 543; // พ.ศ.

    if (filterMonth.value !== "all" && month !== Number(filterMonth.value)) {
      return false;
    }

    if (filterYear.value !== "all" && year !== Number(filterYear.value)) {
      return false;
    }

    if (filterStatus.value !== "all" && b.status !== filterStatus.value) {
      return false;
    }

    return true;
  });
});

const formatDT = (dt) => {
  if (!dt) return "-";
  const d = new Date(dt);
  if (isNaN(d.getTime())) return "-";

  return d.toLocaleString("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

const approve = async (id) => {
  if (!confirm("อนุมัติคำขอนี้?")) return;
  await BorrowService.approve(id);
  loadBorrows();
};

const getOverdueDays = (expectedReturn) => {
  if (!expectedReturn) return 0;
  const now = new Date();
  const expected = new Date(expectedReturn);
  if (now <= expected) return 0;
  return Math.floor((now - expected) / (1000 * 60 * 60 * 24));
};

const openRejectModal = (id) => {
  rejectingId.value = id;
  rejectNote.value = "";
  showRejectModal.value = true;
};

const confirmReject = async () => {
  if (!rejectNote.value.trim()) {
    alert("กรุณากรอกเหตุผลการปฏิเสธ");
    return;
  }
  try {
    await BorrowService.reject(rejectingId.value, rejectNote.value);
    showRejectModal.value = false;
    loadBorrows();
  } catch (err) {
    alert("เกิดข้อผิดพลาด");
  }
};

const confirmReturn = async (id) => {
  if (!confirm("ยืนยันการคืนของ?")) return;
  await BorrowService.confirmReturn(id);
  loadBorrows();
};

onMounted(loadBorrows);
</script>

<template>
  <div class="p-6">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
      <h1 class="text-2xl font-bold text-gray-800">จัดการคำขอยืม / จอง</h1>

      <div class="flex flex-wrap items-center gap-3">

        <!-- ปี -->
        <select v-model="filterYear" class="border px-3 py-2 rounded">
          <option value="all">ทุกปี</option>
          <option :value="2568">2568</option>
          <option :value="2569">2569</option>
        </select>
      
        <!-- เดือน -->
        <select v-model="filterMonth" class="border px-3 py-2 rounded">
          <option value="all">ทุกเดือน</option>
          <option v-for="m in 12" :key="m" :value="m">
            {{ thaiMonths[m] }}
          </option>
        </select>
      
        <!-- สถานะ -->
        <select v-model="filterStatus" class="border px-3 py-2 rounded">
          <option value="all">ทุกสถานะ</option>
          <option value="pending">รอดำเนินการ</option>
          <option value="approved">อนุมัติแล้ว</option>
          <option value="return_requested">รอรับคืน</option>
          <option value="returned">คืนแล้ว</option>
          <option value="rejected">ปฏิเสธ</option>
        </select>
      </div>

      <router-link
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <div v-if="loading">กำลังโหลด...</div>

    <div
      v-for="b in filteredBorrows"
      :key="b.id"
      class="border rounded p-4 mb-4 bg-white"
    >
      <div class="flex items-center gap-3">
        <div>
          <h3 class="font-bold">
            <span v-if="b.borrow_type === 'ITEM'">ยืมสิ่งของ</span>
            <span v-else>จองสถานที่</span>
          </h3>
          <span
            class="px-3 py-1 rounded-md text-xs font-bold"
            :class="statusClass[b.status]"
          >
            {{ statusLabel[b.status] }}
          </span>
          <p class="text-sm text-gray-600">
            ชื่อผู้ขอ:
            <button
              @click="toggleProfile(b.id)"
              class="text-blue-600 hover:underline font-medium"
            >
              {{ b.borrower_name }}
            </button>
          </p>
          <div
            v-if="expandedProfileId === b.id && b.borrower_profile"
            class="mt-2 p-3 bg-blue-50 border border-blue-100 rounded text-sm space-y-1"
          >
            <p><span class="text-gray-500">ชื่อ-นามสกุล:</span> {{ b.borrower_profile.full_name || '-' }}</p>
            <p><span class="text-gray-500">เบอร์โทร:</span> {{ b.borrower_profile.phone || '-' }}</p>
            <p><span class="text-gray-500">รหัสทะเบียนบ้าน:</span> {{ b.borrower_profile.citizen_id || '-' }}</p>
            <p><span class="text-gray-500">ที่อยู่:</span> {{ b.borrower_profile.address || '-' }}</p>
            <p><span class="text-gray-500">ชื่อเจ้าบ้าน:</span> {{ b.borrower_profile.house_owner_name || '-' }}</p>          </div>
          <p v-if="b.purpose" class="text-sm text-gray-600 mt-1">วัตถุประสงค์: {{ b.purpose }}</p>
        </div>
      </div>

      <!-- รายละเอียด -->
      <div class="mt-3 text-gray-700">
        <div v-if="b.borrow_type === 'ITEM'">
          <div v-for="(i, idx) in b.items" :key="idx">
            • {{ i.item_name }} × {{ i.quantity }} {{ i.unit }}
          </div>
        </div>

        <div v-else>
          สถานที่: {{ b.location_name }}
        </div>
      </div>

      <p class="text-sm text-gray-500 mt-2">
        ระยะเวลา: {{ formatDT(b.start_datetime) }} – {{ formatDT(b.end_datetime) }}
      </p>

      <p class="text-sm text-gray-500">รับของ/สถานที่: {{ formatDT(b.pickup_datetime) }}</p>
      <p class="text-sm text-gray-500">วันส่งคืน: {{ formatDT(b.expected_return_datetime) }}
        <span
          v-if="['approved', 'return_requested'].includes(b.status) && getOverdueDays(b.expected_return_datetime) > 0"
          class="ml-2 font-bold text-red-600"
        >
          เกินกำหนด {{ getOverdueDays(b.expected_return_datetime) }} วัน
        </span>
      </p>

      <p v-if="b.status === 'rejected' && b.admin_note" class="text-sm text-red-600 mt-2">
        เหตุผล: {{ b.admin_note }}
      </p>

      <!-- ปุ่ม -->
      <div class="mt-4 flex gap-3">
        <button
          v-if="b.status === 'pending'"
          @click="approve(b.id)"
          class="px-3 py-1 bg-green-600 text-white rounded"
        >
          อนุมัติ
        </button>

        <button
          v-if="b.status === 'pending'"
          @click="openRejectModal(b.id)"
          class="px-3 py-1 bg-red-600 text-white rounded"
        >
          ปฏิเสธ
        </button>

        <button
          v-if="b.status === 'return_requested'"
          @click="confirmReturn(b.id)"
          class="px-3 py-1 bg-orange-500 text-white rounded"
        >
          ยืนยันคืน
        </button>
      </div>
    </div>
  </div>
  <div
    v-if="showRejectModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
      <h2 class="text-lg font-bold mb-4">เหตุผลการปฏิเสธ</h2>
      <textarea
        v-model="rejectNote"
        rows="4"
        class="w-full border rounded p-2 mb-4"
        placeholder="กรุณาระบุเหตุผล..."
      ></textarea>
      <div class="flex gap-3 justify-end">
        <button
          @click="showRejectModal = false"
          class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          ยกเลิก
        </button>
        <button
          @click="confirmReject"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          ยืนยันปฏิเสธ
        </button>
      </div>
    </div>
  </div>
</template>