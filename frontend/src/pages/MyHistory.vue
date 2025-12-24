<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const activeTab = ref("reports");
const router = useRouter();

const reports = ref([]);
const requests = ref([]);
const merged = ref([]);
const appointments = ref([]);
const borrows = ref([]);

const placeLabel = {
  temple: "วัด",
  village_hall: "ศาลากลางหมู่บ้าน",
  headman_office: "สำนักงานผู้ใหญ่บ้าน",
  learning_center: "ศูนย์เรียนรู้หมู่บ้าน"
};

const targetLabel = {
  headman: "ผู้ใหญ่บ้าน",
  assistant_headman: "ผู้ช่วยผู้ใหญ่บ้าน"
};

// ดึง Token แบบไม่ Error
const getToken = () => localStorage.getItem("access");
const token = getToken();

// ---------------------------
// Format วันที่
// ---------------------------
const formatDT = (dt) => {
  if (!dt) return "-";

  const d = new Date(dt);
  if (isNaN(d.getTime())) return "-";

  return d.toLocaleString("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};


// ---------------------------
// โหลดรายงานปัญหา (Report)
// ---------------------------
const loadReports = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/reports/my/", {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    reports.value = res.data.map((i) => ({
      id: i.id,
      type: "report",
      title: i.category,
      detail: i.description,
      status: i.status,
      created_at: i.created_at,
    }));
  } catch (err) {
    console.error("โหลดรายงานผิดพลาด", err);
  }
};

// ---------------------------
// โหลดคำขอความอนุเคราะห์
// ---------------------------
const loadRequests = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/reports/help/my/", {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    requests.value = res.data.map((i) => ({
      id: i.id,
      type: "request",
      title: i.request_type,
      detail: i.detail,
      status: i.status,
      created_at: i.created_at,
    }));
  } catch (err) {
    console.error("โหลดคำขอความอนุเคราะห์ผิดพลาด", err);
  }
};

// ---------------------------
// โหลดนัดหมาย
// ---------------------------
const loadAppointments = async () => {
  try {
    const res = await axios.get(
      "http://localhost:8000/api/appointments/my/",
      { headers: { Authorization: `Bearer ${token}` } }
    );
    appointments.value = res.data;
  } catch (err) {
    console.error("LOAD APPOINTMENTS ERROR:", err);
  }
};

// ---------------------------
// โหลดประวัติการยืม
// ---------------------------
const loadBorrows = async () => {
  try {
    const res = await axios.get(
      "http://localhost:8000/api/borrow/my/",
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );

    borrows.value = res.data.map((b) => ({
      id: b.id,
      type: "borrow",
      title: b.borrow_type === "ITEM" ? "ยืมสิ่งของ" : "ยืมสถานที่",
      detail:
        b.borrow_type === "ITEM"
          ? b.items
              .map(
                (i) => `${i.item_name} × ${i.quantity} ${i.unit}`
              )
              .join(", ")
          : b.location?.name || "-",
      status: b.status,
      created_at: b.created_at,
      raw: b, // เก็บ object เต็มไว้ใช้ต่อ
    }));
  } catch (err) {
    console.error("โหลดประวัติการยืมผิดพลาด", err);
  }
};

// ---------------------------
// แจ้งคืนการยืม
// ---------------------------
const requestReturn = async (id) => {
  if (!confirm("ยืนยันการแจ้งคืนหรือไม่?")) return;

  try {
    await axios.post(
      `http://localhost:8000/api/borrow/${id}/request-return/`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );

    alert("แจ้งคืนเรียบร้อย รอแอดมินตรวจสอบ");
    loadBorrows();
  } catch (err) {
    alert("ไม่สามารถแจ้งคืนได้");
  }
};

