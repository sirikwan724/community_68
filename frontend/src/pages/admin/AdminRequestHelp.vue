<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import RequestHelpDetailModal from "../../components/RequestHelpDetailModal.vue";

const list = ref([]);
const selected = ref(null);
const modalOpen = ref(false);
const token = localStorage.getItem("access");

//  ฟิลเตอร์ ปี / เดือน / สถานะ
const selectedYear = ref("");
const selectedMonth = ref("");
const filter = ref("all");
const selectedStatus = ref("");

// =======================
// ปี (ย้อนหลัง 5 ปี)
// =======================
const currentYear = new Date().getFullYear();
const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

// =======================
// เดือน
// =======================
const months = [
  { value: 1, label: "มกราคม" },
  { value: 2, label: "กุมภาพันธ์" },
  { value: 3, label: "มีนาคม" },
  { value: 4, label: "เมษายน" },
  { value: 5, label: "พฤษภาคม" },
  { value: 6, label: "มิถุนายน" },
  { value: 7, label: "กรกฎาคม" },
  { value: 8, label: "สิงหาคม" },
  { value: 9, label: "กันยายน" },
  { value: 10, label: "ตุลาคม" },
  { value: 11, label: "พฤศจิกายน" },
  { value: 12, label: "ธันวาคม" },
];

// โหลดข้อมูล
const loadData = async () => {
  const res = await axios.get("http://localhost:8000/api/reports/help/admin/", {
    headers: { Authorization: `Bearer ${token}` },
  });
  list.value = res.data;
};

// เปิด Modal
const openDetail = (item) => {
  selected.value = item;
  modalOpen.value = true;
};

// อนุมัติ
const approve = async (id) => {
  await axios.patch(
    `http://localhost:8000/api/reports/help/${id}/approve/`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  modalOpen.value = false;
  loadData();
};

// แปลงวันเวลาให้อ่านง่าย
const formatTime = (datetime) => {
  if (!datetime) return "-";
  return new Date(datetime).toLocaleString("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

// ฟิลเตอร์
const filteredList = computed(() => {
  return list.value.filter(item => {
    const date = new Date(item.start_datetime);

    const matchYear =
      !selectedYear.value ||
      date.getFullYear() === Number(selectedYear.value);

    const matchMonth =
      !selectedMonth.value ||
      date.getMonth() + 1 === Number(selectedMonth.value);

    const matchStatus =
      !selectedStatus.value ||
      item.status === selectedStatus.value;

    return matchYear && matchMonth && matchStatus;
  });
});

onMounted(loadData);
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">คำขอความอนุเคราะห์</h2>
            <!-- ฟิลเตอร์ ปี / เดือน -->
      <div class="flex gap-3 mb-4">
      
        <!-- ปี -->
        <select v-model="selectedYear" class="border rounded px-4 py-2">
          <option value="">ทุกปี</option>
          <option v-for="y in years" :key="y" :value="y">
            {{ y }}
          </option>
        </select>
      
        <!-- เดือน -->
        <select v-model="selectedMonth" class="border rounded px-4 py-2">
          <option value="">ทุกเดือน</option>
          <option v-for="m in months" :key="m.value" :value="m.value">
            {{ m.label }}
          </option>
        </select>
        <select v-model="selectedStatus" class="border rounded px-4 py-2">
          <option value="">ทุกสถานะ</option>
          <option value="pending">รอดำเนินการ</option>
          <option value="approved">อนุมัติแล้ว</option>
          <option value="rejected">ปฏิเสธ</option>
        </select>

        <router-link 
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
        >
        กลับหน้าหลัก
        </router-link>
      
      </div>
    </div>

    <!-- Data Table -->
    <div class="overflow-x-auto bg-white shadow-md rounded-xl">
      <table class="min-w-full border-collapse">

        <!-- Header -->
        <thead class="bg-gray-100 text-gray-700">
          <tr>
            <th class="py-3 px-4 text-left border-b">ประเภท</th>
            <th class="py-3 px-4 text-left border-b">ช่วงเวลา</th>
            <th class="py-3 px-4 text-left border-b">สถานที่</th>
            <th class="py-3 px-4 text-left border-b">สถานะ</th>
            <th class="py-3 px-4 text-center border-b">ดูรายละเอียด</th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody>
          <tr
            v-for="item in filteredList"
            :key="item.id"
            class="hover:bg-gray-50 transition"
          >
            <td class="py-3 px-4 border-b">{{ item.request_type }}</td>

            <td class="py-3 px-4 border-b">
              {{ formatTime(item.start_datetime) }} 
              - 
              {{ formatTime(item.end_datetime) }}
            </td>

            <td class="py-3 px-4 border-b">{{ item.area }}</td>

            <!-- Badge สถานะ -->
            <td class="py-3 px-4 border-b">
              <span
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-yellow-100 text-yellow-700': item.status === 'pending',
                  'bg-green-100 text-green-700': item.status === 'approved',
                  'bg-red-100 text-red-700': item.status === 'rejected',
                }"
              >
                {{ 
                  item.status === 'pending'
                     ? 'รอดำเนินการ'
                     : item.status === 'approved'
                     ? 'อนุมัติแล้ว'
                     : 'ปฏิเสธ' 
                }}
              </span>
            </td>

            <!-- ปุ่มดูรายละเอียด -->
            <td class="py-3 px-4 border-b text-center">
              <button
                @click="openDetail(item)"
                class="text-blue-600 hover:text-blue-800 font-medium underline"
              >
                ดูรายละเอียด
              </button>
            </td>
          </tr>
        </tbody>

      </table>
    </div>

    <!-- Modal -->
    <RequestHelpDetailModal
      :show="modalOpen"
      :data="selected"
      @close="modalOpen = false"
      @approve="approve"
    />

  </div>
</template>
