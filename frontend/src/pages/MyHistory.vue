<script setup>
// import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "@/services/api";

const activeTab = ref("reports");
const router = useRouter();
const route = useRoute();
const reports = ref([]);
const requests = ref([]);

const expandedRequestId = ref(null);
const toggleRequestDetail = (id) => {
  expandedRequestId.value = expandedRequestId.value === id ? null : id;
}

const merged = ref([]);
const appointments = ref([]);
const borrows = ref([]);

const serviceReports = ref([]); // สำหรับเก็บรายงานปัญหาบริการสาธารณะของผู้ใช้

const filterMonth = ref(""); // "01" - "12"
const filterYear = ref("");  // "2024", "2025"

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
  approved: "อนุมัติแล้ว",
  rejected: "ปฏิเสธ",
  canceled: "รายงานไม่ถูกต้อง",
  cancelled: "ยกเลิกแล้ว",
  resolved: "เสร็จสิ้น",
  done: "เสร็จสิ้น",
  return_requested: "แจ้งคืนแล้ว",
  returned: "คืนแล้ว",
};

const statusClass = {
  pending: "bg-yellow-200 text-yellow-800",
  processing: "bg-blue-200 text-blue-800",
  approved: "bg-green-200 text-green-800",
  rejected: "bg-red-200 text-red-800",
  canceled: "bg-gray-300 text-gray-800",
  cancelled: "bg-gray-300 text-gray-700",
  resolved: "bg-green-200 text-green-800",
  done: "bg-green-200 text-green-800",
  return_requested: "bg-orange-200 text-orange-800",
  returned: "bg-green-300 text-green-900",
};

const placeLabel = {
  temple: "วัด",
  village_hall: "ศาลากลางหมู่บ้าน",
  headman_office: "สำนักงานผู้ใหญ่บ้าน",
  learning_center: "ศูนย์เรียนรู้หมู่บ้าน"
};

const apptStatusLabel = {
  pending: "รอดำเนินการ",
  approved: "อนุมัติแล้ว",
  rejected: "ปฏิเสธนัดหมาย",
  canceled: "ยกเลิกโดยผู้ใช้",
  done: "ดำเนินการเสร็จสิ้น",
};

const targetLabel = {
  headman: "ผู้ใหญ่บ้าน",
  assistant_headman: "ผู้ช่วยผู้ใหญ่บ้าน"
};

// ดึง Token แบบไม่ Error
// const getToken = () => localStorage.getItem("access");
// const token = getToken();

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

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  const [year, month, day] = dateStr.split("-");
  const d = new Date(Number(year), Number(month) - 1, Number(day));
  return d.toLocaleDateString("th-TH", { dateStyle: "long" });
};

// ---------------------------
// โหลดรายงานปัญหา (Report)
// ---------------------------
const loadReports = async () => {
  try {
    const res = await api.get("/reports/my/");

    reports.value = res.data.map((i) => ({
      id: i.id,
      type: "report",
      title: i.category,
      detail: i.description,
      status: i.status,
      created_at: i.created_at,
      notes: i.notes || [],  
      showNotes: false,
    }));
  } catch (err) {
    console.error("โหลดรายงานผิดพลาด", err);
  }
};

// ---------------------------
// โหลดรายงานปัญหาบริการสาธารณะ (Service Report)
// ---------------------------
const loadServiceReports = async () => {
  try {
    const res = await api.get("/services/reports/my/");

    const categoryLabel = {
      water: "ตู้กดน้ำ",
      washer: "เครื่องซักผ้า",
      other: "บริการอื่นๆ",
    };

    serviceReports.value = res.data.map((i) => ({
      id: i.id,
      type: "service_report",
      title: `บริการสาธารณะ • ${categoryLabel[i.service_category] || "บริการ"} ${i.service_name || ""}`.trim(),
      detail: `${i.title} - ${i.description}`,
      status: i.status,
      created_at: i.created_at,
      service_id: i.service_id,
    }));

  } catch (err) {
    console.error("โหลดรายงานตู้บริการผิดพลาด", err);
  }
};

// รวมข้อมูลรายงานปัญหาทั้งหมด (Report + Service Report)
const refreshReportsTab = async () => {
  await loadReports();
  await loadServiceReports();
  reports.value = [...reports.value, ...serviceReports.value].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
};

// ---------------------------
// ยกเลิกรายงานปัญหาบริการสาธารณะ
// ---------------------------
const cancelServiceReport = async (id) => {
  if (!confirm("ต้องการยกเลิกคำร้องนี้หรือไม่?")) return;

  try {
    await api.patch(`/services/reports/my/${id}/cancel/`, {});
    alert("ยกเลิกคำร้องสำเร็จ");
    await refreshReportsTab(); 
  } catch (err) {
    alert("ไม่สามารถยกเลิกได้");
  }
};

