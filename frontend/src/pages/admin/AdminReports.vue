<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";
// import axios from "axios";
// import api from "@/api";
import ReportDetailModal from "@/components/ReportDetailModal.vue";

// const reports = ref([]);
const loading = ref(true);
const activeTab = ref("pending"); // pending | processing | resolved

const getToken = () => localStorage.getItem("access");

const reportsRaw = ref([]);

const thaiMonths = [
  { value: "01", label: "มกราคม" },
  { value: "02", label: "กุมภาพันธ์" },
  { value: "03", label: "มีนาคม" },
  { value: "04", label: "เมษายน" },
  { value: "05", label: "พฤษภาคม" },
  { value: "06", label: "มิถุนายน" },
  { value: "07", label: "กรกฎาคม" },
  { value: "08", label: "สิงหาคม" },
  { value: "09", label: "กันยายน" },
  { value: "10", label: "ตุลาคม" },
  { value: "11", label: "พฤศจิกายน" },
  { value: "12", label: "ธันวาคม" },
];

const statusLabel = {
  pending: "รอรับเรื่อง",
  processing: "กำลังดำเนินการ",
  resolved: "แก้ไขเสร็จสิ้น",
  canceled: "ผู้แจ้งยกเลิก",
};

const statusClass = {
  pending: "bg-yellow-200 text-yellow-800",
  processing: "bg-blue-200 text-blue-800",
  resolved: "bg-green-200 text-green-800",
  canceled: "bg-gray-300 text-gray-700",
};

// filter
const filterMonth = ref(""); // 01 - 12
const filterYear = ref("");  // 2024, 2025
const filterStatus = ref(""); // pending | processing | resolved

// map สถานะจาก backend → frontend
const statusMap = {
  pending: ["pending", "open"],
  processing: ["processing", "in_progress"],
  resolved: ["resolved", "done", "approved"],
  canceled: ["canceled"],
};

// โหลดรายการตามแท็บ
const loadReports = async () => {
  loading.value = true;
  try {
    const res = await api.get("/reports/admin-all/");
    reportsRaw.value = res.data;
  } finally {
    loading.value = false;
  }
};

onMounted(loadReports);

// เปลี่ยนแท็บ
const changeTab = (tab) => {
  activeTab.value = tab;
  filterStatus.value = tab; 
};

// เปิด Pop-up (เราจะทำในขั้นตอนที่ 2)
const selectedReport = ref(null);
const openDetail = (data) => {
  selectedReport.value = data;
};

// รับเรื่อง
const acceptReport = async (id) => {
  if (!confirm("รับเรื่องนี้หรือไม่?")) return;

  try {
    await api.patch(`/reports/${id}/accept/`);
    loadReports();
  } catch (err) {
    console.error("Accept error:", err);
    alert("รับเรื่องไม่สำเร็จ");
  }
};

const reports = computed(() => {
  return reportsRaw.value.filter((r) => {
    const date = new Date(r.created_at);
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = String(date.getFullYear());

    const matchMonth =
      !filterMonth.value || filterMonth.value === month;

    const matchYear =
      !filterYear.value || filterYear.value === year;

    const matchStatus =
      !filterStatus.value || statusMap[filterStatus.value]?.includes(r.status);

    return matchMonth && matchYear && matchStatus;
  });
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString("th-TH", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

</script>

<template>
  <div class="p-6">

    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
      <h1 class="text-2xl font-bold text-gray-800">จัดการรายงานปัญหา</h1>

      <div class="flex items-center gap-3">
        <select v-model="filterMonth" class="border rounded px-3 py-2">
          <option value="">ทุกเดือน</option>
          <option v-for="m in thaiMonths" 
          :key="m.value" 
          :value="m.value"
          >
            {{ m.label }}
          </option>
        </select>
        <select v-model="filterYear" class="border rounded px-3 py-2">
          <option value="">ทุกปี</option>
          <option v-for="y in [2024, 2025, 2026]" :key="y" :value="String(y)">
            {{ y }}
          </option>
        </select>
        <select v-model="filterStatus" class="border rounded px-3 py-2">
          <option value="">ทุกสถานะ</option>
          <option value="pending">รอรับเรื่อง</option>
          <option value="processing">กำลังดำเนินการ</option>
          <option value="resolved">แก้ไขเสร็จสิ้น</option>
        </select>
        <router-link 
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
        >
        กลับหน้าหลัก
        </router-link>
      </div>
    </div>

    <div v-if="loading">กำลังโหลด...</div>

    <table v-else class="w-full bg-white shadow rounded">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-3 text-left">เรื่องรายงาน</th>
          <th class="p-3 text-left">พื้นที่</th>
          <th class="p-3 text-left">ผู้แจ้ง</th>
          <th class="p-3 text-left">วันที่แจ้ง</th>
          <th class="p-3 text-center">สถานะ</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="r in reports"
          :key="r.id"
          class="border-b hover:bg-gray-50"
        >
          <td class="p-3">{{ r.category }}</td>
          <td class="p-3">{{ r.area }}</td>
          <td class="p-3">{{ r.user_data.full_name }}</td>
          <td class="p-3">{{ formatDate(r.created_at) }}</td>

          <td class="p-3 text-center flex justify-center gap-2">

            <span
              class="px-3 py-1 rounded-full text-xs font-bold inline-block mb-2"
              :class="statusClass[r.status]"
            >
              {{ statusLabel[r.status] }}
            </span> 
            <!-- ดูรายละเอียด -->
            <button
              class="text-blue-600 underline"
              @click="openDetail(r)"
            >
              ดูรายละเอียด
            </button>

            <!-- รับเรื่อง -->
            <button
              v-if="statusMap.pending.includes(r.status)"
              class="bg-green-600 text-white px-3 py-1 rounded"
              @click="acceptReport(r.id)"
            >
              รับเรื่อง
            </button>

          </td>
        </tr>
      </tbody>
    </table>
    <ReportDetailModal
    v-if="selectedReport"
    :report="selectedReport"
    @close="selectedReport = null"
    @updated="loadReports"
    />
  </div>
</template>
