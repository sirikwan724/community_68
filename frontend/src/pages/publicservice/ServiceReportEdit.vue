<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();

const id = route.params.id;

const loading = ref(true);
const saving = ref(false);
const error = ref("");

const serviceName = ref("");
const status = ref("");

const title = ref("");
const description = ref("");

// รูปเดิมจาก backend (url)
const currentImageUrl = ref(""); // เอาไว้แสดงรูปเก่า

// รูปใหม่ที่ผู้ใช้เลือก + preview
const imageFile = ref(null);
const newPreviewUrl = ref("");

const handleFileUpload = (e) => {
  const file = e.target.files?.[0] || null;
  imageFile.value = file;

  // สร้าง preview รูปใหม่
  if (newPreviewUrl.value) URL.revokeObjectURL(newPreviewUrl.value);
  newPreviewUrl.value = file ? URL.createObjectURL(file) : "";
};

onMounted(async () => {
  loading.value = true;
  error.value = "";

  try {
    const res = await api.get(`/services/reports/my/${id}/`);
    const data = res.data;

    status.value = data.status;
    serviceName.value = data.service_name || "";

    // ถ้าไม่ pending ห้ามแก้ (เหมือน ReportEdit)
    if (data.status !== "pending") {
      error.value = "รายงานนี้ถูกรับเรื่องแล้ว คุณไม่สามารถแก้ไขได้";
      return;
    }

    title.value = data.title || "";
    description.value = data.description || "";

    // รูปเดิม (ถ้ามี)
    // backend ของคุณส่ง image เป็น URL หรือ path ก็ได้
    // ถ้าเป็น path เช่น "/media/..." ให้แปะ baseURL เอง
    if (data.image) {
      // กรณี data.image เป็น full URL แล้ว
      if (String(data.image).startsWith("http")) {
        currentImageUrl.value = data.image;
      } else {
        // กรณีเป็น path เช่น "/media/.."
        currentImageUrl.value = `http://localhost:8000${data.image}`;
      }
    } else {
      currentImageUrl.value = "";
    }
  } catch (err) {
    console.error(err);
    error.value = err?.response?.data?.detail || "ไม่พบรายงานนี้";
  } finally {
    loading.value = false;
  }
});

const submitEdit = async () => {
  if (!title.value.trim() || !description.value.trim()) {
    alert("กรุณากรอกหัวข้อและรายละเอียดให้ครบ");
    return;
  }

  saving.value = true;

  try {
    const formData = new FormData();
    formData.append("title", title.value.trim());
    formData.append("description", description.value.trim());

    // ถ้าเลือกไฟล์ใหม่ ค่อยส่ง image
    // ถ้าไม่เลือก ไม่ส่ง -> รูปเดิมยังอยู่
    if (imageFile.value) formData.append("image", imageFile.value);

    await api.put(`/services/reports/my/${id}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    alert("แก้ไขรายงานตู้บริการสำเร็จ");
    router.push("/my-history");
  } catch (err) {
    console.error(err);
    alert(err?.response?.data?.detail || "เกิดข้อผิดพลาด ไม่สามารถแก้ไขได้");
  } finally {
    saving.value = false;
  }
};

const cancel = () => router.back();
</script>

<template>
  <div class="p-6 max-w-xl mx-auto bg-white rounded-lg shadow border">
    <h1 class="text-2xl font-bold mb-2">แก้ไขรายงานตู้บริการ</h1>

    <p v-if="serviceName" class="text-gray-600 mb-4">
      บริการ: <span class="font-semibold">{{ serviceName }}</span>
    </p>

    <div v-if="loading">กำลังโหลดข้อมูล...</div>
    <div v-else-if="error" class="text-red-600 font-medium">{{ error }}</div>

    <form v-else @submit.prevent="submitEdit" class="space-y-4">
      <!-- รูปเดิม -->
      <div v-if="currentImageUrl" class="border rounded-lg p-3">
        <p class="font-semibold mb-2 text-gray-700">รูปเดิมที่แนบไว้</p>
        <img
          :src="currentImageUrl"
          alt="current"
          class="w-full h-56 object-cover rounded"
        />
        <p class="text-xs text-gray-500 mt-2">
          * หากไม่อัปโหลดรูปใหม่ ระบบจะใช้รูปเดิม
        </p>
      </div>

      <!-- รูปใหม่ preview -->
      <div v-if="newPreviewUrl" class="border rounded-lg p-3">
        <p class="font-semibold mb-2 text-gray-700">ตัวอย่างรูปใหม่ (ก่อนบันทึก)</p>
        <img
          :src="newPreviewUrl"
          alt="preview"
          class="w-full h-56 object-cover rounded"
        />
      </div>

      <div>
        <label class="font-bold">หัวข้อปัญหา</label>
        <input v-model="title" class="w-full border p-2 rounded" />
      </div>

      <div>
        <label class="font-bold">รายละเอียด</label>
        <textarea v-model="description" rows="4" class="w-full border p-2 rounded" />
      </div>

      <div>
        <label class="font-bold">อัปโหลดภาพใหม่ (ถ้ามี)</label>
        <input type="file" accept="image/*" @change="handleFileUpload" />
        <button
          v-if="imageFile"
          type="button"
          @click="
            imageFile = null;
            if (newPreviewUrl) { URL.revokeObjectURL(newPreviewUrl); newPreviewUrl=''; }
          "
          class="mt-2 text-sm px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          เอารูปใหม่ออก
        </button>
      </div>

      <button
        :disabled="saving"
        class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        <span v-if="!saving">บันทึกการแก้ไข</span>
        <span v-else>กำลังบันทึก...</span>
      </button>

      <button
        type="button"
        @click="cancel"
        class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
      >
        ย้อนกลับ
      </button>
    </form>
  </div>
</template>