// ---------------------------
// รวมข้อมูลทั้งหมด
// ---------------------------
const mergeAll = () => {
  const formattedAppointments = appointments.value.map(ap => ({
    id: ap.id,
    type: "appointment",
    title: placeLabel[ap.meeting_place],  // แสดงชื่อสถานที่ (ภาษาไทย)
    detail: ap.reason,
    status: ap.status,
    created_at: ap.date
  }));

  merged.value = [
    ...reports.value,
    ...requests.value,
    ...formattedAppointments,
    ...borrows.value,
  ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
};

// ---------------------------
// ยกเลิกรายงาน
// ---------------------------
const cancelReport = async (id) => {
  if (!confirm("ต้องการยกเลิกคำร้องนี้หรือไม่?")) return;

  try {
    await axios.delete(`http://localhost:8000/api/reports/${id}/cancel/`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });

    alert("ยกเลิกคำร้องสำเร็จ");
    loadReports();
  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาด ไม่สามารถยกเลิกได้");
  }
};

// ---------------------------
// ยกเลิกคำขอความอนุเคราะห์
// ---------------------------
const cancelRequest = async (id) => {
  if (!confirm("ต้องการยกเลิกคำขอนี้หรือไม่?")) return;

  try {
    await axios.patch(
      `http://localhost:8000/api/reports/help/my/${id}/cancel/`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );

    alert("ยกเลิกคำขอเรียบร้อยแล้ว!");
    loadRequests();
  } catch (err) {
    console.error(err);
    alert("ไม่สามารถยกเลิกคำขอได้");
  }
};

