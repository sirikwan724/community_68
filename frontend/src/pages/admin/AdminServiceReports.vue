<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";

const loading = ref(true);
const error = ref("");
const reports = ref([]);
const selectedReport = ref(null);
const showUserDetail = ref(false);
const userDetail = ref(null);
const userDetailLoading = ref(false);
// Filters
const statusFilter = ref("");
const categoryFilter = ref("");
const monthFilter = ref("");
const yearFilter = ref("");

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
    if (selectedReport.value?.id === id) {
      selectedReport.value = reports.value.find((r) => r.id === id) || null;
    }
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

const availableYears = computed(() => {
  const years = new Set(reports.value.map((r) => getYear(r.created_at)).filter(Boolean));
  return Array.from(years).sort((a, b) => Number(b) - Number(a));
});

const openDetail = (r) => {
  selectedReport.value = r;
};

const closeModal = () => {
  selectedReport.value = null;
  showUserDetail.value = false;
  userDetail.value = null;
};

const toggleUserDetail = async () => {
  if (showUserDetail.value) {
    showUserDetail.value = false;
    return;
  }
  userDetailLoading.value = true;
  try {
    const res = await api.get("/accounts/admin/users/");
    userDetail.value = res.data.find(u => u.id === selectedReport.value.user_id) || null;
    showUserDetail.value = true;
  } catch (e) {
    alert("โหลดข้อมูลผู้แจ้งไม่สำเร็จ");
  } finally {
    userDetailLoading.value = false;
  }
};

