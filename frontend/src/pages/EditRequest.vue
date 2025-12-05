<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const id = route.params.id;

const form = ref({
  request_type: "",
  detail: "",
  area: ""
});

const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const token = localStorage.getItem("access");

    // ✔ โหลดเฉพาะของ user ทั้งหมด
    const res = await axios.get(
      "http://localhost:8000/api/reports/help/my/",
      { headers: { Authorization: `Bearer ${token}` } }
    );

    // ✔ หา record ที่ต้องการแก้ไข
    const item = res.data.find(r => r.id == id);

    if (!item) {
      error.value = "ไม่พบข้อมูลคำขอ";
      return;
    }

    // ✔ ตั้งค่า form
    form.value = {
      request_type: item.request_type,
      detail: item.detail,
      area: item.area
    };

  } catch (err) {
    console.error(err);
    error.value = "โหลดข้อมูลไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
});

const updateRequest = async () => {
  const token = localStorage.getItem("access");

  try {
    // ✔ URL ที่ถูกต้อง
    await axios.patch(
      `http://localhost:8000/api/reports/help/my/${id}/update/`,
      form.value,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    alert("แก้ไขคำขอสำเร็จ");
    router.push("/my-history");

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

    <form v-else @submit.prevent="updateRequest" class="space-y-3">

      <label>ประเภทคำขอ</label>
      <select v-model="form.request_type" class="w-full p-2 border rounded">
        <option value="เสียง">เสียง</option>
        <option value="ปิดทาง">ปิดทาง</option>
        <option value="ทั้งสองอย่าง">ทั้งสองอย่าง</option>
        <option value="อื่นๆ">อื่นๆ</option>
      </select>

      <label>รายละเอียด</label>
      <textarea v-model="form.detail" class="w-full p-2 border rounded"></textarea>

      <label>พื้นที่</label>
      <input v-model="form.area" class="w-full p-2 border rounded" />

      <button class="w-full bg-blue-600 text-white p-2 rounded mt-4">
        บันทึกการแก้ไข
      </button>
    </form>
  </div>
</template>
