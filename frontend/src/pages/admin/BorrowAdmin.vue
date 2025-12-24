<script setup>
import { ref, onMounted } from "vue";
import { BorrowService } from "@/services/borrow.service";

const borrows = ref([]);
const loading = ref(true);

const loadBorrows = async () => {
  loading.value = true;
  const res = await BorrowService.adminList();
  borrows.value = res.data;
  loading.value = false;
};

const approve = async (id) => {
  if (!confirm("อนุมัติคำขอนี้?")) return;
  await BorrowService.approve(id);
  loadBorrows();
};

const reject = async (id) => {
  if (!confirm("ปฏิเสธคำขอนี้?")) return;
  await BorrowService.reject(id);
  loadBorrows();
};

const confirmReturn = async (id) => {
  if (!confirm("ยืนยันการคืนของ?")) return;
  await BorrowService.confirmReturn(id);
  loadBorrows();
};

onMounted(loadBorrows);
</script>

<template>
  <div class="max-w-6xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">จัดการคำขอยืม / จอง</h1>

      <router-link
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <div v-if="loading">กำลังโหลด...</div>

    <div
      v-for="b in borrows"
      :key="b.id"
      class="border rounded p-4 mb-4 bg-white"
    >
      <div class="flex justify-between">
        <div>
          <h3 class="font-bold">
            <span v-if="b.borrow_type === 'ITEM'">ยืมสิ่งของ</span>
            <span v-else>จองสถานที่</span>
          </h3>
          <p class="text-sm text-gray-500">
            ผู้ขอ: {{ b.user_name }}
          </p>
        </div>

        <span
          class="px-2 py-1 rounded text-white text-sm"
          :class="{
            'bg-yellow-500': b.status === 'pending',
            'bg-blue-500': b.status === 'approved',
            'bg-orange-500': b.status === 'return_requested',
            'bg-green-600': b.status === 'returned',
            'bg-red-600': b.status === 'rejected',
          }"
        >
          {{ b.status }}
        </span>
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
        ระยะเวลา: {{ b.start_datetime }} – {{ b.end_datetime }}
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
          @click="reject(b.id)"
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
</template>
