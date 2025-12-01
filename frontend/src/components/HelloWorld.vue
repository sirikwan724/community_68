<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import HeroSlider from "@/components/HeroSlider.vue";  // ⭐ เพิ่มตรงนี้

const router = useRouter();
const isLoggedIn = ref(false);
const user = ref({});
const newsList = ref([]);

onMounted(async () => {
  const token = localStorage.getItem("access");
  const userData = localStorage.getItem("user");

  if (token && userData) {
    isLoggedIn.value = true;
    try {
      user.value = JSON.parse(userData);
    } catch (e) {
      console.error("Parse error", e);
    }
  }

  try {
    const res = await axios.get("http://localhost:8000/api/accounts/news/");
    newsList.value = res.data;
  } catch (err) {
    console.error("ไม่สามารถดึงข่าวได้", err);
  }
});

const logout = () => {
  localStorage.clear();
  isLoggedIn.value = false;
  router.push("/login");
};
</script>

<template>
  <!-- ======================  ผู้เยี่ยมชม (ยังไม่ล็อกอิน)  ====================== -->
  <div v-if="!isLoggedIn" class="min-h-screen bg-gray-50 font-sans">

    <!-- Navbar -->
    <nav class="bg-white shadow-sm px-6 py-4 flex justify-between items-center sticky top-0 z-50">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🏡</span>
        <h1 class="text-xl font-bold text-brand-darkBlue">ชุมชนบ้านสร้างขุนศรี</h1>
      </div>
      <div class="flex gap-3">
        <router-link to="/register-request" class="px-4 py-2 text-sm font-semibold text-brand-darkBlue bg-yellow-100 hover:bg-yellow-200 rounded-lg transition">ลงทะเบียน</router-link>
        <router-link to="/login" class="px-4 py-2 text-sm font-semibold text-white bg-brand-darkBlue hover:bg-blue-900 rounded-lg transition">เข้าสู่ระบบ</router-link>
      </div>
    </nav>

    <!-- ⭐ Hero Slider -->
    <HeroSlider />

    <!-- Header Section -->
    <header class="bg-gradient-to-br from-brand-softYellow via-brand-cream to-white py-16 text-center px-4">
      <h1 class="text-4xl font-extrabold text-brand-darkBlue tracking-wide mb-4">ยินดีต้อนรับสู่หมู่บ้านของเรา</h1>
      <p class="text-gray-600 text-lg max-w-2xl mx-auto">
        ศูนย์กลางข้อมูลข่าวสาร และการติดต่อผู้นำชุมชนแบบออนไลน์
      </p>
    </header>

    <!-- Latest News -->
    <section class="max-w-5xl mx-auto py-12 px-6">
      <div class="flex items-center gap-2 mb-6">
        <h2 class="text-2xl font-bold text-gray-800">📰 ข่าวประชาสัมพันธ์ล่าสุด</h2>
        <span class="h-1 flex-grow bg-gray-200 rounded"></span>
      </div>

      <div v-if="newsList.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="news in newsList" :key="news.id" class="bg-white rounded-xl shadow-sm hover:shadow-md transition overflow-hidden border border-gray-100 flex flex-col">
          <div class="h-48 bg-gray-200 relative">
            <img v-if="news.image" :src="news.image" class="w-full h-full object-cover" alt="News" />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-4xl">📰</div>
          </div>
          <div class="p-5 flex-grow">
            <h3 class="font-bold text-lg text-gray-800 mb-2 line-clamp-2">{{ news.title }}</h3>
            <p class="text-gray-600 text-sm line-clamp-3">{{ news.content }}</p>
          </div>
          <div class="px-5 pb-4 pt-0 text-xs text-gray-400">ประกาศเมื่อ: {{ news.created_at_formatted }}</div>
        </div>
      </div>

      <div v-else class="text-center py-10 bg-white rounded-xl border border-dashed">
        <p class="text-gray-500">ยังไม่มีข่าวสารในขณะนี้</p>
      </div>
    </section>

    <footer class="bg-brand-darkBlue text-white text-center py-6 mt-10">
      <p class="text-sm opacity-80">ระบบชุมชนบ้านสร้างขุนศรี | ติดต่อผู้ใหญ่บ้าน โทร. 0xx-xxx-8584</p>
    </footer>
  </div>

  <!-- ======================  ผู้ใช้งานล็อกอิน  ====================== -->
  <div v-else class="min-h-screen bg-gray-50">

    <nav class="bg-brand-darkBlue text-white shadow-md px-6 py-4 flex justify-between items-center sticky top-0 z-50">
      <h1 class="text-xl font-bold"> Community</h1>

      <div class="flex items-center gap-6">
        <router-link to="/profile" class="hidden sm:flex items-center gap-2 text-sm text-brand-softYellow hover:text-white transition cursor-pointer">
          <div class="w-8 h-8 rounded-full bg-brand-yellow text-brand-darkBlue flex items-center justify-center font-bold text-xs border border-white/20">
            {{ user.first_name ? user.first_name[0] : 'U' }}
          </div>
          <span>คุณ{{ user.first_name || user.username }}</span>
        </router-link>

        <button @click="logout" class="bg-red-500/80 hover:bg-red-600 text-white text-xs px-4 py-2 rounded-lg transition shadow-sm">ออกจากระบบ</button>
      </div>
    </nav>

    <!-- ⭐ Hero Slider -->
    <HeroSlider />

    <main class="max-w-4xl mx-auto p-6 space-y-8">
      <div class="bg-white rounded-2xl p-8 shadow-sm border-l-8 border-brand-yellow flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-gray-800"> คุณ{{ user.first_name || "สมาชิก" }} </h2>
          <p class="text-gray-500 mt-1">ยินดีต้อนรับกลับสู่ชุมชนบ้านสร้างขุนศรี</p>
        </div>
      </div>

      <section>
        <h3 class="text-lg font-semibold text-gray-700 mb-4 border-b pb-2">บริการออนไลน์</h3>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <router-link to="/report/create" class="service-card group border-red-100 hover:border-red-200">
            <div class="icon-circle bg-red-50 text-red-500 group-hover:bg-red-500 group-hover:text-white"></div>
            <span class="font-medium text-gray-700 group-hover:text-red-600">แจ้งปัญหา</span>
          </router-link>

          <router-link to="/booking/create" class="service-card group border-blue-100 hover:border-blue-200">
            <div class="icon-circle bg-blue-50 text-blue-500 group-hover:bg-blue-500 group-hover:text-white"></div>
            <span class="font-medium text-gray-700 group-hover:text-blue-600">ยืมของ/จองที่</span>
          </router-link>

          <router-link to="/appointment/create" class="service-card group border-green-100 hover:border-green-200">
            <div class="icon-circle bg-green-50 text-green-500 group-hover:bg-green-500 group-hover:text-white"></div>
            <span class="font-medium text-gray-700 group-hover:text-green-600">นัดหมายผู้นำ</span>
          </router-link>

          <router-link to="/public-service" class="service-card group border-yellow-100 hover:border-yellow-200">
            <div class="icon-circle bg-yellow-50 text-yellow-600 group-hover:bg-yellow-500 group-hover:text-white"></div>
            <span class="font-medium text-gray-700 group-hover:text-yellow-600">สาธารณะ</span>
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.service-card {
  @apply bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition hover:-translate-y-1 flex flex-col items-center gap-3 text-center cursor-pointer border;
}
.icon-circle {
  @apply w-14 h-14 rounded-full flex items-center justify-center text-2xl transition;
}
</style>
