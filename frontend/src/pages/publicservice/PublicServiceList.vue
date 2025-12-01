<template>
  <div class="container mx-auto p-6">

    <!-- ปุ่มกลับ -->
    <div class="mb-4">
      <router-link
        to="/"
        class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
      >
         กลับหน้าหลัก
      </router-link>
    </div>

    <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
       บริการสาธารณะของหมู่บ้าน
    </h2>

    <div v-if="services.length === 0" class="text-gray-500 text-center mt-10">
      ยังไม่มีบริการสาธารณะ
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="item in services"
        :key="item.id"
        @click="goDetail(item.id)"
        class="bg-white border shadow-sm rounded-lg p-4 cursor-pointer hover:shadow-lg transition"
      >
        <img
          v-if="item.image"
          :src="item.image"
          class="w-full h-40 object-cover rounded"
        />

        <h3 class="font-semibold text-lg mt-2">{{ item.name }}</h3>
        <p class="text-sm text-gray-600">{{ item.location }}</p>

        <!-- สถานะ -->
        <span
          class="inline-block mt-2 px-2 py-1 text-xs rounded-full"
          :class="{
            'bg-green-100 text-green-700': item.status === 'normal',
            'bg-yellow-100 text-yellow-700': item.status === 'maintenance',
            'bg-red-100 text-red-700': item.status === 'broken'
          }"
        >
          {{
            item.status === 'normal'
              ? 'ใช้งานได้ปกติ'
              : item.status === 'maintenance'
              ? 'กำลังซ่อมบำรุง'
              : 'ชำรุด'
          }}
        </span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const services = ref([]);

onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/services/");
    services.value = res.data;
  } catch (err) {
    console.error("โหลดข้อมูลล้มเหลว", err);
  }
});

const goDetail = (id) => {
  router.push(`/public-services/${id}`);
};
</script>
