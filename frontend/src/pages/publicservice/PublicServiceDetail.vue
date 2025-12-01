<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();

const service = ref(null);
const loading = ref(true);

const token = localStorage.getItem("access");
const role = localStorage.getItem("role");

onMounted(async () => {
  try {
    const res = await axios.get(`http://localhost:8000/api/services/${route.params.id}/`);
    service.value = res.data;
  } catch (err) {
    console.error("ไม่พบข้อมูลบริการ", err);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="max-w-3xl mx-auto p-6">
    <button
      @click="$router.back()"
      class="text-blue-600 mb-4 hover:underline"
    >
       กลับ
    </button>

    <div v-if="loading">กำลังโหลด...</div>

    <div v-else-if="service" class="bg-white p-6 shadow rounded-lg">
      <img
        v-if="service.image"
        :src="service.image"
        class="w-full h-60 object-cover rounded-lg mb-4"
      />

      <h1 class="text-3xl font-bold mb-2">{{ service.name }}</h1>
      <p class="text-gray-600 mb-4">{{ service.description }}</p>

      <p class="text-gray-700"><strong>สถานที่:</strong> {{ service.location }}</p>
      <p class="text-gray-700">
        <strong>สถานะบริการ:</strong> 
        <span class="text-blue-600">{{ service.status }}</span>
      </p>

      <!-- ผู้ใช้ที่มีบัญชี = รายงานปัญหา -->
      <router-link
        v-if="token && role === 'user'"
        to="/report/create"
        class="block mt-5 bg-red-500 text-white p-3 rounded text-center hover:bg-red-600"
      >
         รายงานปัญหาบริการนี้
      </router-link>

      <!-- Admin = ปุ่มแก้ไข -->
      <router-link
        v-if="role === 'admin'"
        :to="`/admin/services/${service.id}/edit`"
        class="block mt-5 bg-yellow-500 text-white p-3 rounded text-center hover:bg-yellow-600"
      >
         แก้ไขบริการนี้
      </router-link>
    </div>
  </div>
</template>