// ---------------------------
// ยกเลิกนัดหมาย
// ---------------------------
const cancelAppointment = async (id) => {
  if (!confirm("ต้องการยกเลิกนัดหมายนี้หรือไม่?")) return;

  try {
    await axios.patch(
      `http://localhost:8000/api/appointments/${id}/cancel/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );

    alert("ยกเลิกสำเร็จ");
    loadAppointments();
  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาด");
  }
};

// ---------------------------
// โหลดข้อมูลเมื่อเปิดหน้า
// ---------------------------
onMounted(async () => {
  await loadReports();
  await loadRequests();
  await loadAppointments();
  await loadBorrows(); 
  mergeAll();
});
</script>

<template>
  <div class="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow">

    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-blue-600">
        ประวัติของฉัน
      </h2>
      <router-link
        to="/"
        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg shadow"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- Tabs -->
    <div class="flex gap-4 mb-6 border-b pb-2">
      <button
        @click="activeTab = 'reports'"
        :class="activeTab === 'reports'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        รายงานปัญหา
      </button>

      <button
        @click="activeTab = 'requests'"
        :class="activeTab === 'requests'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        ขอความอนุเคราะห์
      </button>

      <button
        @click="activeTab = 'appointments'"
        :class="activeTab === 'appointments'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        นัดหมาย
      </button>

      <button
        @click="activeTab = 'borrows'"
        :class="activeTab === 'borrows'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        การยืม
      </button>

      <button
        @click="activeTab = 'all'"
        :class="activeTab === 'all'
          ? 'border-b-4 border-blue-600 font-bold'
          : 'text-gray-500'"
        class="pb-2"
      >
        ทั้งหมด
      </button>
    </div>

    <!-- เนื้อหา -->

    <!-- ========================= -->
    <!--      รายงานปัญหา         -->
    <!-- ========================= -->
    <div v-if="activeTab === 'reports'">
      <div v-if="reports.length === 0" class="text-gray-500">
        ไม่มีประวัติรายงาน
      </div>

      <div
        v-for="item in reports"
        :key="item.id"
        class="border rounded-md p-4 mb-4"
      >
        <div class="flex justify-between">
          <h3 class="font-bold text-lg">{{ item.title }}</h3>

          <span
            class="px-2 py-1 rounded text-white text-sm"
            :class="{
              'bg-yellow-500': item.status === 'pending',
              'bg-blue-500': item.status === 'processing',
              'bg-green-600': item.status === 'resolved',
            }"
          >
            {{ item.status }}
          </span>
        </div>

        <p class="text-gray-600 mt-2">{{ item.detail }}</p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(item.created_at) }}
        </p>

        <!-- ปุ่มแก้ไข & ยกเลิก -->
        <div v-if="item.status === 'pending'" class="mt-4 flex gap-3">
          <button
            @click="$router.push(`/report/edit/${item.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            @click="cancelReport(item.id)"
            class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            ยกเลิกคำร้อง
          </button>
        </div>

      </div>
    </div>

    <!-- ========================= -->
    <!--   คำขอความอนุเคราะห์     -->
    <!-- ========================= -->
    <div v-if="activeTab === 'requests'">
      <div v-if="requests.length === 0" class="text-gray-500">
        ไม่มีประวัติคำขอความอนุเคราะห์
      </div>

      <div
        v-for="item in requests"
        :key="item.id"
        class="border rounded-md p-4 mb-4"
      >
        <div class="flex justify-between">
          <h3 class="font-bold text-lg">{{ item.title }}</h3>

          <span
            class="px-2 py-1 rounded text-white text-sm"
            :class="{
              'bg-yellow-500': item.status === 'pending',
              'bg-green-600': item.status === 'approved',
              'bg-red-600': item.status === 'rejected',
              'bg-purple-600': item.status === 'done',
            }"
          >
            {{ item.status }}
          </span>
        </div>

        <p class="text-gray-600 mt-2">{{ item.detail }}</p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(item.created_at) }}
        </p>

        <!-- ปุ่มแก้ไข & ยกเลิก -->
        <div v-if="item.status === 'pending'" class="mt-4 flex gap-3">
          <button
            @click="router.push(`/edit-request/${item.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            @click="cancelRequest(item.id)"
            class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            ยกเลิก
          </button>
        </div>
      </div>
    </div>

    <!-- ========================= -->
    <!--        นัดหมาย            -->
    <!-- ========================= -->
    <div v-if="activeTab === 'appointments'">

      <div v-if="appointments.length === 0" class="text-gray-500">
        ไม่มีประวัตินัดหมาย
      </div>

      <div
        v-for="ap in appointments"
        :key="ap.id"
        class="border rounded-md p-4 mb-4"
      >

      <p class="font-bold text-lg">
          ต้องการพบ: {{ targetLabel[ap.meet_with] }}
      </p>

      <h3 class="text-gray-600 mt-2"> สถานที่: {{ placeLabel[ap.meeting_place] }}</h3>

        <p class="text-gray-600 mt-2">
          วันที่: {{ ap.date }} เวลา {{ ap.start_time }} - {{ ap.end_time }}
        </p>

        <p class="text-gray-600 mt-2">เหตุผล: {{ ap.reason }}</p>

        <!-- Status -->
        <span
          class="px-3 py-1 rounded-full text-xs font-bold"
          :class="{
            'bg-yellow-200 text-yellow-800': ap.status === 'pending',
            'bg-green-200 text-green-800': ap.status === 'approved',
            'bg-red-200 text-red-800': ap.status === 'rejected',
          }"
        >
          {{ ap.status }}
        </span>

        <!-- ปุ่มเฉพาะ pending -->
        <div v-if="['pending', 'rejected'].includes(ap.status)" class="mt-3 flex gap-3">
          <button
            @click="$router.push(`/appointments/edit/${ap.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            class="px-4 py-2 bg-red-600 text-white rounded"
            @click="cancelAppointment(ap.id)"
          >
            ยกเลิก
          </button>
        </div>
      </div>
    </div>

    <!-- ========================= -->
    <!--        การยืม             -->
    <!-- ========================= -->
    <div v-if="activeTab === 'borrows'">
      <div v-if="borrows.length === 0" class="text-gray-500">
        ไม่มีประวัติการยืม
      </div>

      <div
        v-for="item in borrows"
        :key="item.id"
        class="border rounded-md p-4 mb-4"
      >
        <div class="flex justify-between">
          <h3 class="font-bold text-lg">
            <span v-if="item.borrow_type === 'ITEM'">ยืมสิ่งของ</span>
            <span v-else>จองสถานที่</span>
          </h3>

          <span
            class="px-2 py-1 rounded text-white text-sm"
            :class="{
              'bg-yellow-500': item.status === 'pending',
              'bg-blue-500': item.status === 'approved',
              'bg-orange-500': item.status === 'return_requested',
              'bg-green-600': item.status === 'returned',
              'bg-red-600': item.status === 'rejected',
            }"
          >
            {{ item.status }}
          </span>
        </div>

        <div class="text-gray-700 mt-2">

          <!-- กรณียืมสิ่งของ -->
          <div v-if="item.borrow_type === 'ITEM'">
            <div
              v-for="(bi, idx) in item.items"
              :key="idx"
            >
              • {{ bi.item_name }} × {{ bi.quantity }} {{ bi.unit }}
            </div>
          </div>
        
          <!-- กรณีจองสถานที่ -->
          <div v-else>
            จองสถานที่: {{ item.location_name }}
          </div>
        
        </div>

        <p class="text-sm text-gray-500 mt-2">
          ระยะเวลา:
          <span v-if="item.start_datetime && item.end_datetime">
            {{ formatDT(item.start_datetime) }} – {{ formatDT(item.end_datetime) }}
          </span>
          <span v-else>-</span>
        </p>


        <p class="text-sm text-gray-500">
          รับของ:
          <span v-if="item.pickup_datetime">
            {{ formatDT(item.pickup_datetime) }}
          </span>
          <span v-else>-</span>
        </p>

        <p class="text-sm text-gray-500">
          คืนของ:
          <span v-if="item.expected_return_datetime">
            {{ formatDT(item.expected_return_datetime) }}
          </span>
          <span v-else>-</span>
        </p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(item.created_at) }}
        </p>

        <div v-if="item.status === 'pending'" class="mt-4 flex gap-3">
          <button
            @click="cancelBorrow(item.id)"
            class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            ยกเลิกคำขอ
          </button>
        </div>

        <!-- ปุ่มแจ้งคืน -->
        <div v-if="item.status === 'approved'" class="mt-4">
          <button
            @click="requestReturn(item.id)"
            class="px-4 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600"
          >
            แจ้งคืน
          </button>
        </div>
      </div>
    </div>


    <!-- ========================= -->
    <!--        ทั้งหมด           -->
    <!-- ========================= -->
    <div v-if="activeTab === 'all'">
      <div v-if="merged.length === 0" class="text-gray-500">
        ยังไม่มีประวัติ
      </div>

      <div
        v-for="item in merged"
        :key="item.id"
        class="border rounded-md p-4 mb-4"
      >
        <div class="flex justify-between">

          <h3 class="font-bold text-lg">
            <span v-if="item.type === 'report'">รายงานปัญหา: </span>
            <span v-else-if="item.type === 'request'">ขอความอนุเคราะห์: </span>
            <span v-else-if="item.type === 'appointment'">นัดหมาย: </span>

            {{ item.title }}
          </h3>

          <span
            class="px-2 py-1 rounded text-white text-sm"
            :class="{
              'bg-yellow-500': item.status === 'pending',
              'bg-blue-500': item.status === 'processing',
              'bg-green-600': item.status === 'resolved',
              'bg-green-700': item.status === 'approved',
              'bg-red-600': item.status === 'rejected',
              'bg-purple-600': item.status === 'done',
            }"
          >
            {{ item.status }}
          </span>

        </div>

        <p class="text-gray-600 mt-2">{{ item.detail }}</p>

        <p v-if="item.type === 'appointment'" class="text-gray-600 mt-1">
          วันที่นัด: {{ item.created_at }}
        </p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(item.created_at) }}
        </p>

      </div>
    </div>

  </div>
</template>
