<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import Chart from "chart.js/auto";

const token = localStorage.getItem("access");

const reportChart = ref(null);
const requestChart = ref(null);

let chart1Instance;
let chart2Instance;

const loadStats = async () => {
  const res = await axios.get(
    "http://localhost:8000/api/reports/admin/stats/",
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const reports = res.data.reports_by_category;
  const requests = res.data.requests_by_type;

  createReportChart(reports);
  createRequestChart(requests);
};

const createReportChart = (data) => {
  if (chart1Instance) chart1Instance.destroy();

  const ctx = reportChart.value;

  chart1Instance = new Chart(ctx, {
    type: "pie",
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          data: Object.values(data),
        },
      ],
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
            font: {
              size: 16,
              family: "Prompt",
            },
          },
        },
      },
    },
  });
};

const createRequestChart = (data) => {
  if (chart2Instance) chart2Instance.destroy();

  const ctx = requestChart.value;

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
  });
};

onMounted(loadStats);
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">สถิติหมู่บ้าน</h1>

      <router-link
        to="/admin/dashboard"
        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg shadow"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- รายงานร้องเรียน (Pie Chart) -->
    <div class="bg-white shadow rounded p-4 mb-10">
      <h2 class="text-xl font-bold mb-4">
        รายงานร้องเรียน
      </h2>
    
      <div class="h-[560px] relative">
        <canvas ref="reportChart"></canvas>
      </div>
    </div>

    <!-- คำขอความอนุเคราะห์ (Bar Chart) -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-bold mb-4">จำนวนคำขอความอนุเคราะห์</h2>
      <canvas ref="requestChart"></canvas>
    </div>
  </div>
</template>
