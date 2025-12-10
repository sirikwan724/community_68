<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const id = route.params.id;
const token = localStorage.getItem("access");

// ฟอร์มหลัก
const form = ref({
  meet_with: "",
  meeting_place: "",
  date: "",
  start_time: "",
  end_time: "",
  reason: "",
});

// ตัวเลือก dropdown
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

// โหลดข้อมูลนัดหมายเดิม
const loadAppointment = async () => {
  try {
    const res = await axios.get(
      `http://localhost:8000/api/appointments/my/${id}/`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    form.value = {
      meet_with: res.data.meet_with,
      meeting_place: res.data.meeting_place,
      date: res.data.date,
      start_time: res.data.start_time,
      end_time: res.data.end_time,
      reason: res.data.reason,
    };
  } catch (err) {
    console.error("LOAD ERROR:", err);
    alert("โหลดข้อมูลผิดพลาด");
  }
};

// อัปเดตข้อมูล
const updateAppointment = async () => {
  try {
    await axios.patch(
      `http://localhost:8000/api/appointments/${id}/update/`,
      form.value,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    alert("อัปเดตข้อมูลสำเร็จ");
    router.push("/my-history");
  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาดในการบันทึก");
  }
};

// ยกเลิกการแก้ไข
const cancelEdit = () => router.push("/my-history");

onMounted(loadAppointment);
</script>

<template>
  <div class="max-w-2xl mx-auto p-6 bg-white shadow rounded-lg">

    <h2 class="text-2xl font-bold mb-6">แก้ไขข้อมูลนัดหมาย</h2>

    <!-- ผู้ที่ต้องการนัดหมาย -->
    <label class="font-semibold">ผู้ที่ต้องการนัดหมาย</label>
    <select v-model="form.meet_with" class="w-full p-2 border rounded mt-1 mb-4">
      <option disabled value="">-- เลือกบุคคลที่ต้องการนัดหมาย --</option>
      <option v-for="t in targetOptions" :key="t.value" :value="t.value">
        {{ t.text }}
      </option>
    </select>

    <!-- สถานที่ -->
    <label class="font-semibold">สถานที่</label>
    <select v-model="form.meeting_place" class="w-full p-2 border rounded mt-1 mb-4">
      <option disabled value="">-- เลือกสถานที่ --</option>
      <option v-for="p in placeOptions" :key="p.value" :value="p.value">
        {{ p.text }}
      </option>
    </select>

    <!-- วันที่ -->
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
    ></textarea>

    <!-- ปุ่ม -->
    <div class="flex gap-3 mt-6">
      <button
        @click="updateAppointment"
        class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        บันทึกการแก้ไข
      </button>

      <button
        @click="cancelEdit"
        class="w-full bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400"
      >
        ยกเลิก
      </button>
    </div>

  </div>
</template>
