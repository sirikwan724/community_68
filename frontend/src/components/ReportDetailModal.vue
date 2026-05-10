<script setup>
import { ref, watch } from "vue";
import axios from "axios";

const props = defineProps({
  report: Object,   // ข้อมูลรายงานจากหน้า List
});

const emit = defineEmits(["close", "updated"]);
const getToken = () => localStorage.getItem("access");

const currentReport = ref(null);
const noteText = ref("");
const newStatus = ref("");
const showUserCard = ref(false);

const loadReportDetail = async () => {
  const res = await axios.get(
    `http://localhost:8000/api/reports/${props.report.id}/`,
    {
      headers: { Authorization: `Bearer ${getToken()}` },
    }
  );
  currentReport.value = res.data;

  const s = res.data.status;
  if (s === "pending") newStatus.value = "accepted";
  else if (s === "processing") newStatus.value = "processing";
  else if (s === "resolved") newStatus.value = "rollback";
  else newStatus.value = "";
};

// เมื่อ modal เปิด / report เปลี่ยน → โหลดใหม่
watch(
  () => props.report,
  () => {
    if (props.report?.id) {
      loadReportDetail();
    }
  },
  { immediate: true }
);

// ------------------------------
// ปิดหน้าต่าง Popup
// ------------------------------
const closeModal = () => {
  emit("close");
};

// ------------------------------
// เรียก API อัปเดตสถานะ + บันทึกโน้ต
// ------------------------------
const updateStatus = async () => {
  if (!newStatus.value) {
    alert("กรุณาเลือกสถานะใหม่");
    return;
  }

  if (!noteText.value) {
    alert("กรุณากรอกโน้ต");
    return;
  }

  let url = "";
  let method = "patch";
  let body = {};

  // รับเรื่อง -> เปลี่ยนเป็น processing
  if (newStatus.value === "accepted") {
    url = `http://localhost:8000/api/reports/${props.report.id}/accept/`;
    body = {};
  }

  // เพิ่มโน้ต (POST + message)
  else if (newStatus.value === "processing") {
    url = `http://localhost:8000/api/reports/${props.report.id}/add-note/`;
    method = "post";
    body = { message: noteText.value };
  }

  // สถานะเสร็จสิ้น
  else if (newStatus.value === "resolved") {
    url = `http://localhost:8000/api/reports/${props.report.id}/done/`;
    body = { message: noteText.value }; // ส่งโน้ตไปบันทึกพร้อมกับเปลี่ยนสถานะเสร็จสิ้นด้วย
  }

  // ย้อนกลับสถานะ
  else if (newStatus.value === "rollback") {
    url = `http://localhost:8000/api/reports/${props.report.id}/rollback/`;
    body = {};
  }

  try {
    await axios({
      method: method,
      url: url,
      data: body,
      headers: { Authorization: `Bearer ${getToken()}` }
    });

    alert("อัปเดตสำเร็จ");

    emit("updated");
    emit("close");

  } catch (err) {
    console.error("Update error:", err);
    alert("อัปเดตสถานะไม่สำเร็จ");
  }
};