onMounted(fetchReports);
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
      <h1 class="text-2xl font-bold text-gray-800">รายงานปัญหาตู้บริการ</h1>

      <div class="flex flex-wrap items-center gap-2">
        <!-- ประเภทบริการ -->
        <select v-model="categoryFilter" class="border rounded px-3 py-2">
          <option value="">ทุกประเภท</option>
          <option value="water">ตู้น้ำ</option>
          <option value="washer">เครื่องซักผ้า</option>
          <option value="other">บริการอื่นๆ</option>
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

        <!-- สถานะ -->
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

    <!-- Loading / Error -->
    <div v-if="loading" class="text-gray-600">กำลังโหลด...</div>
    <div v-else-if="error" class="text-red-600 font-medium">{{ error }}</div>

    <!-- Table -->
    <table v-else class="w-full bg-white shadow rounded">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-3 text-left">ประเภทบริการ</th>
          <th class="p-3 text-left">เลขเครื่อง</th>
          <th class="p-3 text-left">สถานที่</th>
          <th class="p-3 text-left">วันที่แจ้ง</th>
          <th class="p-3 text-left">ผู้แจ้ง</th>
          <th class="p-3 text-center">สถานะ</th>
        </tr>
      </thead>

      <tbody>
        <tr v-if="filteredList.length === 0">
          <td colspan="6" class="p-4 text-center text-gray-500">ไม่มีรายงาน</td>
        </tr>

        <tr
          v-for="r in filteredList"
          :key="r.id"
          class="border-b hover:bg-gray-50"
        >
          <td class="p-3">{{ categoryLabel[r.service_category] || "-" }}</td>
          <td class="p-3">{{ r.service_name || "-" }}</td>
          <td class="p-3">{{ r.service_location || "-" }}</td>
          <td class="p-3">{{ formatThaiDT(r.created_at) }}</td>
          <td class="p-3">{{ r.user_full_name || "-" }}</td>
          <td class="p-3 text-center">
            <div class="flex items-center justify-center gap-2">
              <span
                class="px-3 py-1 rounded-full text-xs font-bold"
                :class="statusClass[r.status]"
              >
                {{ statusLabel[r.status] || r.status }}
              </span>
              <button
                class="text-blue-600 underline text-sm"
                @click="openDetail(r)"
              >
                ดูรายละเอียด
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Modal -->
    <div
      v-if="selectedReport"
      class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white p-6 w-full max-w-xl rounded shadow-lg relative max-h-[90vh] overflow-y-auto">
        <!-- ปุ่มปิด -->
        <button
          class="absolute top-2 right-2 text-gray-600 text-xl"
          @click="closeModal"
        >
          ✕
        </button>

        <h2 class="text-xl font-bold mb-4">รายละเอียดรายงาน</h2>

        <div class="space-y-2">
          <p>
            <strong>ประเภทบริการ:</strong>
            {{ categoryLabel[selectedReport.service_category] || "-" }}
          </p>
          <p><strong>เลขเครื่อง:</strong> {{ selectedReport.service_name || "-" }}</p>
          <p><strong>สถานที่:</strong> {{ selectedReport.service_location || "-" }}</p>
          <p>
            <strong>ผู้แจ้ง:</strong>
            <button
              class="text-blue-600 underline ml-1"
              @click="toggleUserDetail"
            >
              {{ selectedReport.user_full_name || "-" }}
            </button>
          </p>

          <!-- กล่องรายละเอียดผู้แจ้ง -->
          <div v-if="userDetailLoading" class="ml-4 text-sm text-gray-400">
            กำลังโหลด...
          </div>
          <div
            v-if="showUserDetail && userDetail"
            class="ml-4 mt-1 p-3 bg-gray-50 border rounded text-sm space-y-1"
          >
            <p><strong>ชื่อ-นามสกุล:</strong> {{ userDetail.full_name || "-" }}</p>
            <p><strong>เบอร์โทร:</strong> {{ userDetail.phone || "-" }}</p>
            <p><strong>ที่อยู่:</strong> {{ userDetail.address || "-" }}</p>
            <p><strong>เลขทะเบียนบ้าน:</strong> {{ userDetail.citizen_id || "-" }}</p>
          </div>
          <p><strong>หัวข้อปัญหา:</strong> {{ selectedReport.title || "-" }}</p>
          <p v-if="selectedReport.description">
            <strong>รายละเอียด:</strong> {{ selectedReport.description }}
          </p>
          <p><strong>วันที่แจ้ง:</strong> {{ formatThaiDT(selectedReport.created_at) }}</p>

          <!-- รูปแนบ -->
          <div v-if="selectedReport.image_url" class="mt-3">
            <img
              :src="selectedReport.image_url"
              class="w-full max-h-64 object-cover rounded border"
            />
          </div>
        </div>

        <!-- อัปเดตสถานะ -->
        <div class="mt-6">
          <label class="font-semibold">อัปเดตสถานะ</label>

          <!-- pending → รอรับเรื่องอยู่ -->
          <div v-if="selectedReport.status === 'pending'" class="flex gap-2 mt-3">
            <button
              class="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
              @click="updateStatus(selectedReport.id, 'processing')"
            >
              รับเรื่อง
            </button>
            <button
              class="flex-1 bg-gray-400 text-white py-2 rounded hover:bg-gray-500"
              @click="updateStatus(selectedReport.id, 'canceled')"
            >
              รายงานไม่ถูกต้อง
            </button>
          </div>

          <!-- processing → กำลังดำเนินการ -->
          <div v-else-if="selectedReport.status === 'processing'" class="flex gap-2 mt-3">
            <button
              class="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700"
              @click="updateStatus(selectedReport.id, 'resolved')"
            >
              ดำเนินการเสร็จสิ้น
            </button>
            <button
              class="flex-1 bg-gray-400 text-white py-2 rounded hover:bg-gray-500"
              @click="updateStatus(selectedReport.id, 'canceled')"
            >
              รายงานไม่ถูกต้อง
            </button>
          </div>

          <!-- resolved / canceled → ปิดงานแล้ว -->
          <p v-else class="text-sm text-gray-400 mt-3">
            รายงานนี้ปิดแล้ว ไม่สามารถเปลี่ยนสถานะได้
          </p>
        </div>
      </div>
    </div>
  </div>
</template>