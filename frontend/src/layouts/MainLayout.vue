<template>
  <div class="min-h-screen flex flex-col bg-brand-softYellow">

    <!-- Navbar -->
    <nav class="bg-white/80 backdrop-blur border-b border-brand-cream shadow-sm">
      <div class="container mx-auto flex justify-between items-center py-4 px-4">

        <!-- Logo -->
        <h1 class="text-2xl font-extrabold text-brand-darkBlue tracking-wide">
          Community
        </h1>

        <!-- Menu -->
        <div class="flex items-center space-x-6 text-brand-darkBlue font-medium">

          <!-- ไม่ได้ล็อกอิน -->
          <template v-if="!isLoggedIn">
            <router-link to="/register-request" class="hover:text-pink-600 transition">
              ลงทะเบียน
            </router-link>
            <router-link
              to="/login"
              class="px-3 py-1 bg-pink-400 text-white rounded-lg hover:bg-pink-500 transition"
            >
              เข้าสู่ระบบ
            </router-link>
          </template>

          <!-- ผู้ใช้ทั่วไป -->
          <template v-else-if="role === 'user'">
            <router-link to="/profile" class="hover:text-brand-orange">โปรไฟล์</router-link>
            <button @click="logout" class="hover:text-red-500">ออกจากระบบ</button>
          </template>

          <!-- ผู้ใหญ่บ้าน -->
          <template v-else-if="role === 'admin'">
            <router-link to="/" class="hover:text-brand-orange">หน้าแรก</router-link>
            <router-link to="/admin/dashboard" class="hover:text-brand-orange">จัดการระบบ</router-link>
            <span class="text-sm">สวัสดี, {{ user.full_name || user.username }}</span>
            <button @click="logout" class="hover:text-red-500">ออกจากระบบ</button>
          </template>

          <!-- สถานะผู้ใหญ่บ้าน -->
          <div class="flex items-center space-x-2 ml-3 pl-3 border-l border-gray-300">
            <div
              class="w-3 h-3 rounded-full"
              :class="isHeadmanOnline ? 'bg-green-500' : 'bg-gray-400'"
            ></div>
            <span class="text-sm opacity-80">
              {{ isHeadmanOnline ? "พร้อมให้บริการ" : "ไม่พร้อมให้บริการ" }}
            </span>
          </div>

        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 container mx-auto p-6">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="text-center text-gray-500 text-sm p-4">
      ระบบชุมชนบ้านสร้างขุนศรี | ติดต่อผู้ใหญ่บ้าน โทร. 0xx-xxx-8584
    </footer>

  </div>
</template>



<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";

/* -------------------------------------------------------------
   โหลด user แบบปลอดภัย + reactive
------------------------------------------------------------- */
const user = ref({});
const storedUser = localStorage.getItem("user");

try {
  user.value =
    storedUser && storedUser !== "undefined" ? JSON.parse(storedUser) : {};
} catch {
  user.value = {};
}

/* -------------------------------------------------------------
   role ต้องเป็น computed → reactive
------------------------------------------------------------- */
const role = computed(() => user.value.role || null);

/* -------------------------------------------------------------
   token ต้องอ่านแบบ reactive
------------------------------------------------------------- */
const token = computed(() => localStorage.getItem("access"));

/* -------------------------------------------------------------
   เช็คว่าเข้าสู่ระบบหรือยัง
------------------------------------------------------------- */
const isLoggedIn = computed(() => !!token.value);

/* -------------------------------------------------------------
   สถานะผู้ใหญ่บ้าน
------------------------------------------------------------- */
const isHeadmanOnline = ref(false);

const loadStatus = async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/accounts/status/headman/");
    isHeadmanOnline.value = res.data.is_online;
  } catch (err) {
    console.error("โหลดสถานะผู้ใหญ่บ้านล้มเหลว", err);
  }
};

/* -------------------------------------------------------------
   ออกจากระบบ
------------------------------------------------------------- */
const logout = () => {
  localStorage.clear();
  window.location.href = "/login";
};

/* -------------------------------------------------------------
   เรียกทุกครั้งที่โหลดหน้า
------------------------------------------------------------- */
onMounted(() => {
  loadStatus();
  setInterval(loadStatus, 15000);
});
</script>
