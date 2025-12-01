<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();

const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

// ฟิลด์ฟอร์ม
const category = ref("");
const description = ref("");
const area = ref("");
const imageFile = ref(null);


// หมวดหมู่ปัญหา
const categories = [
  "ไฟฟ้า",
  "น้ำ",
  "ถนน",
  "บุคคล",
  "เสียง",
  "กลิ่น",
  "อื่นๆ",
];

const handleFileUpload = (e) => {
  imageFile.value = e.target.files[0];
};

const submitForm = async () => {
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  const token = localStorage.getItem("access");

  try {
    const formData = new FormData();

    formData.append("category", category.value);
    formData.append("description", description.value);
    formData.append("area", area.value);

    if (imageFile.value) {
      formData.append("image", imageFile.value);
    }

    await axios.post(
      "http://localhost:8000/api/reports/create/",
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      }
    );

    successMessage.value =
      "ส่งคำร้องเรียบร้อยแล้ว! แอดมินจะตรวจสอบโดยเร็วที่สุด";

    setTimeout(() => {
      router.push("/");
    }, 1500);
  } catch (error) {
    console.error(error);
    errorMessage.value =
      "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div
    class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md border border-gray-200"
  >
    <h2 class="text-2xl font-bold mb-4 text-blue-600">
      ส่งคำร้อง / รายงานปัญหา
    </h2>

    <!-- Success -->
    <div
      v-if="successMessage"
      class="p-3 bg-green-100 border border-green-400 text-green-700 rounded mb-4"
    >
      {{ successMessage }}
    </div>

    <!-- Error -->
    <div
      v-if="errorMessage"
      class="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4"
    >
      {{ errorMessage }}
    </div>

    <form @submit.prevent="submitForm" class="space-y-4">

      <!-- หมวดหมู่ -->
      <div>
        <label class="font-medium text-gray-700">หัวข้อปัญหา *</label>
        <select
          v-model="category"
          required
          class="w-full p-2 border rounded-md"
        >
          <option value="" disabled>-- เลือกหัวข้อปัญหา --</option>
          <option
            v-for="c in categories"
            :key="c"
            :value="c"
          >
            {{ c }}
          </option>
        </select>
      </div>

      <!-- รายละเอียด -->
      <div>
        <label class="font-medium text-gray-700">รายละเอียด *</label>
        <textarea
          v-model="description"
          required
          rows="4"
          placeholder="อธิบายรายละเอียดปัญหา..."
          class="w-full p-2 border rounded-md"
        ></textarea>
      </div>

      <!-- พื้นที่ -->
      <div>
        <label class="font-medium text-gray-700">บริเวณที่พบ *</label>
        <input
          v-model="area"
          required
          type="text"
          placeholder="เช่น หน้าบ้านเลขที่ 15 หมู่ 3"
          class="w-full p-2 border rounded-md"
        />
      </div>

      <!-- รูป -->
      <div>
        <label class="font-medium text-gray-700"
          >แนบรูปภาพ (ไม่บังคับ)</label
        >
        <input
          type="file"
          accept="image/*"
          @change="handleFileUpload"
          class="w-full p-2 border rounded-md"
        />
      </div>

      <!-- ปุ่ม -->
      <button
        :disabled="loading"
        class="w-full bg-blue-600 text-white p-3 rounded-lg shadow hover:bg-blue-700 transition disabled:opacity-50"
      >
        <span v-if="!loading">ส่งคำร้อง</span>
        <span v-else>กำลังส่ง...</span>
      </button>
      <button
        type="button"
        @click="router.push('/')"
        class="w-full mt-3 bg-gray-200 text-gray-700 p-3 rounded-lg shadow hover:bg-gray-300 transition"
      >
        กลับหน้าหลัก
      </button>
    </form>
  </div>
</template>
