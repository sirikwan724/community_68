<template>
  <div class="p-6 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">แก้ไขบริการสาธารณะ</h1>

    <!-- โหลดข้อมูลไม่ทัน -->
    <div v-if="loading" class="text-gray-500">กำลังโหลดข้อมูล...</div>

    <div v-else class="space-y-4">

      <!-- ชื่อ -->
      <input v-model="name" class="input" placeholder="ชื่อบริการ" />

      <!-- ประเภท -->
      <select v-model="category" class="input">
        <option value="water">ตู้กดน้ำ</option>
        <option value="washer">เครื่องซักผ้า</option>
        <option value="other">บริการอื่นๆ</option>
      </select>

      <!-- ที่ตั้ง -->
      <input v-model="location" class="input" placeholder="ที่ตั้ง" />

      <!-- รายละเอียด -->
      <textarea v-model="description" class="input" placeholder="รายละเอียดเพิ่มเติม"></textarea>

      <!-- สถานะ -->
      <select v-model="status" class="input">
        <option value="normal">✓ ใช้งานปกติ</option>
        <option value="maintenance">⚠ กำลังซ่อมบำรุง</option>
        <option value="broken">✗ ชำรุด</option>
      </select>

      <!-- รูปเดิม -->
      <div v-if="image" class="mt-4">
        <p class="text-gray-600">รูปภาพเดิม:</p>
        <img :src="image" class="w-full h-40 object-cover rounded" />
      </div>

      <!-- เปลี่ยนรูปใหม่ -->
      <input type="file" @change="uploadFile" />

      <!-- ปุ่มบันทึก -->
      <button
        @click="updateService"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
      >
        บันทึกการเปลี่ยนแปลง
      </button>

      <!-- ปุ่มกลับ -->
      <button @click="router.push('/admin/services/')"
        class="px-4 py-2 bg-gray-300 rounded">
      กลับหน้าหลัก
      </button>

    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const id = route.params.id;

const loading = ref(true);

const name = ref("");
const category = ref("");
const location = ref("");
const description = ref("");
const status = ref("");
const image = ref("");

const newImageFile = ref(null);

// โหลดรูปใหม่
const uploadFile = (e) => {
  newImageFile.value = e.target.files[0];
};

onMounted(async () => {
  try {
    const res = await axios.get(`http://localhost:8000/api/services/${id}/`);
    const data = res.data;

    name.value = data.name;
    category.value = data.category;
    location.value = data.location;
    description.value = data.description;
    status.value = data.status;
    image.value = data.image;

    loading.value = false;
  } catch (err) {
    console.error("Error loading service:", err);
    loading.value = false;
  }
});

const updateService = async () => {
  const formData = new FormData();
  formData.append("name", name.value);
  formData.append("category", category.value);
  formData.append("location", location.value);
  formData.append("description", description.value);
  formData.append("status", status.value);

  if (newImageFile.value) {
    formData.append("image", newImageFile.value);
  }

  try {
    await axios.put(`http://localhost:8000/api/services/${id}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    alert("อัปเดตข้อมูลสำเร็จ");
    router.push("/admin/services");
  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาด");
  }
};
</script>


<style>
.input {
  @apply w-full p-2 border rounded-lg;
}
</style>
