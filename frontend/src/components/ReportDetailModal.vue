<script setup>
import { ref } from "vue";
import axios from "axios";

const props = defineProps({
  report: Object,   // ข้อมูลรายงานจากหน้า List
});

const emit = defineEmits(["close", "updated"]);

const getToken = () => localStorage.getItem("access");

const noteText = ref("");
const newStatus = ref("");

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
    body = {};
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
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 w-full max-w-xl rounded shadow-lg relative">

      <!-- ปุ่มปิด -->
      <button class="absolute top-2 right-2 text-gray-600 text-xl" @click="closeModal">✕</button>

      <h2 class="text-xl font-bold mb-4">รายละเอียดรายงาน</h2>

      <!-- รายละเอียด -->
      <div class="space-y-2">
        <p><strong>หัวข้อ:</strong> {{ report.category }}</p>
        <p><strong>ผู้แจ้ง:</strong> {{ report.user_data.full_name }}</p>
        <p><strong>เบอร์โทร:</strong> {{ report.user_data.phone }}</p>
        <p><strong>พื้นที่:</strong> {{ report.area }}</p>
        <p><strong>รายละเอียด:</strong> {{ report.description }}</p>
        <p><strong>วันที่แจ้ง:</strong> {{ report.created_at }}</p>

        <div v-if="report.image" class="mt-3">
          <img
            :src="`http://localhost:8000${report.image}`"
            class="w-full max-h-64 object-cover rounded border"
          />
        </div>
      </div>

      <!-- ประวัติโน้ตเก่า -->
      <div v-if="report.notes && report.notes.length" class="mt-6">
        <h3 class="font-semibold mb-2">บันทึกโน้ตที่ผ่านมา</h3>

        <ul class="space-y-2">
          <li 
            v-for="note in report.notes" 
            :key="note.id"
            class="p-2 bg-gray-100 rounded border"
          >
            <p class="text-sm">{{ note.text }}</p>
            <p class="text-xs text-gray-500">{{ note.created_at }}</p>
          </li>
        </ul>
      </div>

      <!-- อัปเดตสถานะ -->
      <div class="mt-6">
        <label class="font-semibold">อัปเดตสถานะ</label>

        <select
          v-model="newStatus"
          class="w-full p-2 border rounded mt-2"
        >
          <option disabled value="">-- เลือกสถานะใหม่ --</option>
          <option value="accepted">รับเรื่อง</option>
          <option value="processing">กำลังดำเนินการ</option>
          <option value="resolved">ดำเนินการเสร็จสิ้น</option>
          <option value="rollback">ย้อนกลับสถานะ</option>
        </select>
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