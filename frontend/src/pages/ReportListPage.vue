<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const reports = ref([]);       
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const token = localStorage.getItem("access");
    console.log("TOKEN:", token);

    const res = await axios.get("http://localhost:8000/api/reports/my/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    reports.value = res.data;

  } catch (err) {
    console.error("Error loading reports:", err);
    error.value = "โหลดข้อมูลไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
});

// ยกเลิกรายงาน
const cancelReport = async (id) => {
  if (!confirm("ต้องการยกเลิกรายงานนี้หรือไม่?")) return;

  try {
    const token = localStorage.getItem("access");

    await axios.delete(`http://localhost:8000/api/reports/${id}/cancel/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // ลบออกจากหน้าจอทันที
    reports.value = reports.value.filter((r) => r.id !== id);

    alert("ยกเลิกรายงานสำเร็จ");

  } catch (err) {
    console.error("Cancel error:", err);
    alert("ไม่สามารถยกเลิกรายงานได้");
  }
};

</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">

  <div class="flex justify-between items-center mb-6">
    <h1 class="text-2xl font-bold">รายการคำร้องของฉัน</h1>

    <router-link
      to="/"
      class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg shadow"
    >
       กลับหน้าหลัก
    </router-link>
  </div>
    <!-- แสดงสถานะโหลด -->
    <div v-if="loading">กำลังโหลดข้อมูล...</div>

    <!-- แสดง error -->
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <!-- ไม่มีข้อมูล -->
    <div v-if="!loading && reports.length === 0">
      ยังไม่มีคำร้องที่ส่งเข้ามา
    </div>

    <!-- รายการคำร้อง -->
    <div
      v-for="report in reports"
      :key="report.id"
      class="p-4 bg-white shadow rounded border mb-4"
    >
      <h2 class="font-bold text-lg mb-1">{{ report.category }}</h2>

      <p>รายละเอียด: {{ report.description }}</p>
      <p>พื้นที่: {{ report.area }}</p>

      <p class="text-sm text-gray-500 mt-1">
        ส่งเมื่อ: {{ report.created_at }}
      </p>

      <div class="flex gap-2 mt-3">

        <!-- ปุ่มแก้ไข -->
        <router-link
          v-if="report.status === 'pending'"
          :to="`/report/edit/${report.id}`"
          class="px-4 py-1 bg-blue-500 text-white rounded"
        >
          แก้ไข
        </router-link>

        <!-- ปุ่มยกเลิก -->
        <button
          v-if="report.status === 'pending'"
          @click="cancelReport(report.id)"
          class="px-4 py-1 bg-red-500 text-white rounded"
        >
          ยกเลิกรายงาน
        </button>

        <!-- สถานะอื่น -->
        <div v-else class="px-4 py-1 bg-gray-300 rounded text-gray-700">
          ผู้ใหญ่บ้านรับเรื่องแล้ว
        </div>

      </div>
    </div>
  </div>
</template>
