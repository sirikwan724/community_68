<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const user = ref({});
const isHeadmanOnline = ref(false);

onMounted(() => {
  const userData = localStorage.getItem("user");
  if (userData) {
    user.value = JSON.parse(userData);
  }
});

onMounted(() => {
  fetchHeadmanStatus();
});

const logout = () => {
  localStorage.clear();
  router.push("/login");
};

const fetchHeadmanStatus = async () => {
  const res = await axios.get("http://localhost:8000/api/accounts/status/headman/");
  isHeadmanOnline.value = res.data.is_online;
};

const toggleStatus = async () => {
  const token = localStorage.getItem("access");

  const res = await axios.patch(
    "http://localhost:8000/api/accounts/status/headman/update/",
    { is_online: !isHeadmanOnline.value },
    { headers: { Authorization: `Bearer ${token}` } }
  );

  isHeadmanOnline.value = res.data.is_online;
};

</script>

<template>
  <div class="min-h-screen bg-gray-100 font-sans">
    
    <nav class="bg-yellow-100 text-gray shadow-lg px-6 py-4 flex justify-between items-center sticky top-0 z-50 border-b-4 border-yellow-300">
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-bold tracking-wide cursor-pointer hover:opacity-80 transition" @click="router.push('/admin/dashboard')">
             ผู้ดูแลระบบชุมชนบ้านสร้างขุนศรี
        </h1>
      </div>
      
      <div class="flex items-center gap-4">
            <button
              @click="toggleStatus"
              class="px-4 py-1 rounded bg-green-600 text-white"
              :class="isHeadmanOnline ? 'bg-green-500' : 'bg-red-500'"
            >
              <span class="text-sm opacity-80">{{ isHeadmanOnline ? "พร้อมให้บริการ" : "ไม่พร้อมให้บริการ" }}</span>
            </button>
            <button @click="logout" class="bg-red-500 hover:bg-white/20 bg-gray-100 text-sm px-3 py-2 rounded border border-white/20 transition">
              ออกจากระบบ
            </button>
        <div 
            class="hidden sm:flex text-right flex-col cursor-pointer hover:opacity-80 transition"
            @click="router.push('/admin/profile')"
        >
            <span class="text-sm font-semibold bg-gray-100">
                {{ user.first_name || 'Admin' }}
            </span>
        </div>

      </div>
    </nav>

    <main class="p-6">
      <router-view />
    </main>

  </div>
</template>