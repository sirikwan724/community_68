<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import RequestHelpDetailModal from "../../components/RequestHelpDetailModal.vue";

const list = ref([]);
const selected = ref(null);
const modalOpen = ref(false);
const token = localStorage.getItem("access");

// ⭐ ฟิลเตอร์สถานะ
const filter = ref("all");

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

// ⭐ ฟิลเตอร์ข้อมูลตามสถานะ
const filteredList = computed(() => {
  if (filter.value === "all") return list.value;
  return list.value.filter((item) => item.status === filter.value);
});

onMounted(loadData);
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">คำขอความอนุเคราะห์</h2>

      <router-link 
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- ⭐ ปุ่ม Filter -->
    <div class="flex gap-3 mb-5">

      <button 
        @click="filter = 'all'"
        :class="filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >
        ทั้งหมด
      </button>

      <button 
        @click="filter = 'pending'"
        :class="filter === 'pending' ? 'bg-yellow-500 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >
        รอดำเนินการ
      </button>

      <button 
        @click="filter = 'approved'"
        :class="filter === 'approved' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >
        อนุมัติแล้ว
      </button>

      <button 
        @click="filter = 'rejected'"
        :class="filter === 'rejected' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >
        ปฏิเสธ
      </button>

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
                {{ item.status }}
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
