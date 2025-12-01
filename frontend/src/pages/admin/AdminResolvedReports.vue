<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const reports = ref([]);
const loading = ref(true);

const loadData = async () => {
  try {
    const token = localStorage.getItem("access");

    const res = await axios.get(
      "http://localhost:8000/api/reports/admin/resolved/",
      { headers: { Authorization: `Bearer ${token}` } }
    );

    reports.value = res.data;
  } catch (err) {
    console.error("load error:", err);
  } finally {
    loading.value = false;
  }
};

// Rollback
const rollbackReport = async (id) => {
  if (!confirm("ย้อนกลับเป็นกำลังดำเนินการใช่ไหม?")) return;

  try {
    const token = localStorage.getItem("access");

    await axios.patch(
      `http://localhost:8000/api/reports/${id}/rollback/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );

    reports.value = reports.value.filter((r) => r.id !== id);
  } catch (err) {
    console.error("Rollback error:", err);
    alert("ย้อนกลับไม่สำเร็จ");
  }
};

onMounted(loadData);
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">✅ รายงานที่แก้ไขแล้ว (Resolved)</h1>

    <div v-if="loading">กำลังโหลด...</div>

    <div v-else-if="reports.length === 0" class="text-gray-500">
      ยังไม่มีรายงานที่เสร็จสมบูรณ์
    </div>

    <div v-else class="space-y-4">
      <div v-for="r in reports" :key="r.id" class="p-4 bg-white rounded shadow">
        <p class="font-bold text-lg">{{ r.category }}</p>
        <p>พื้นที่: {{ r.area }}</p>
        <p>{{ r.description }}</p>

        <!-- แสดงโน้ต -->
        <div class="mt-3" v-if="r.notes.length > 0">
          <p class="font-semibold">โน้ตงาน:</p>
          <ul class="text-sm text-gray-600 space-y-1">
            <li v-for="n in r.notes" :key="n.id">
              - {{ n.message }} ({{ n.created_at }})
            </li>
          </ul>
        </div>

        <!-- rollback button -->
        <button
          @click="rollbackReport(r.id)"
          class="mt-3 px-4 py-1 bg-yellow-600 text-white rounded"
        >
          ย้อนกลับสถานะ
        </button>
      </div>
    </div>
  </div>
</template>
