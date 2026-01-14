<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import AppointmentDetailModal from "../../components/AppointmentDetailModal.vue";

const token = localStorage.getItem("access");

const appointments = ref([]);
const filter = ref("all");
const selected = ref(null);

// ฟิลเตอร์
const selectedYear = ref("");
const selectedMonth = ref("");
const selectedStatus = ref("");

// ปี (ย้อนหลัง 5 ปี)
const currentYear = new Date().getFullYear();
const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

// เดือน
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

const modalOpen = ref(false);

// โหลดข้อมูลทั้งหมด
const loadAppointments = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/appointments/all/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    appointments.value = res.data;
  } catch (err) {
    console.error(err);
  }
};

// ฟิลเตอร์ข้อมูล
const filteredAppointments = computed(() => {
  return appointments.value.filter((item) => {
    const date = new Date(item.date);

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

// เปิด popup
const openDetail = (item) => {
  selected.value = item;
  modalOpen.value = true;
};

// อนุมัติ
const approve = async (id) => {
  if (!confirm("ยืนยันการอนุมัตินัดหมายนี้หรือไม่?")) return;
  try {
    await axios.patch(
      `http://localhost:8000/api/appointments/${id}/approve/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert("อนุมัติสำเร็จ");
    modalOpen.value = false;
    loadAppointments();
  } catch (err) {
    console.error(err);
  }
};

// ยกเลิก
const reject = async (id) => {
  if (!confirm("ต้องการยกเลิกนัดหมายนี้หรือไม่?")) return;
  try {
    await axios.patch(
      `http://localhost:8000/api/appointments/${id}/reject/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert("ยกเลิกสำเร็จ");
    modalOpen.value = false;
    loadAppointments();
  } catch (err) {
    console.error(err);
  }
};

// เสร็จสิ้น (ถ้ามี)
const done = async (id) => {
  if (!confirm("ยืนยันว่าดำเนินการเสร็จสิ้นแล้ว?")) return;
  try {
    await axios.patch(
      `http://localhost:8000/api/appointments/${id}/done/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert("อัปเดตสำเร็จ");
    modalOpen.value = false;
    loadAppointments();
  } catch (err) {
    console.error(err);
  }
};

onMounted(loadAppointments);
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto">

    <!-- หัวข้อ + ปุ่มกลับ -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">ตารางการนัดหมายทั้งหมด</h1>
      <!-- ฟิลเตอร์ -->
      <div class="flex gap-3 mb-6 flex-wrap">
      
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
      
        <!-- สถานะ -->
        <select v-model="selectedStatus" class="border rounded px-4 py-2">
          <option value="">ทุกสถานะ</option>
          <option value="pending">รออนุมัติ</option>
          <option value="approved">อนุมัติแล้ว</option>
          <option value="rejected">ถูกยกเลิก</option>
        </select>
        <router-link
          to="/admin/dashboard"
          class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
        >
          กลับหน้าหลัก
        </router-link>
      </div>
    </div>

    <!-- ตาราง -->
    <div class="overflow-x-auto bg-white shadow-md rounded-xl">
      <table class="min-w-full border-collapse">

        <!-- Header -->
        <thead class="bg-gray-100 text-gray-700">
          <tr>
            <th class="py-3 px-4 text-left border-b">ผู้ขอนัด</th>
            <th class="py-3 px-4 text-left border-b">วันที่</th>
            <th class="py-3 px-4 text-left border-b">เวลา</th>
            <th class="py-3 px-4 text-left border-b">สถานะ</th>
            <th class="py-3 px-4 text-center border-b">จัดการ</th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody>
          <tr
            v-for="item in filteredAppointments"
            :key="item.id"
            class="hover:bg-gray-50 transition"
          >
            <!-- ผู้ขอนัด -->
            <td class="py-3 px-4 border-b">{{ item.user_name }}</td>

            <!-- วันที่ -->
            <td class="py-3 px-4 border-b">
              {{ new Date(item.date).toLocaleDateString("th-TH") }}
            </td>

            <!-- เวลา -->
            <td class="py-3 px-4 border-b">
              {{ item.start_time.slice(0,5) }} - {{ item.end_time.slice(0,5) }}
            </td>

            <!-- สถานะ -->
            <td class="py-3 px-4 border-b">
              <span
                class="px-3 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-yellow-100 text-yellow-700': item.status === 'pending',
                  'bg-green-100 text-green-700': item.status === 'approved',
                  'bg-red-100 text-red-700': item.status === 'rejected'
                }"
              >
                {{ 
                  item.status === 'pending'
                    ? 'รออนุมัติ'
                    : item.status === 'approved'
                    ? 'อนุมัติแล้ว'
                    : 'ถูกยกเลิก'
                }}
              </span>
            </td>

            <!-- ปุ่มจัดการ -->
            <td class="py-3 px-4 border-b text-center flex gap-3 justify-center">

              <!-- ปุ่มดูรายละเอียด -->
              <button
                @click="openDetail(item)"
                class="text-blue-600 hover:text-blue-800 underline"
              >
                ดูรายละเอียด
              </button>

              <!-- ปุ่มอนุมัติ -->
              <button
                v-if="item.status === 'pending'"
                @click="approve(item.id)"
                class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                อนุมัติ
              </button>

              <!-- ปุ่มปฏิเสธ -->
              <button
                v-if="item.status === 'pending'"
                @click="reject(item.id)"
                class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              >
                ปฏิเสธ
              </button>

            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Popup -->
    <AppointmentDetailModal
      v-if="modalOpen"
      :appointment="selected"
      @close="modalOpen = false"
      @approve="approve"
      @reject="reject"
      @done="done"
    />

  </div>
</template>