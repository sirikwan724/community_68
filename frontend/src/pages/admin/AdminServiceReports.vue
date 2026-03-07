<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";

const loading = ref(true);
const error = ref("");
const reports = ref([]);

// Filters
const statusFilter = ref("");        // pending/processing/resolved/canceled
const categoryFilter = ref("");      // water/washer
const monthFilter = ref("");         // "01".."12"
const yearFilter = ref("");          // "2025".."2026" etc

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
  pending: "รอดำเนินการ",
  processing: "กำลังดำเนินการ",
  resolved: "เสร็จสิ้น",
  canceled: "รายงานไม่ถูกต้อง",
};

const statusClass = {
  pending: "bg-yellow-200 text-yellow-800",
  processing: "bg-blue-200 text-blue-800",
  resolved: "bg-green-200 text-green-800",
  canceled: "bg-gray-300 text-gray-700",
};

const categoryLabel = {
  water: "ตู้น้ำ",
  washer: "เครื่องซักผ้า",
  other: "บริการอื่นๆ",
};

const normalizeImageUrl = (img) => {
  if (!img) return "";
  if (String(img).startsWith("http")) return img;
  return `http://localhost:8000${img}`;
};

const formatThaiDT = (dt) => {
  if (!dt) return "-";
  const d = new Date(dt);
  if (isNaN(d.getTime())) return "-";
  return d.toLocaleString("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

// สำหรับกรองเดือน/ปี จาก created_at
const getMonth = (dt) => {
  const d = new Date(dt);
  if (isNaN(d.getTime())) return "";
  return String(d.getMonth() + 1).padStart(2, "0");
};
const getYear = (dt) => {
  const d = new Date(dt);
  if (isNaN(d.getTime())) return "";
  return String(d.getFullYear());
};

const fetchReports = async () => {
  loading.value = true;
  error.value = "";
  try {
    // โหลดทั้งหมดก่อน แล้วค่อย filter ที่ frontend
    const res = await api.get("/services/reports/admin/");
    reports.value = res.data.map((r) => ({
      ...r,
      image_url: normalizeImageUrl(r.image),
    }));
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.detail || "โหลดรายงานตู้บริการไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
};

const updateStatus = async (id, newStatus) => {
  try {
    await api.patch(`/services/reports/${id}/status/`, { status: newStatus });
    await fetchReports();
  } catch (e) {
    console.error(e);
    alert(e?.response?.data?.detail || "เปลี่ยนสถานะไม่สำเร็จ");
  }
};

const filteredList = computed(() => {
  return reports.value.filter((r) => {
    if (statusFilter.value && r.status !== statusFilter.value) return false;
    if (categoryFilter.value && r.service_category !== categoryFilter.value) return false;

    if (monthFilter.value && getMonth(r.created_at) !== monthFilter.value) return false;
    if (yearFilter.value && getYear(r.created_at) !== yearFilter.value) return false;

    return true;
  });
});

// สร้างรายการปีจากข้อมูลจริง (หรือจะทำเป็นช่วงปีคงที่ก็ได้)
const availableYears = computed(() => {
  const years = new Set(reports.value.map((r) => getYear(r.created_at)).filter(Boolean));
  return Array.from(years).sort((a, b) => Number(b) - Number(a));
});

onMounted(fetchReports);
</script>

<template>
  <div class="max-w-6xl mx-auto p-6 space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-2xl font-bold">รายงานปัญหาตู้บริการ</h1>

      <div class="flex flex-wrap gap-2 items-center">
        <!-- ประเภทบริการ -->
        <select v-model="categoryFilter" class="border rounded px-3 py-2">
          <option value="">ทุกประเภท</option>
          <option value="water">ตู้น้ำ</option>
          <option value="washer">เครื่องซักผ้า</option>
        </select>

        <!-- เดือน -->
        <select v-model="monthFilter" class="border rounded px-3 py-2">
          <option value="">ทุกเดือน</option>
          <option v-for="m in thaiMonths" :key="m.value" :value="m.value">
            {{ m.label }}
          </option>
        </select>

        <!-- ปี -->
        <select v-model="yearFilter" class="border rounded px-3 py-2">
          <option value="">ทุกปี</option>
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
        </select>

        <!-- สถานะรายงาน -->
        <select v-model="statusFilter" class="border rounded px-3 py-2">
          <option value="">ทุกสถานะ</option>
          <option value="pending">รอดำเนินการ</option>
          <option value="processing">กำลังดำเนินการ</option>
          <option value="resolved">เสร็จสิ้น</option>
          <option value="canceled">รายงานไม่ถูกต้อง</option>
        </select>

        <button
          @click="fetchReports"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          รีเฟรช
        </button>

        <router-link
          to="/admin/dashboard"
          class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
        >
          กลับหน้าหลัก
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="text-gray-600">กำลังโหลด...</div>
    <div v-else-if="error" class="text-red-600 font-medium">{{ error }}</div>

    <div v-else>
      <div v-if="filteredList.length === 0" class="text-gray-500">ไม่มีรายงาน</div>

      <div
        v-for="r in filteredList"
        :key="r.id"
        class="bg-white border rounded-lg p-4 shadow-sm"
      >
        <div class="flex flex-wrap justify-between gap-3">
          <!-- ซ้าย: ข้อมูลตามที่คุณต้องการ -->
          <div class="space-y-1">
            <!-- บรรทัดหัว: ประเภท + เลขตู้ -->
            <div class="font-bold text-lg">
              {{ categoryLabel[r.service_category] || "บริการ" }} • {{ r.service_name || "-" }}
            </div>

            <!-- สถานที่ -->
            <div class="text-sm text-gray-600">
              สถานที่: {{ r.service_location || "-" }}
            </div>

            <!-- ข้อความรายงาน: title + description ในบรรทัดเดียว -->
            <div class="text-gray-800">
              {{ r.title }} <span v-if="r.description"> — {{ r.description }}</span>
            </div>

            <!-- ผู้แจ้ง + เบอร์ -->
            <div class="text-sm text-gray-600">
              ผู้แจ้ง: {{ r.user_full_name || r.user_name || "-" }}
              <span v-if="r.user_phone"> | โทร: {{ r.user_phone }}</span>
            </div>

            <!-- วันเวลาไทย -->
            <div class="text-xs text-gray-500">
              แจ้งเมื่อ: {{ formatThaiDT(r.created_at) }}
            </div>
          </div>

          <!-- ขวา: สถานะ + dropdown -->
          <div class="flex items-center gap-2">
            <span
              class="px-3 py-1 rounded-full text-xs font-bold"
              :class="statusClass[r.status]"
            >
              {{ statusLabel[r.status] || r.status }}
            </span>

            <select
              class="border rounded px-2 py-1"
              :value="r.status"
              :disabled="['resolved','canceled'].includes(r.status)"
              :class="['resolved','canceled'].includes(r.status) ? 'opacity-50 cursor-not-allowed' : ''"
              @change="updateStatus(r.id, $event.target.value)"
            >
              <option value="pending">รอดำเนินการ</option>
              <option value="processing">กำลังดำเนินการ</option>
              <option value="resolved">เสร็จสิ้น</option>
              <option value="canceled">รายงานไม่ถูกต้อง</option>
            </select>
          </div>
        </div>

        <!-- รูปแนบ -->
        <div v-if="r.image_url" class="mt-3">
          <img :src="r.image_url" class="w-full max-w-xl h-64 object-cover rounded border" />
        </div>
      </div>
    </div>
  </div>
</template>