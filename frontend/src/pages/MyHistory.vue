<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const activeTab = ref("reports"); 
// reports | requests | all

const reports = ref([]);
const requests = ref([]);
const merged = ref([]);

const token = localStorage.getItem("access");

// -------------------------------------------------------
// FORMAT วันที่
// -------------------------------------------------------
const formatDT = (dt) => {
  return new Date(dt).toLocaleString("th-TH", {
    dateStyle: "long",
    timeStyle: "short",
  });
};

// -------------------------------------------------------
// โหลดรายงานปัญหา (Report)
// -------------------------------------------------------
const loadReports = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/reports/my/", {
      headers: { Authorization: `Bearer ${token}` },
    });

    reports.value = res.data.map((i) => ({
      id: i.id,
      type: "report",
      title: i.category,
      detail: i.description,
      status: i.status,
      created_at: i.created_at,
    }));
  } catch (err) {
    console.error("โหลดรายงานผิดพลาด", err);
  }
};

// -------------------------------------------------------
// โหลดคำขอความอนุเคราะห์ (Request Help)
// -------------------------------------------------------
const loadRequests = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/reports/help/my/", {
      headers: { Authorization: `Bearer ${token}` },
    });

    console.log("DATA FROM API:", res.data); 

    requests.value = res.data.map((i) => ({
      id: i.id,
      type: "request",
      title: i.request_type ?? "(ไม่พบประเภท)",
      detail: i.detail ?? "(ไม่มีรายละเอียด)",
      status: i.status,
      created_at: i.created_at,
    }));
  } catch (err) {
    console.error("โหลดคำขอความอนุเคราะห์ผิดพลาด", err);
  }
};


// -------------------------------------------------------
// รวมข้อมูลทั้งหมด
// -------------------------------------------------------
const mergeAll = () => {
  merged.value = [...reports.value, ...requests.value].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
};

// -------------------------------------------------------
// ยกเลิกรายงาน (เฉพาะ Report)
// -------------------------------------------------------
const cancelReport = async (id) => {
  if (!confirm("ต้องการยกเลิกคำร้องนี้หรือไม่?")) return;

  try {
    await axios.delete(
      `http://localhost:8000/api/reports/${id}/cancel/`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    alert("ยกเลิกคำร้องสำเร็จ");
    loadReports();
  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาด ไม่สามารถยกเลิกได้");
  }
};

// -------------------------------------------------------
// เมื่อเปิดหน้าให้โหลดข้อมูล
// -------------------------------------------------------
onMounted(async () => {
  await loadReports();
  await loadRequests();
  mergeAll();
});
</script>

<template>
  <div class="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow">

    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-blue-600">
        ประวัติของฉัน
      </h2>
      <router-link
        to="/"
        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg shadow"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- Tabs -->
    <div class="flex gap-4 mb-6 border-b pb-2">
      <button
        @click="activeTab = 'reports'"
        :class="activeTab === 'reports'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        รายงานปัญหา
      </button>

      <button
        @click="activeTab = 'requests'"
        :class="activeTab === 'requests'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        ขอความอนุเคราะห์
      </button>

      <button
        @click="activeTab = 'all'"
        :class="activeTab === 'all'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        ทั้งหมด
      </button>
    </div>

    <!-- เนื้อหา -->
    <div>

      <!-- รายงานปัญหา -->
      <div v-if="activeTab === 'reports'">
        <div v-if="reports.length === 0" class="text-gray-500">
          ไม่มีประวัติรายงาน
        </div>

        <div
          v-for="item in reports"
          :key="item.id"
          class="border rounded-md p-4 mb-4"
        >
          <div class="flex justify-between">
            <h3 class="font-bold text-lg">{{ item.title }}</h3>

            <span
              class="px-2 py-1 rounded text-white text-sm"
              :class="{
                'bg-yellow-500': item.status === 'pending',
                'bg-blue-500': item.status === 'processing',
                'bg-green-600': item.status === 'resolved',
              }"
            >
              {{ item.status }}
            </span>
          </div>

          <p class="text-gray-600 mt-2">{{ item.detail }}</p>

          <p class="text-sm text-gray-400 mt-1">
            ส่งเมื่อ: {{ formatDT(item.created_at) }}
          </p>

          <!-- ปุ่มแก้ไข & ยกเลิก -->
          <div v-if="item.status === 'pending'" class="mt-4 flex gap-3">
            <button
              @click="$router.push(`/report/edit/${item.id}`)"
              class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
            >
              แก้ไข
            </button>

            <button
              @click="cancelReport(item.id)"
              class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
            >
              ยกเลิกคำร้อง
            </button>
          </div>

        </div>
      </div>

      <!-- คำขอความอนุเคราะห์ -->
      <div v-if="activeTab === 'requests'">
        <div v-if="requests.length === 0" class="text-gray-500">
          ไม่มีประวัติคำขอความอนุเคราะห์
        </div>

        <div
          v-for="item in requests"
          :key="item.id"
          class="border rounded-md p-4 mb-4"
        >
          <div class="flex justify-between">
            <h3 class="font-bold text-lg">{{ item.title }}</h3>

            <span
              class="px-2 py-1 rounded text-white text-sm"
              :class="{
                'bg-yellow-500': item.status === 'pending',
                'bg-green-600': item.status === 'approved',
                'bg-red-600': item.status === 'rejected',
                'bg-purple-600': item.status === 'done',
              }"
            >
              {{ item.status }}
            </span>
          </div>

          <p class="text-gray-600 mt-2">{{ item.detail }}</p>

          <p class="text-sm text-gray-400 mt-1">
            ส่งเมื่อ: {{ formatDT(item.created_at) }}
          </p>
        </div>
      </div>

      <!-- ทั้งหมด -->
      <div v-if="activeTab === 'all'">
        <div v-if="merged.length === 0" class="text-gray-500">
          ยังไม่มีประวัติ
        </div>

        <div
          v-for="item in merged"
          :key="item.id"
          class="border rounded-md p-4 mb-4"
        >
          <div class="flex justify-between">

            <h3 class="font-bold text-lg">
              {{ item.type === 'report' ? 'รายงาน: ' : 'ขอความอนุเคราะห์: ' }}
              {{ item.title }}
            </h3>

            <span
              class="px-2 py-1 rounded text-white text-sm"
              :class="{
                'bg-yellow-500': item.status === 'pending',
                'bg-blue-500': item.status === 'processing',
                'bg-green-600': item.status === 'resolved',
                'bg-green-700': item.status === 'approved',
                'bg-red-600': item.status === 'rejected',
                'bg-purple-600': item.status === 'done',
              }"
            >
              {{ item.status }}
            </span>

          </div>

          <p class="text-gray-600 mt-2">{{ item.detail }}</p>

          <p class="text-sm text-gray-400 mt-1">
            ส่งเมื่อ: {{ formatDT(item.created_at) }}
          </p>

        </div>
      </div>

    </div>

  </div>
</template>
