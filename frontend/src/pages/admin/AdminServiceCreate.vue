<template>
  <div class="p-6 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">เพิ่มบริการสาธารณะ</h1>
    
    <div class="space-y-4">
      <input v-model="name" class="input" placeholder="ชื่อบริการ" />

      <select v-model="category" class="input">
        <option value="">เลือกประเภท</option>
        <option value="water">ตู้กดน้ำ</option>
        <option value="washer">เครื่องซักผ้า</option>
        <option value="other">บริการอื่นๆ</option>
      </select>

      <input v-model="location" class="input" placeholder="ที่ตั้ง" />
      <textarea v-model="description" class="input" placeholder="รายละเอียด"></textarea>

      <input type="file" @change="uploadFile" />

      <button
        @click="save"
        class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
      >
        บันทึก
      </button>

      <button @click="router.push('/admin/services/')"
        class="px-4 py-2 bg-gray-300 rounded">
        กลับหน้าหลัก
      </button>

      
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const name = ref("");
const category = ref("");
const location = ref("");
const description = ref("");
const imageFile = ref(null);

const router = useRouter();

const uploadFile = (e) => {
  imageFile.value = e.target.files[0];
};

const save = async () => {
  const formData = new FormData();
  formData.append("name", name.value);
  formData.append("category", category.value);
  formData.append("location", location.value);
  formData.append("description", description.value);

  if (imageFile.value) {
    formData.append("image", imageFile.value);
  }

  await axios.post("http://localhost:8000/api/services/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  alert("เพิ่มบริการสำเร็จ");
  router.push("/admin/services");
};
</script>

<style>
.input {
  @apply w-full p-2 border rounded-lg;
}
</style>