const formatDateTimeTH = (datetime) => {
  if (!datetime) return "-";

  const date = new Date(datetime);

  const datePart = date.toLocaleDateString("th-TH", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const timePart = date.toLocaleTimeString("th-TH", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return `${datePart} เวลา ${timePart} น.`;
};

</script>

<template>
  <div v-if="currentReport" class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
    <div class="bg-white p-6 w-full max-w-xl rounded shadow-lg relative max-h-[90vh] overflow-y-auto">

      <!-- ปุ่มปิด -->
      <button class="absolute top-2 right-2 text-gray-600 text-xl" @click="closeModal">✕</button>

      <h2 class="text-xl font-bold mb-4">รายละเอียดรายงาน</h2>

      <!-- รายละเอียด -->
      <div v-if="currentReport" class="space-y-2">
        <p><strong>หัวข้อ:</strong> {{ currentReport.category }}</p>
        <p>
          <strong>ผู้แจ้ง:</strong>
          <span
            @click="showUserCard = !showUserCard"
            class="text-blue-600 underline cursor-pointer ml-1"
          >
            {{ currentReport.user_data.full_name }}
          </span>
        </p>
        <div
          v-if="showUserCard"
          class="mt-2 p-4 bg-blue-50 border border-blue-200 rounded"
        >
          <p class="font-semibold text-blue-800 mb-2">ข้อมูลผู้แจ้ง</p>
          <p><strong>ชื่อ-นามสกุล:</strong> {{ currentReport.user_data.full_name }}</p>
          <p><strong>เบอร์โทร:</strong> {{ currentReport.user_data.phone }}</p>
          <p><strong>ที่อยู่:</strong> {{ currentReport.user_data.address }}</p>
          <p><strong>เลขทะเบียนบ้าน:</strong> {{ currentReport.user_data.citizen_id }}</p>
          <p><strong>ชื่อเจ้าบ้าน:</strong> {{ currentReport.user_data.house_owner_name }}</p>
        </div>
        <p><strong>เบอร์โทร:</strong> {{ currentReport.user_data.phone }}</p>
        <p><strong>พื้นที่:</strong> {{ currentReport.area }}</p>
        <p><strong>รายละเอียด:</strong> {{ currentReport.description }}</p>
        <p><strong>วันที่แจ้ง:</strong> {{ formatDateTimeTH(currentReport.created_at) }}</p>

        <div v-if="report.image" class="mt-3">
          <img
            :src="`http://localhost:8000${report.image}`"
            class="w-full max-h-64 object-cover rounded border"
          />
        </div>
      </div>

      <!-- อัปเดตสถานะ -->
      <div class="mt-6">
        <label class="font-semibold">อัปเดตสถานะ</label>

        <select
          v-model="newStatus"
          class="w-full p-2 border rounded mt-2"
        >
          <option value="" disabled>-- เลือกการดำเนินการ --</option>
          <option
            value="accepted"
            v-if="currentReport.status === 'pending'"
          >
            รับเรื่อง
          </option>

          <option
            value="processing"
            v-if="currentReport.status === 'processing'"
          >
            เพิ่มบันทึก / ดำเนินการต่อ
          </option>

          <option
            value="resolved"
            v-if="currentReport.status === 'processing'"
          >
            ดำเนินการเสร็จสิ้น
          </option>

          <option
            value="rollback"
            v-if="currentReport.status === 'resolved'"
          >
            ย้อนกลับสถานะ
          </option>

        </select>
      </div>

      <!-- ประวัติโน้ต -->
      <div
        v-if="currentReport.notes && currentReport.notes.length"
        class="mt-6 border-t pt-4"
      >
        <h3 class="font-semibold mb-3">ประวัติการอัปเดต</h3>

        <ul class="space-y-3 max-h-48 overflow-y-auto">
          <li
            v-for="note in currentReport.notes"
            :key="note.id"
            class="p-3 bg-gray-100 rounded border"
          >
            <p>{{ note.text }}</p>
            <p class="text-xs text-gray-500">
              {{ new Date(note.created_at).toLocaleString("th-TH") }}
            </p>
          </li>
        </ul>
      </div>

      <!-- ช่องใส่โน้ตใหม่ -->
      <div class="mt-4">
        <label class="font-semibold">บันทึกโน้ตใหม่</label>
        <textarea
          v-model="noteText"
          rows="3"
          class="w-full p-2 border rounded mt-2"
          placeholder="รายละเอียดเพิ่มเติม เช่น การติดต่อช่าง การตรวจสอบสถานที่"
        ></textarea>
      </div>

      <!-- บันทึก -->
      <button
        @click="updateStatus"
        class="w-full bg-blue-600 text-white py-2 mt-4 rounded hover:bg-blue-700"
      >
        บันทึกการอัปเดต
      </button>
    </div>
  </div>
</template>