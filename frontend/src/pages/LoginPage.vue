<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const username = ref("");
const password = ref("");
const errorMessage = ref("");

const handleLogin = async () => {
  errorMessage.value = "";

  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = "กรุณากรอกข้อมูลให้ครบถ้วน";
    return;
  }

  try {
    const res = await axios.post("http://localhost:8000/api/accounts/login/", {
      username: username.value,
      password: password.value,
    });

    console.log("LOGIN RESPONSE =", res.data);

    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
    localStorage.setItem("role", res.data.role);
    localStorage.setItem("user", JSON.stringify(res.data.user));

    if (res.data.role === "admin") {
      router.push("/admin/dashboard");
    } else {
      router.push("/");
    } 
  }catch (err) {
    errorMessage.value = "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง";
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[#FAF7DB] px-4">
    <div
      class="bg-white w-full max-w-lg rounded-2xl shadow-lg p-8 border border-[#F2ECD2]"
    >
      <!-- Back -->
      <button
        @click="$router.push('/')"
        class="text-gray-500 text-sm flex items-center mb-4 hover:text-gray-700"
      >
        ← กลับหน้าหลัก
      </button>

      <!-- Title -->
      <h1 class="text-2xl font-bold text-center text-gray-800">
        เข้าสู่ระบบชุมชนบ้านสร้างขุนศรี
      </h1>

      <!-- Form -->
      <div class="mt-10 space-y-6">

        <!-- Username -->
        <div class="relative">
          <input
            v-model="username"
            type="text"
            class="peer w-full px-4 py-3 border rounded-lg bg-white outline-none 
                   border-gray-300 focus:border-blue-500 transition"
            required
          />
          <label
            class="absolute left-4 top-3 text-gray-500 px-1 transition-all
                   peer-focus:-top-2 peer-focus:text-xs peer-focus:text-blue-600
                   peer-valid:-top-2 peer-valid:text-xs peer-valid:text-blue-600
                   bg-white"
          >
            ชื่อผู้ใช้งาน
          </label>
        </div>

        <!-- Password -->
        <div class="relative">
          <input
            v-model="password"
            type="password"
            class="peer w-full px-4 py-3 border rounded-lg bg-white outline-none 
                   border-gray-300 focus:border-blue-500 transition"
            required
          />
          <label
            class="absolute left-4 top-3 text-gray-500 px-1 transition-all
                   peer-focus:-top-2 peer-focus:text-xs peer-focus:text-blue-600
                   peer-valid:-top-2 peer-valid:text-xs peer-valid:text-blue-600
                   bg-white"
          >
            รหัสผ่าน
          </label>
        </div>

        <!-- Error -->
        <p v-if="errorMessage" class="text-red-500 text-sm text-center">
          {{ errorMessage }}
        </p>

        <!-- Login button -->
        <button
          @click="handleLogin"
          class="w-full py-3 bg-[#5A4FF3] text-white font-semibold rounded-lg
                 hover:bg-[#473EC7] transition shadow-md"
        >
          เข้าสู่ระบบ
        </button>

        <!-- Register link -->
        <p class="text-center text-gray-600 text-sm mt-3">
          ยังไม่มีบัญชีผู้ใช้งาน?
          <router-link
            to="/register-request"
            class="text-blue-600 font-semibold hover:underline"
          >
            สมัครสมาชิกที่นี่
          </router-link>
        </p>

      </div>
    </div>
  </div>
</template>

<style>
/* เพื่อให้ label ลอยขึ้นเมื่อมีค่าใน input */
input:valid + label {
  top: -8px !important;
  font-size: 12px !important;
  color: #1c9a3e !important;
}
</style>
