<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const id = route.params.id;

const request_type = ref("");
const custom_type = ref("");
const start_date = ref("");
const start_time = ref("");
const end_date = ref("");
const end_time = ref("");
const detail = ref("");
const area = ref("");
const currentFile = ref("");   // URL ไฟล์เดิม
const newFile = ref(null);     // ไฟล์ใหม่ที่อัปโหลด
const previewUrl = ref(""); 
const loading = ref(true);
const error = ref("");

const FIXED_TYPES = ["เสียง", "ปิดทาง", "ทั้งสองอย่าง", "อื่นๆ"];

const toDateStr = (iso) => iso ? iso.substring(0, 10) : "";
const toTimeStr = (iso) => iso ? iso.substring(11, 16) : "";

onMounted(async () => {
  try {
    const token = localStorage.getItem("access");
    const res = await axios.get(
      "http://localhost:8000/api/reports/help/my/",
      { headers: { Authorization: `Bearer ${token}` } }
    );

    const item = res.data.find(r => r.id == id);
    if (!item) { error.value = "ไม่พบข้อมูลคำขอ"; return; }

    // ตรวจว่า request_type เป็น choice หรือ custom
    if (FIXED_TYPES.includes(item.request_type)) {
      request_type.value = item.request_type;
    } else {
      request_type.value = "อื่นๆ";
      custom_type.value = item.request_type;
    }

    start_date.value = toDateStr(item.start_datetime);
    start_time.value = toTimeStr(item.start_datetime);
    end_date.value   = toDateStr(item.end_datetime);
    end_time.value   = toTimeStr(item.end_datetime);
    detail.value     = item.detail;
    area.value       = item.area;
    currentFile.value = item.file || "";

  } catch (err) {
    console.error(err);
    error.value = "โหลดข้อมูลไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
});

const handleFile = (e) => {
  newFile.value = e.target.files[0];
  if (newFile.value) {
    previewUrl.value = URL.createObjectURL(newFile.value);  
  }
};

const minDate = computed(() => {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split("T")[0];
});

const updateRequest = async () => {
  const token = localStorage.getItem("access");

  const finalType = request_type.value === "อื่นๆ" && custom_type.value.trim()
    ? custom_type.value.trim()
    : request_type.value;

  const formData = new FormData();
  formData.append("request_type", finalType);
  formData.append("start_datetime", `${start_date.value}T${start_time.value}`);
  formData.append("end_datetime", `${end_date.value}T${end_time.value}`);
  formData.append("detail", detail.value);
  formData.append("area", area.value);
  if (newFile.value) {
    formData.append("file", newFile.value);
  }

  try {
    await axios.patch(
      `http://localhost:8000/api/reports/help/my/${id}/update/`,
      formData,
      { headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" } }
    );
    alert("แก้ไขคำขอสำเร็จ");
    router.push("/my-history?tab=requests");
  } catch (e) {
    console.error(e);
    alert("ไม่สามารถแก้ไขได้");
  }
};
</script>

<template>
  <div class="p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-4">แก้ไขคำขอความอนุเคราะห์</h2>

    <div v-if="loading">กำลังโหลดข้อมูล...</div>
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <form v-else @submit.prevent="updateRequest" class="space-y-4">

      <!-- ประเภทคำขอ -->
      <div>
        <label class="block mb-1 font-medium">ประเภทคำขอ</label>
        <select v-model="request_type" class="w-full p-2 border rounded">
          <option value="เสียง">เสียง</option>
          <option value="ปิดทาง">ปิดทาง</option>
          <option value="ทั้งสองอย่าง">ทั้งสองอย่าง</option>
          <option value="อื่นๆ">อื่นๆ</option>
        </select>
      </div>

      <!-- กรอกหัวข้อกรณีอื่นๆ -->
      <div v-if="request_type === 'อื่นๆ'">
        <label class="block mb-1 font-medium">ระบุประเภทคำขอ</label>
        <input v-model="custom_type" type="text" class="w-full p-2 border rounded"
          placeholder="กรอกประเภทคำขอของคุณ..." />
      </div>

      <!-- วันเวลาเริ่ม -->
      <div>
        <label class="block mb-1 font-medium">วันเวลาเริ่ม</label>
        <div class="flex gap-2">
          <input type="date" v-model="start_date" :min="minDate" class="border p-2 rounded w-1/2" />
          <input type="time" v-model="start_time" class="border p-2 rounded w-1/2" />
        </div>
      </div>

      <!-- วันเวลาสิ้นสุด -->
      <div>
        <label class="block mb-1 font-medium">วันเวลาสิ้นสุด</label>
        <div class="flex gap-2">
          <input type="date" v-model="end_date" :min="minDate" class="border p-2 rounded w-1/2" />
          <input type="time" v-model="end_time" class="border p-2 rounded w-1/2" />
        </div>
      </div>

      <!-- รายละเอียด -->
      <div>
        <label class="block mb-1 font-medium">รายละเอียด</label>
        <textarea v-model="detail" rows="3" class="w-full p-2 border rounded"></textarea>
      </div>

      <!-- สถานที่ -->
      <div>
        <label class="block mb-1 font-medium">สถานที่</label>
        <input v-model="area" type="text" class="w-full p-2 border rounded" />
      </div>

      <!-- ไฟล์/รูปภาพ -->
      <div>
        <label class="block mb-1 font-medium">ไฟล์/รูปภาพประกอบ</label>
        <div v-if="previewUrl || currentFile" class="mb-2">
          <p class="text-sm text-gray-500 mb-1">
            {{ previewUrl ? 'รูปใหม่ที่เลือก:' : 'ไฟล์ปัจจุบัน:' }}
          </p>
          <img
            :src="previewUrl || `http://localhost:8000${currentFile}`"
            class="max-h-40 rounded border object-cover"
          />
        </div>
        <input type="file" @change="handleFile" class="w-full border p-2 rounded" />
        <p class="text-xs text-gray-400 mt-1">อัปโหลดใหม่เพื่อเปลี่ยนไฟล์เดิม</p>
      </div>

      <button type="submit"
        class="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
        บันทึกการแก้ไข
      </button>

      <button
        type="button"
        @click="router.push('/my-history?tab=requests')"
        class="w-full bg-gray-200 text-gray-700 p-2 rounded hover:bg-gray-300"
      >
        ยกเลิก / กลับ
      </button>

    </form>
  </div>
</template>