<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import AppointmentDetailModal from "../components/AppointmentDetailModal.vue";

const router = useRouter();
const token = localStorage.getItem("access");

const appointments = ref([]);
const selected = ref(null);
const modalOpen = ref(false);

// โหลดข้อมูลนัดหมายของ user
const loadAppointments = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/appointment/my/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    appointments.value = res.data;
  } catch (err) {
    console.error(err);
  }
};

const openDetail = (item) => {
  selected.value = item;
  modalOpen.value = true;
};

// ยกเลิกนัดหมาย
const cancelAppointment = async (id) => {
  if (!confirm("ยืนยันการยกเลิกนัดหมายนี้หรือไม่?")) return;

  try {
    await axios.patch(
      `http://localhost:8000/api/appointment/${id}/cancel/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );

    alert("ยกเลิกนัดหมายสำเร็จ");
    loadAppointments();

  } catch (err) {
    console.error(err);
    alert("ไม่สามารถยกเลิกนัดหมายได้");
  }
};

// แปลงวันที่ให้สวยงาม
const formatDate = (date) => {
  return new Date(date).toLocaleDateString("th-TH", { dateStyle: "long" });
};
const formatTime = (t) => (t ? t.slice(0, 5) : "-");

onMounted(loadAppointments);
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">

    <!-- ปุ่มกลับ -->
    <router-link
      to="/"
      class="inline-block bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
    >
       กลับหน้าหลัก
    </router-link>

    <h1 class="text-2xl font-bold mt-6 mb-4">การนัดหมายของฉัน</h1>

    <div v-if="appointments.length === 0" class="text-gray-500 mt-10">
      ยังไม่มีการนัดหมาย
    </div>

    <!-- รายการนัดหมาย -->
    <div class="space-y-4 mt-6">

      <div
        v-for="item in appointments"
        :key="item.id"
        class="bg-white border shadow p-4 rounded-lg flex justify-between items-start"
      >
        <div>
          <p class="font-semibold text-lg">{{ item.target }}</p>

          <p class="text-sm text-gray-600">
            วันที่นัดหมาย: {{ formatDate(item.date) }}
          </p>

          <p class="text-sm text-gray-600">
            เวลา: {{ formatTime(item.start_time) }} - {{ formatTime(item.end_time) }}
          </p>

          <p class="text-sm text-gray-600">
            สถานที่: {{ item.place }}
          </p>

          <!-- Badge สถานะ -->
          <span
            class="inline-block mt-2 px-3 py-1 text-xs rounded-full font-semibold"
            :class="{
              'bg-yellow-100 text-yellow-700': item.status === 'pending',
              'bg-green-100 text-green-700': item.status === 'approved',
              'bg-red-100 text-red-700': item.status === 'rejected',
              'bg-blue-100 text-blue-700': item.status === 'done',
            }"
          >
            {{
              item.status === "pending"
                ? "รอดำเนินการ"
                : item.status === "approved"
                ? "อนุมัติแล้ว"
                : item.status === "rejected"
                ? "ถูกยกเลิก"
                : "ดำเนินการเสร็จสิ้น"
            }}
          </span>

        </div>

        <!-- ปุ่มด้านขวา -->
        <div class="flex flex-col gap-2">

          <button
            @click="openDetail(item)"
            class="text-blue-600 hover:text-blue-800 underline"
          >
            ดูรายละเอียด
          </button>

          <button
            v-if="item.status === 'pending'"
            @click="cancelAppointment(item.id)"
            class="text-red-600 hover:text-red-800 underline"
          >
            ยกเลิกนัดหมาย
          </button>

        </div>
      </div>

    </div>

    <!-- Popup Modal -->
    <AppointmentDetailModal
      v-if="modalOpen"
      :appointment="selected"
      @close="modalOpen = false"
    />

  </div>
</template>