// ---------------------------
// โหลดคำขอความอนุเคราะห์
// ---------------------------
const loadRequests = async () => {
  try {
    const res = await api.get("/reports/help/my/");

    requests.value = res.data.map((i) => ({
      id: i.id,
      type: "request",
      title: i.request_type,
      detail: i.detail,
      status: i.status,
      created_at: i.created_at,
      start_datetime: i.start_datetime,
      end_datetime: i.end_datetime,
      area: i.area,
      file: i.file,
      reject_reason: i.reject_reason,
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
    const res = await api.get("/appointments/my/");
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
    const res = await api.get("/borrow/my/");
    borrows.value = res.data;
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
    await api.post(`/borrow/${id}/request-return/`, {});
    alert("แจ้งคืนเรียบร้อย รอแอดมินตรวจสอบ");
    loadBorrows();
  } catch (err) {
    alert("ไม่สามารถแจ้งคืนได้");
  }
};

const cancelBorrow = async (id) => {
  if (!confirm("ต้องการยกเลิกคำขอนี้หรือไม่?")) return;
  try {
    await api.patch(`/borrow/my/${id}/cancel/`, {});
    alert("ยกเลิกคำขอเรียบร้อย");
    loadBorrows();
  } catch (err) {
    alert("ไม่สามารถยกเลิกได้");
  }
};

// ---------------------------
// รวมข้อมูลทั้งหมด
// ---------------------------
const mergeAll = () => {
  const formattedAppointments = appointments.value.map(ap => ({
    id: ap.id,
    type: "appointment",
    title: placeLabel[ap.meeting_place],
    detail: ap.reason,
    status: ap.status,
    created_at: ap.created_at,
  }));

  const formattedBorrows = borrows.value.map(b => ({
    id: b.id,
    type: "borrow",   
    title: b.borrow_type === "ITEM" ? "ยืมสิ่งของ" : "จองสถานที่",
    detail:
      b.borrow_type === "ITEM"
        ? b.items
            .map(i => `${i.item_name} × ${i.quantity} ${i.unit}`)
            .join(", ")
        : `สถานที่: ${b.location_name}`,
    status: b.status,
    created_at: b.created_at,
  }));

  merged.value = [
    ...reports.value,
    ...requests.value,
    ...formattedAppointments,
    ...formattedBorrows,   
  ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
};

// ---------------------------
// ยกเลิกรายงาน
// ---------------------------
const cancelReport = async (id) => {
  if (!confirm("ต้องการยกเลิกคำร้องนี้หรือไม่?")) return;

  try {
    await api.patch(`/reports/${id}/cancel/`, {});
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
    await api.patch(`/reports/help/my/${id}/cancel/`, {});
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
    await api.patch(`/appointments/my/${id}/cancel/`, {});
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
  if (route.query.tab) {          
    activeTab.value = route.query.tab;
  }
  await loadReports(); // โหลดรายงานปัญหาทั่วไป
  await refreshReportsTab(); // โหลดรายงานปัญหาบริการสาธารณะของผู้ใช้
  await loadRequests(); // โหลดคำขอความอนุเคราะห์
  await loadAppointments(); // โหลดนัดหมาย
  await loadBorrows(); // โหลดประวัติการยืม
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
        การยืม/จอง
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
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="statusClass[item.status]"
          >
            {{ statusLabel[item.status] }}
          </span>
        </div>

        <p class="text-gray-600 mt-2">{{ item.detail }}</p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(item.created_at) }}
        </p>
        <div v-if="item.notes && item.notes.length > 0" class="mt-3">
          <button
            @click="item.showNotes = !item.showNotes"
            class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            {{ item.showNotes ? 'ซ่อนอัปเดต' : `ดูอัปเดตจากแอดมิน (${item.notes.length})` }}
          </button>

          <div v-if="item.showNotes" class="mt-3 space-y-2">
            <div
              v-for="note in item.notes"
              :key="note.id"
              class="p-3 bg-blue-50 border border-blue-200 rounded text-sm"
            >
              <p class="text-gray-800">{{ note.text }}</p>
              <p class="text-xs text-gray-400 mt-1">
                {{ new Date(note.created_at).toLocaleString('th-TH') }}
              </p>
            </div>
          </div>
        </div>

        <!-- ปุ่มแก้ไข & ยกเลิก -->
        <div v-if="item.status === 'pending'" class="mt-4 flex gap-3">
          <!-- รายงานหมู่บ้าน -->
          <button
            v-if="item.type === 'report'"
            @click="$router.push(`/report/edit/${item.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            v-if="item.type === 'report'"
            @click="cancelReport(item.id)"
            class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            ยกเลิกคำร้อง
          </button>

          <!-- รายงานตู้บริการ -->
          <button
            v-else-if="item.type === 'service_report'"
            @click="$router.push(`/service-reports/edit/${item.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            v-if="item.type === 'service_report'"
            @click="cancelServiceReport(item.id)"
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
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="statusClass[item.status]"
          >
            {{ statusLabel[item.status] }}
          </span>
        </div>

        <p class="text-gray-600 mt-2">{{ item.detail }}</p>
        <p class="text-sm text-gray-400 mt-1">ส่งเมื่อ: {{ formatDT(item.created_at) }}</p>

        <!-- ปุ่มดูรายละเอียด -->
        <button
          @click="toggleRequestDetail(item.id)"
          class="mt-3 text-sm text-blue-600 hover:underline"
        >
          {{ expandedRequestId === item.id ? 'ซ่อนรายละเอียด' : 'ดูรายละเอียด' }}
        </button>

        <!-- รายละเอียดแบบขยาย -->
        <div v-if="expandedRequestId === item.id" class="mt-3 bg-gray-50 border rounded p-3 space-y-1 text-sm">
          <p><strong>วันเวลาเริ่ม:</strong> {{ formatDT(item.start_datetime) }}</p>
          <p><strong>วันเวลาสิ้นสุด:</strong> {{ formatDT(item.end_datetime) }}</p>
          <p><strong>สถานที่:</strong> {{ item.area }}</p>
          <div v-if="item.file" class="mt-2">
            <p class="font-semibold mb-1">ไฟล์ประกอบ:</p>
            <img :src="`http://localhost:8000${item.file}`" class="max-h-48 rounded border object-cover" />
          </div>
          <div v-if="item.status === 'rejected' && item.reject_reason"
            class="mt-2 p-2 bg-red-50 border border-red-200 rounded">
            <p class="text-red-700 font-semibold">เหตุผลการปฏิเสธ:</p>
            <p class="text-red-600">{{ item.reject_reason }}</p>
          </div>
        </div>

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
        <div class="flex justify-between">
          <h3 class="font-bold text-lg">ต้องการพบ: {{ targetLabel[ap.meet_with] }}</h3>

          <span
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="statusClass[ap.status]"
          >
            {{ apptStatusLabel[ap.status] }}
          </span>
        </div>

        <p class="text-gray-600 mt-2">สถานที่: {{ placeLabel[ap.meeting_place] }}</p>

        <p class="text-gray-600 mt-1">
          วันที่: {{ formatDate(ap.date) }} เวลา {{ ap.start_time?.slice(0,5) }} - {{ ap.end_time?.slice(0,5) }}
        </p>

        <p class="text-gray-600 mt-1">เหตุผล: {{ ap.reason }}</p>

        <p class="text-sm text-gray-400 mt-1">
          ส่งเมื่อ: {{ formatDT(ap.created_at) }}
        </p>

        <div
          v-if="ap.status === 'rejected' && ap.admin_note"
          class="mt-2 p-3 bg-red-50 border border-red-200 rounded text-sm"
        >
          <p class="text-red-700">
            <strong>เหตุผลที่ถูกปฏิเสธ:</strong> {{ ap.admin_note }}
          </p>
        </div>

        <!-- ปุ่มเฉพาะ pending -->
        <div v-if="ap.status === 'pending'" class="mt-4 flex gap-3">
          <button
            @click="$router.push(`/appointments/edit/${ap.id}`)"
            class="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            แก้ไข
          </button>

          <button
            @click="cancelAppointment(ap.id)"
            class="px-4 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            ยกเลิก
          </button>
        </div>
      </div>
    </div>

    <!-- ========================= -->
    <!--        การยืม/จอง             -->
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
            :class="statusClass[item.status]"
          >
            {{ statusLabel[item.status] }}
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

        <!-- แสดงเหตุผลปฏิเสธ -->
        <div
          v-if="item.status === 'rejected' && item.admin_note"
          class="mt-2 p-3 bg-red-50 border border-red-200 rounded text-sm"
        >
          <p class="text-red-700">
            <strong>เหตุผลที่ถูกปฏิเสธ:</strong> {{ item.admin_note }}
          </p>
        </div>

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
            <span v-else-if="item.type === 'borrow'">การยืม/จอง: </span>

            {{ item.title }}
          </h3>

          <span
            class="px-3 py-1 rounded-full text-xs font-bold"
            :class="statusClass[item.status]"
          >
            {{ statusLabel[item.status] }}
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
