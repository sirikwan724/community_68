<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import AppointmentDetailModal from "../../components/AppointmentDetailModal.vue";

const token = localStorage.getItem("access");

const appointments = ref([]);
const filter = ref("all");

const selected = ref(null);
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
  if (filter.value === "all") return appointments.value;
  return appointments.value.filter((item) => item.status === filter.value);
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
      `http://localhost:8000/api/appointments/${id}/accept/`,
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

      <router-link
        to="/admin/dashboard"
        class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- ปุ่มฟิลเตอร์ -->
    <div class="flex gap-3 mb-6 flex-wrap">

      <button
        @click="filter = 'all'"
        :class="filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >ทั้งหมด</button>

      <button
        @click="filter = 'approved'"
        :class="filter === 'approved' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >อนุมัติแล้ว</button>

      <button
        @click="filter = 'rejected'"
        :class="filter === 'rejected' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'"
        class="px-4 py-2 rounded-lg"
      >ถูกยกเลิก</button>

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
                {{ item.status }}
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