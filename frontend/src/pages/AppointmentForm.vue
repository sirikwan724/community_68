<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();

const token = localStorage.getItem("access");

// -------------------------------
// ฟอร์มหลัก
// -------------------------------
const form = ref({
  target: "",
  date: "",
  start_time: "",
  end_time: "",
  reason: "",
  place: "",
});

// -------------------------------
// Dropdown options
// -------------------------------
const targetOptions = [
  { value: "headman", text: "ผู้ใหญ่บ้าน" },
  { value: "assistant_headman", text: "ผู้ช่วยผู้ใหญ่บ้าน" },
];

const placeOptions = [
  { value: "temple", text: "วัด" },
  { value: "village_hall", text: "ศาลากลางหมู่บ้าน" },
  { value: "headman_office", text: "สถานที่ทำการผู้ใหญ่บ้าน" },
  { value: "learning_center", text: "ศูนย์ให้ความรู้หมู่บ้าน" },
];

// -------------------------------
// ส่งข้อมูลไป Backend (ถูกต้อง)
// -------------------------------
const submitForm = async () => {
  try {
    const payload = {
      meet_with: form.value.target,
      meeting_place: form.value.place,
      date: form.value.date,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      reason: form.value.reason,
    };

    await axios.post("http://localhost:8000/api/appointments/create/", payload, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    alert("สร้างนัดหมายสำเร็จ");
    router.push("/my-history");

  } catch (err) {
    console.error("ERROR RESPONSE:", err.response?.data || err);
    alert("เกิดข้อผิดพลาด ไม่สามารถบันทึกนัดหมายได้");
  }
};

// -------------------------------
// ยกเลิก
// -------------------------------
const cancelForm = () => {
  if (confirm("ยืนยันยกเลิกแบบฟอร์มหรือไม่")) {
    router.push("/");
  }
};
</script>

<template>
  <div class="max-w-2xl mx-auto p-6 bg-white shadow rounded-lg">

    <h2 class="text-2xl font-bold mb-6">แบบฟอร์มนัดหมาย</h2>

    <!-- ผู้ที่ต้องการนัดหมาย -->
    <label class="font-semibold">ผู้ที่ต้องการนัดหมาย</label>
    <select v-model="form.target" class="w-full p-2 border rounded mt-1 mb-4">
      <option disabled value="">-- เลือกบุคคลที่ต้องการนัดหมาย --</option>
      <option v-for="t in targetOptions" :key="t.value" :value="t.value">
        {{ t.text }}
      </option>
    </select>

    <!-- วันที่ต้องการนัด -->
    <label class="font-semibold">วันที่ต้องการนัด</label>
    <input type="date" v-model="form.date" class="w-full p-2 border rounded mt-1 mb-4" />

    <!-- เวลาเริ่มต้น -->
    <label class="font-semibold">เวลาเริ่มต้น</label>
    <input type="time" v-model="form.start_time" class="w-full p-2 border rounded mt-1 mb-4" />

    <!-- เวลาสิ้นสุด -->
    <label class="font-semibold">เวลาสิ้นสุด</label>
    <input type="time" v-model="form.end_time" class="w-full p-2 border rounded mt-1 mb-4" />

    <!-- เหตุผล -->
    <label class="font-semibold">เหตุผลในการนัดหมาย</label>
    <textarea
      v-model="form.reason"
      rows="3"
      class="w-full p-2 border rounded mt-1 mb-4"
      placeholder="กรุณากรอกรายละเอียดเหตุผล"
    ></textarea>

    <!-- สถานที่ -->
    <label class="font-semibold">สถานที่</label>
    <select v-model="form.place" class="w-full p-2 border rounded mt-1 mb-6">
      <option disabled value="">-- เลือกสถานที่ --</option>
      <option v-for="p in placeOptions" :key="p.value" :value="p.value">
        {{ p.text }}
      </option>
    </select>

    <!-- ปุ่ม -->
    <div class="flex gap-3 mt-6">
      <button
        @click="submitForm"
        class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        ยืนยันการนัดหมาย
      </button>

      <button
        @click="cancelForm"
        class="w-full bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400"
      >
        ยกเลิก
      </button>
    </div>

  </div>
</template>
