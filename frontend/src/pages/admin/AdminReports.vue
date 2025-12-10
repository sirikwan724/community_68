<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import ReportDetailModal from "@/components/ReportDetailModal.vue";

const reports = ref([]);
const loading = ref(true);
const activeTab = ref("pending"); // pending | processing | resolved

const getToken = () => localStorage.getItem("access");

// โหลดรายการตามแท็บ
const loadReports = async () => {
  loading.value = true;

  let url = "";

  if (activeTab.value === "pending") url = "http://localhost:8000/api/reports/admin/pending/";
  if (activeTab.value === "processing") url = "http://localhost:8000/api/reports/admin/processing/";
  if (activeTab.value === "resolved") url = "http://localhost:8000/api/reports/admin/resolved/";

  try {
    const res = await axios.get(url, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    reports.value = res.data;
  } catch (err) {
    console.error("Error loading reports:", err);
  } finally {
    loading.value = false;
  }
};

onMounted(loadReports);

// เปลี่ยนแท็บ
const changeTab = (tab) => {
  activeTab.value = tab;
  loadReports();
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
    await axios.patch(
      `http://localhost:8000/api/reports/${id}/accept/`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    loadReports();
  } catch (err) {
    console.error("Accept error:", err);
    alert("รับเรื่องไม่สำเร็จ");
  }
};
</script>

<template>
  <div class="p-6">

    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
      <h1 class="text-2xl font-bold text-gray-800">จัดการรายงานปัญหา</h1>

      <router-link 
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- Tabs -->
    <div class="flex gap-3 mb-4">
      <button
        @click="changeTab('pending')"
        :class="activeTab === 'pending' ? 'bg-blue-600 text-white' : 'bg-gray-200'"
        class="px-4 py-2 rounded"
      >
        รอรับเรื่อง
      </button>

      <button
        @click="changeTab('processing')"
        :class="activeTab === 'processing' ? 'bg-blue-600 text-white' : 'bg-gray-200'"
        class="px-4 py-2 rounded"
      >
        กำลังดำเนินการ
      </button>

      <button
        @click="changeTab('resolved')"
        :class="activeTab === 'resolved' ? 'bg-blue-600 text-white' : 'bg-gray-200'"
        class="px-4 py-2 rounded"
      >
        แก้ไขเสร็จแล้ว
      </button>
    </div>

    <div v-if="loading">กำลังโหลด...</div>

    <table v-else class="w-full bg-white shadow rounded">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-3 text-left">หัวข้อ</th>
          <th class="p-3 text-left">พื้นที่</th>
          <th class="p-3 text-left">ผู้แจ้ง</th>
          <th class="p-3 text-left">วันที่สร้าง</th>
          <th class="p-3 text-center">การจัดการ</th>
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
          <td class="p-3">{{ r.created_at }}</td>

          <td class="p-3 text-center flex justify-center gap-2">

            <!-- ดูรายละเอียด -->
            <button
              class="text-blue-600 underline"
              @click="openDetail(r)"
            >
              ดูรายละเอียด
            </button>

            <!-- รับเรื่อง -->
            <button
              v-if="activeTab === 'pending'"
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
