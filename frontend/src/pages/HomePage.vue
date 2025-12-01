<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import HeroSlider from "@/components/HeroSlider.vue"; 

const router = useRouter();
const isLoggedIn = ref(false);
const user = ref({});
const newsList = ref([]);

// โหลดข้อมูลจาก localStorage
const token = localStorage.getItem("access");
const storedUser = localStorage.getItem("user");

if (token) {
  isLoggedIn.value = true;

  if (storedUser && storedUser !== "undefined") {
    try {
      user.value = JSON.parse(storedUser);
    } catch (e) {
      console.error("Parse error:", e);
      user.value = {};
    }
  } else {
    user.value = {};
  }
}

onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/accounts/news/");
    newsList.value = res.data;
  } catch (err) {
    console.error("ไม่สามารถดึงข่าวได้", err);
    newsList.value = [];
  }
});

const logout = () => {
  localStorage.removeItem("user");
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("role");

  isLoggedIn.value = false;
  user.value = {};
  router.push("/login");
};
</script>



<template>
  <div class="container mx-auto p-6 max-w-6xl">

    <!-- Navbar -->
    <nav class="flex justify-between items-center py-4 border-b border-gray-200 mb-6">
      <router-link to="/">
        <h1 class="text-3xl font-bold text-gray-800 hover:text-blue-700 transition">
           ชุมชนบ้านสร้างขุนศรี
        </h1>
      </router-link>

      <div v-if="isLoggedIn" class="flex items-center gap-4">
        <span class="text-lg font-medium text-gray-600">
          สวัสดี, คุณ{{ user.full_name || user.username }}
        </span>

      </div>
    </nav>

    <HeroSlider class="mb-10" />

    <!-- ====================  NOT LOGGED IN ==================== -->
    <div v-if="!isLoggedIn">
      <!-- เมนูชุมชน -->
      <section class="mt-10">
        <h2 class="text-2xl font-bold text-gray-800 mb-4"> เมนูชุมชน </h2>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">

      <!-- เมนูบริการสาธารณะ -->
          <router-link
            to="/public-services"
            class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-yellow-500"
          >
            <p class="font-medium text-gray-700">บริการสาธารณะ</p>
          </router-link>

    <!-- สามารถเพิ่มเมนูอื่นในอนาคตได้ -->
  </div>
</section>


      <h2 class="text-3xl font-extrabold mb-6 text-gray-800">
        ข่าวสารชุมชนหมู่บ้าน
      </h2>

      <div class="bg-blue-50 p-6 rounded-lg mb-10 border border-blue-100 shadow-inner">
        <p class="text-gray-700 text-base">
          ยินดีต้อนรับสู่ศูนย์กลางข้อมูล! เมนูแจ้งปัญหา ขอความช่วยเหลือ ฯลฯ
        </p>
        <div class="mt-4 flex gap-3">
          <router-link
            to="/login"
            class="px-5 py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-md"
          >
            เข้าสู่ระบบเพื่อใช้บริการ
          </router-link>
        </div>
      </div>

      <!-- ข่าว -->
      <div class="space-y-6">
        <div
          v-if="newsList.length === 0"
          class="text-center py-10 text-gray-500 border rounded-lg bg-white shadow-sm"
        >
          ยังไม่มีการประกาศข่าวสารในขณะนี้
        </div>

        <router-link
          v-for="news in newsList"
          :key="news.id"
          :to="`/news/${news.id}`"
          class="block bg-white p-5 rounded-lg shadow-md border border-gray-100 
                 flex flex-col sm:flex-row gap-5 transition hover:shadow-lg"
        >
          <div v-if="news.image" class="w-full h-40 sm:w-36 sm:h-28 flex-shrink-0">
            <img :src="news.image" class="w-full h-full object-cover rounded-lg" />
          </div>

          <div class="flex-grow">
            <h3 class="font-bold text-xl text-gray-800 mb-1 line-clamp-2 hover:text-blue-700 transition">
              {{ news.title }}
            </h3>
            <p class="text-gray-600 text-sm line-clamp-3">
              {{ news.content }}
            </p>

            <div class="mt-2 text-xs text-gray-400">
              โพสต์เมื่อ: {{ news.created_at_formatted }}
            </div>
          </div>
        </router-link>
      </div>
    </div>



    <!-- ====================  LOGGED IN (USER DASHBOARD) ==================== -->
    <div v-else>
      <h2 class="text-2xl font-semibold text-gray-700 mb-6">
        เมนูชุมชน
      </h2>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">

        <!-- บริการสาธารณะ -->
        <router-link
          to="/public-services"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-yellow-500"
        >
          <span class="text-lg font-medium text-gray-700">บริการสาธารณะ</span>
        </router-link>
        
        <router-link
          to="/request-help"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-gray-500"
        >
          <span class="text-lg font-medium text-gray-700">ขอความอนุเคราะห์</span>
        </router-link>

        <!-- ส่งคำร้อง -->
        <router-link
          to="/report/create"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-blue-500"
        >
          <span class="text-lg font-medium text-gray-700">ส่งคำร้อง/แจ้งปัญหา</span>
        </router-link>

        <router-link 
          to="/my-history"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-blue-500"
        >
          <span class="text-lg font-medium text-gray-700">ประวัติของฉัน</span>
        </router-link>

        <!-- ประวัติคำร้อง
        <router-link
          to="/report/list"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-teal-500"
        >
          <span class="text-lg font-medium text-gray-700">ประวัติคำร้อง</span>
        </router-link> -->

        <!-- เฉพาะ Admin -->
        <router-link
          v-if="user.role === 'admin'"
          to="/admin/dashboard"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-lg transition text-center border-t-4 border-red-500"
        >
          <span class="text-lg font-bold text-red-600">จัดการระบบ</span>
        </router-link>
      </div>


      <!-- ข่าว -->
      <h2 class="text-2xl font-semibold text-gray-700 mt-10 mb-6">
         ข่าวสารชุมชน
      </h2>

      <div class="space-y-6">
        <div
          v-if="newsList.length === 0"
          class="text-center py-10 text-gray-500 border rounded-lg bg-white shadow-sm"
        >
          ยังไม่มีการประกาศข่าวสารในขณะนี้
        </div>

        <router-link
          v-for="news in newsList"
          :key="news.id"
          :to="`/news/${news.id}`"
          class="block bg-white p-5 rounded-lg shadow-md border border-gray-100 
                 flex flex-col sm:flex-row gap-5 transition hover:shadow-lg"
        >
          <div v-if="news.image" class="w-full h-40 sm:w-36 sm:h-28 flex-shrink-0">
            <img :src="news.image" class="w-full h-full object-cover rounded-lg" />
          </div>

          <div class="flex-grow">
            <h3 class="font-bold text-xl text-gray-800 mb-1 line-clamp-2 hover:text-blue-700 transition">
              {{ news.title }}
            </h3>

            <p class="text-gray-600 text-sm line-clamp-3">
              {{ news.content }}
            </p>

            <div class="mt-2 text-xs text-gray-400">
              โพสต์เมื่อ: {{ news.created_at_formatted }}
            </div>
          </div>
        </router-link>
      </div>
    </div>

  </div>
</template>
