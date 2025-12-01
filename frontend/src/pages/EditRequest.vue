<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const form = ref({
  request_type: "",
  detail: "",
  area: "",
  start_datetime: "",
  end_datetime: "",
});

const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    const token = localStorage.getItem("access");
    const res = await axios.get(
      `http://localhost:8000/api/help/my/${route.params.id}/`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    form.value = res.data;
  } catch (err) {
    error.value = "โหลดข้อมูลไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
});

const updateRequest = async () => {
  const token = localStorage.getItem("access");

  try {
    await axios.patch(
      `http://localhost:8000/api/help/my/${route.params.id}/update/`,
      form.value,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    alert("แก้ไขคำขอสำเร็จ");
    router.push("/my-history");
  } catch (e) {
    alert("ไม่สามารถแก้ไขได้");
  }
};
</script>

<template>
  <div class="p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-4">แก้ไขคำขอความอนุเคราะห์</h2>

    <div v-if="loading">กำลังโหลดข้อมูล...</div>

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
