<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();

const serviceId = route.params.serviceId;

const loading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const title = ref("");
const description = ref("");
const imageFile = ref(null);

const handleFileUpload = (e) => {
  imageFile.value = e.target.files?.[0] || null;
};

const submitForm = async () => {
  if (!title.value.trim() || !description.value.trim()) {
    errorMessage.value = "กรุณากรอกหัวข้อและรายละเอียดให้ครบ";
    return;
  }

  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    const formData = new FormData();
    formData.append("service", serviceId);
    formData.append("title", title.value.trim());
    formData.append("description", description.value.trim());
    if (imageFile.value) formData.append("image", imageFile.value);

    // ✅ backend ของคุณอยู่ที่ /api/services/reports/create/
    await api.post("/services/reports/create/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    successMessage.value = "ส่งรายงานปัญหาตู้บริการเรียบร้อยแล้ว!";
    setTimeout(() => router.push(`/public-services/${serviceId}`), 1000);
  } catch (err) {
    console.error(err);
    const msg =
      err?.response?.data?.detail ||
      "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง";
    errorMessage.value = msg;
  } finally {
    loading.value = false;
  }
};

const cancel = () => router.back();
</script>

<template>
  <div class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md border">
    <h2 class="text-2xl font-bold mb-4 text-blue-600">
      รายงานปัญหาบริการสาธารณะ
    </h2>

    <div
      v-if="successMessage"
      class="p-3 bg-green-100 border border-green-300 text-green-700 rounded mb-4"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage"
      class="p-3 bg-red-100 border border-red-300 text-red-700 rounded mb-4"
    >
      {{ errorMessage }}
    </div>

    <form @submit.prevent="submitForm" class="space-y-4">
      <div>
        <label class="font-medium text-gray-700">หัวข้อปัญหา *</label>
        <input
          v-model="title"
          required
          class="w-full p-2 border rounded-md"
          placeholder="เช่น หยอดเหรียญไม่เข้า / น้ำไม่ไหล"
        />
      </div>

      <div>
        <label class="font-medium text-gray-700">รายละเอียด *</label>
        <textarea
          v-model="description"
          required
          rows="4"
          class="w-full p-2 border rounded-md"
          placeholder="อธิบายอาการ/ปัญหาที่พบ..."
        />
      </div>

      <div>
        <label class="font-medium text-gray-700">แนบรูป (ไม่บังคับ)</label>
        <input
          type="file"
          accept="image/*"
          @change="handleFileUpload"
          class="w-full p-2 border rounded-md"
        />
      </div>

      <button
        :disabled="loading"
        class="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
      >
        <span v-if="!loading">ส่งรายงาน</span>
        <span v-else>กำลังส่ง...</span>
      </button>

      <button
        type="button"
        @click="cancel"
        class="w-full bg-gray-200 text-gray-700 p-3 rounded-lg hover:bg-gray-300 transition"
      >
        ย้อนกลับ
      </button>
    </form>
  </div>
</template>
