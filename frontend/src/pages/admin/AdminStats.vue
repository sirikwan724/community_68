<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";
import Chart from "chart.js/auto";

const getToken = () => localStorage.getItem("access");

// Canvas refs
const reportChart = ref(null);
const requestChart = ref(null);
const borrowItemChart = ref(null);
const borrowLocationChart = ref(null);

// chart instances
let chart1Instance;
let chart2Instance;
let chart3Instance;
let chart4Instance;

const loadStats = async () => {
  const token = getToken();
  if (!token) return;

  try {
    // ✅ ยิงพร้อมกัน: ของเดิม + ยืม/จอง 2 ตัว
    const [resReport, resBorrowItems, resBorrowLocations] = await Promise.all([
      axios.get("http://localhost:8000/api/reports/admin/stats/", {
        headers: { Authorization: `Bearer ${token}` },
      }),

      axios.get("http://localhost:8000/api/borrow/admin/stats/borrow-items/", {
        headers: { Authorization: `Bearer ${token}` },
      }),

      axios.get("http://localhost:8000/api/borrow/admin/stats/borrow-locations/", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ]);

    // ของเดิม
    const reports = resReport.data.reports_by_category || {};
    const requests = resReport.data.requests_by_type || {};

    createReportChart(reports);
    createRequestChart(requests);

    // ✅ ของใหม่: ยืม/จอง (approved เท่านั้น)
    createBorrowItemChart(resBorrowItems.data || {});
    createBorrowLocationChart(resBorrowLocations.data || {});
  } catch (err) {
    console.error("loadStats error:", err);
  }
};

// -------------------------
// 1) Pie: รายงานร้องเรียน
// -------------------------
const createReportChart = (data) => {
  if (chart1Instance) chart1Instance.destroy();
  if (!reportChart.value) return;

  const ctx = reportChart.value.getContext("2d");

  chart1Instance = new Chart(ctx, {
    type: "pie",
    data: {
      labels: Object.keys(data),
      datasets: [{ data: Object.values(data) }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      radius: "100%",
      plugins: {
        legend: {
          position: "top",
          labels: {
            boxWidth: 30,
            boxHeight: 18,
            padding: 20,
            font: { size: 16, family: "Prompt" },
          },
        },
      },
    },
  });
};

// -------------------------
// 2) Bar: คำขอความอนุเคราะห์
// -------------------------
const createRequestChart = (data) => {
  if (chart2Instance) chart2Instance.destroy();
  if (!requestChart.value) return;

  const ctx = requestChart.value.getContext("2d");

  chart2Instance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          label: "จำนวนคำขอทั้งหมด",
          data: Object.values(data),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
    },
  });
};

// -------------------------
// 3) Bar: ยืมสิ่งของ (approved)
// data = {"เก้าอี้": 10, "โต๊ะ": 5}
// -------------------------
const createBorrowItemChart = (data) => {
  if (chart3Instance) chart3Instance.destroy();
  if (!borrowItemChart.value) return;

  const labels = Object.keys(data);
  const values = Object.values(data);

  const ctx = borrowItemChart.value.getContext("2d");

  chart3Instance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "จำนวนที่ยืม (อนุมัติแล้ว)",
          data: values,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
    },
  });
};

// -------------------------
// 4) Doughnut: จองสถานที่ (approved)
// data = {"ศาลาประชาคม": 3, "สนามกีฬา": 1}
// -------------------------
const createBorrowLocationChart = (data) => {
  if (chart4Instance) chart4Instance.destroy();
  if (!borrowLocationChart.value) return;

  const labels = Object.keys(data);
  const values = Object.values(data);

  const ctx = borrowLocationChart.value.getContext("2d");

  chart4Instance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "60%",
      plugins: {
        legend: {
          position: "top",
          labels: { font: { size: 14, family: "Prompt" } },
        },
      },
    },
  });
};

onMounted(loadStats);

onBeforeUnmount(() => {
  if (chart1Instance) chart1Instance.destroy();
  if (chart2Instance) chart2Instance.destroy();
  if (chart3Instance) chart3Instance.destroy();
  if (chart4Instance) chart4Instance.destroy();
});
</script>

<template>
  <div class="p-6 space-y-10">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold">สถิติหมู่บ้าน</h1>

      <router-link
        to="/admin/dashboard"
        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg shadow"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- รายงานร้องเรียน (Pie Chart) -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-bold mb-4">รายงานร้องเรียน</h2>
      <div class="h-[560px] relative">
        <canvas ref="reportChart"></canvas>
      </div>
    </div>

    <!-- คำขอความอนุเคราะห์ (Bar Chart) -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-bold mb-4">จำนวนคำขอความอนุเคราะห์</h2>
      <div class="h-[360px] relative">
        <canvas ref="requestChart"></canvas>
      </div>
    </div>

    <!-- ✅ ยืมสิ่งของ (approved) -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-bold mb-4">สถิติการยืมสิ่งของ (อนุมัติแล้ว)</h2>
      <div class="h-[420px] relative">
        <canvas ref="borrowItemChart"></canvas>
      </div>
    </div>

    <!-- ✅ จองสถานที่ (approved) -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-bold mb-4">สถิติการจองสถานที่ (อนุมัติแล้ว)</h2>
      <div class="h-[420px] relative">
        <canvas ref="borrowLocationChart"></canvas>
      </div>
    </div>
  </div>
</template>
