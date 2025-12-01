<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const reports = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const token = localStorage.getItem("access");

    const res = await axios.get(
      "http://localhost:8000/api/reports/admin/pending/",
      { headers: { Authorization: `Bearer ${token}` } }
    );

    reports.value = res.data;
  } catch (err) {
    console.error("Error loading reports:", err);
  } finally {
    loading.value = false;
  }
});

// -------------------------
//  ฟังก์ชันรับเรื่อง
// -------------------------
const acceptReport = async (id) => {
  if (!confirm("ยืนยันการรับเรื่องนี้หรือไม่?")) return;

  try {
    const token = localStorage.getItem("access");

    await axios.patch(
      `http://localhost:8000/api/reports/${id}/accept/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );

    // ลบรายการออกจากหน้านี้
    reports.value = reports.value.filter((r) => r.id !== id);

  } catch (err) {
    console.error("Accept error:", err);
    alert("ไม่สามารถรับเรื่องได้");
  }
};
</script>

<template>
  <div class="p-6">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
  
  <!-- หัวข้อ -->
  <h1 class="text-2xl font-bold text-gray-800">
    รายการคำร้องจากชาวบ้าน
  </h1>

  <!-- ปุ่มกลับหน้าหลัก (แบบเดิม สีเดิม) -->
                <router-link 
                   to="/admin/dashboard"
                   class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
                >
                   กลับหน้าหลัก
                </router-link>


</div>



    <div v-if="loading">กำลังโหลด...</div>

    <div v-else-if="reports.length === 0" class="text-gray-500">
      ยังไม่มีคำร้อง
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="r in reports"
        :key="r.id"
        class="p-4 bg-white shadow rounded border border-gray-200"
      >
        <p class="font-bold text-lg">{{ r.category }}</p>
        <p class="text-sm text-gray-600">
          ผู้แจ้ง: {{ r.user_data?.full_name || "ไม่ระบุ" }}
        </p>
        <p class="text-sm">พื้นที่: {{ r.area }}</p>
        <p class="text-sm">{{ r.description }}</p>

        <p class="text-xs text-gray-400 mt-1">
          ส่งเมื่อ: {{ r.created_at }}
        </p>

        <div v-if="r.image" class="mt-2">
          <img :src="`http://localhost:8000${r.user_data?.avatar}`" />
        </div>

        <!-- ปุ่มรับเรื่อง -->
        <button
          class="mt-3 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          @click="acceptReport(r.id)"
        >
          ✔ รับเรื่อง
        </button>
      </div>
    </div>
  </div>
</template>
