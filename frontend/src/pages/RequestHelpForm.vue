<script setup>
import { ref, computed } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();

const token = localStorage.getItem("access");

const request_type = ref("");
const custom_type = ref(""); 
const start_date = ref("");
const start_time = ref("");
const end_date = ref("");
const end_time = ref("");
const area = ref("");
const detail = ref("");
const file = ref(null);

const handleFile = (e) => {
  file.value = e.target.files[0];
};

const minDate = computed(() => {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split("T")[0];
});

const submitForm = async () => {
  try {
    const start_datetime = `${start_date.value}T${start_time.value}`;
    const end_datetime = `${end_date.value}T${end_time.value}`;

    const formData = new FormData();
    const finalType = request_type.value === "อื่นๆ" && custom_type.value.trim()
      ? custom_type.value.trim()
      : request_type.value;
    formData.append("request_type", finalType);
    formData.append("start_datetime", start_datetime);
    formData.append("end_datetime", end_datetime);
    formData.append("area", area.value);
    formData.append("detail", detail.value);
    if (file.value) {
      formData.append("file", file.value);
    }

    await axios.post(
      "http://localhost:8000/api/reports/help/create/",
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      }
    );

    alert("ส่งคำขอสำเร็จ");
    router.push("/my-history?tab=requests"); 

  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาด กรุณาลองใหม่");
  }
};
</script>

<template>
  <div class="max-w-3xl mx-auto p-6 bg-white shadow rounded">
    <h2 class="text-2xl font-bold mb-4">ขอความอนุเคราะห์</h2>

    <!-- ประเภทคำขอ -->
    <label>ประเภทคำขอ</label>
    <select v-model="request_type" class="w-full border p-2 rounded mb-4">
      <option value="">-- เลือกประเภท --</option>
      <option value="เสียง">เสียง</option>
      <option value="ปิดทาง">ปิดทาง</option>
      <option value="ทั้งสองอย่าง">ทั้งสองอย่าง</option>
      <option value="อื่นๆ">อื่นๆ</option>
    </select>

    <!-- ช่องกรอกหัวข้อกรณีเลือกอื่นๆ -->
    <div v-if="request_type === 'อื่นๆ'" class="mb-4">
      <label>ระบุประเภทคำขอ</label>
      <input
        type="text"
        v-model="custom_type"
        placeholder="กรอกประเภทคำขอของคุณ..."
        class="w-full border p-2 rounded mt-1"
      />
    </div>

    <!-- วันที่เริ่ม -->
    <label>วันเวลาเริ่ม</label>
    <div class="flex gap-2 mb-4">
      <input type="date" v-model="start_date" :min="minDate" class="border p-2 rounded w-1/2" />
      <input type="time" v-model="start_time" class="border p-2 rounded w-1/2" />
    </div>

    <!-- วันสิ้นสุด -->
    <label>วันเวลาสิ้นสุด</label>
    <div class="flex gap-2 mb-4">
      <input type="date" v-model="end_date" :min="minDate" class="border p-2 rounded w-1/2" />
      <input type="time" v-model="end_time" class="border p-2 rounded w-1/2" />
    </div>

    <!-- สถานที่ -->
    <label>สถานที่</label>
    <input type="text" v-model="area" class="w-full border p-2 rounded mb-4" />

    <!-- รายละเอียด -->
    <label>รายละเอียดเพิ่มเติม</label>
    <textarea v-model="detail" class="w-full border p-2 rounded mb-4"></textarea>

    <!-- ไฟล์ -->
    <label>แนบรูปภาพ</label>
    <input type="file" @change="handleFile" class="w-full border p-2 rounded mb-4" />

    <!-- ปุ่มส่งคำขอ -->
    <button
      @click="submitForm"
      class="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
    >
      ส่งคำขอ
    </button>
    <!-- ปุ่มยกเลิก -->
    <button
        @click="cancelForm"
        class="w-full bg-gray-200 text-gray-700 mt-4 py-3 rounded hover:bg-gray-300"
      >
        ยกเลิก
      </button>

    <!-- ปุ่มกลับหน้าหลัก -->
    <button
      @click="router.push('/')"
      class="w-full bg-gray-200 text-gray-700 mt-4 py-3 rounded hover:bg-gray-300"
    >
      กลับหน้าหลัก
    </button>
  </div>
</template>
