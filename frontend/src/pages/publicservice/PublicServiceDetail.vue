<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();

const service = ref(null);
const loading = ref(true);

const token = localStorage.getItem("access");
const role = localStorage.getItem("role");

const serviceStatusText = computed(() => {
  if (!service.value) return "-";
  return serviceStatusLabel[service.value.status] || service.value.status;
});

const serviceStatusLabel = {
  normal: "พร้อมให้บริการ",
  maintenance: "อยู่ระหว่างซ่อมบำรุง",
  broken: "งดให้บริการ",
};

const serviceStatusClass = computed(() => {
  if (!service.value) return "";

  return {
    normal: "text-green-600",
    maintenance: "text-yellow-600",
    broken: "text-red-600",
  }[service.value.status];
});

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
        <span class="px-3 py-1 rounded-full text-s font-bold" :class="serviceStatusClass">{{ serviceStatusText }}</span>
      </p>

      <!-- ผู้ใช้ที่มีบัญชี = รายงานปัญหา -->
      <div class="flex items-center gap-3 mt-6">
        <router-link
          v-if="token && role === 'user'"
          :to="`/service-reports/create/${service.id}`"
          class="inline-block px-5 py-2 bg-brand-darkBlue text-white rounded-lg shadow hover:bg-blue-900 transition"
        >
           รายงานปัญหาบริการนี้
        </router-link>
        <router-link
        v-if="token && role === 'user'"
          to="/public-services"
          class="inline-block px-5 py-2 bg-brand-darkBlue text-white rounded-lg shadow hover:bg-blue-900 transition"
        >
           กลับไปหน้าหลัก
        </router-link>
      </div>

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
