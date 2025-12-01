<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const fullName = ref("");
const phone = ref("");
const address = ref("");
const citizenId = ref("");
const username = ref("");
const password = ref("");
const houseOwnerName = ref("");

const success = ref("");
const error = ref("");
const router = useRouter();

const submitForm = async () => {
    success.value = "";
    error.value = "";

    try {
        await axios.post("http://localhost:8000/api/accounts/register-request/", {
            full_name: fullName.value,
            phone: phone.value,
            address: address.value,
            citizen_id: citizenId.value,
            house_owner_name: houseOwnerName.value,
            username: username.value,
            password: password.value,
        });

        // ⭐ ข้อความที่ต้องการให้ขึ้น
        success.value = "ส่งคำขอสมัครสำเร็จ! รอผลอนุมัติ";

        // ⭐ พากลับหน้าแรกอัตโนมัติหลัง 1.5 วินาที
        setTimeout(() => {
            router.push("/");
        }, 1500);

    } catch (err) {
        console.log("❌ Backend error:", err.response?.data);

        // ถ้า backend ส่งข้อความ error กลับมา
        if (err.response?.data) {
            error.value = JSON.stringify(err.response.data);
        } else {
            error.value = "เกิดข้อผิดพลาด กรุณาตรวจสอบข้อมูลอีกครั้ง";
        }
    }
};
</script>

<template>
  <div class="min-h-screen bg-brand-softYellow flex items-center justify-center p-5">
    <div class="bg-white shadow-lg rounded-2xl w-full max-w-2xl p-10">

      <!-- Back -->
      <router-link to="/" class="text-gray-600 flex items-center gap-2 hover:text-brand-darkBlue mb-6">
        <span class="text-xl">←</span> กลับหน้าหลัก
      </router-link>

      <!-- Title -->
      <h1 class="text-3xl font-bold text-center text-brand-darkBlue">
        สมัครเป็นชาวบ้าน
      </h1>
      <p class="text-center text-gray-500 mt-1 mb-8">
        ระบบชุมชนหมู่บ้านของเรา
      </p>

      <!-- FORM -->
      <form @submit.prevent="submitForm" class="space-y-6">

        <!-- Full Name -->
        <div>
          <label class="block text-gray-700 mb-1">ชื่อ - นามสกุล</label>
          <input
            type="text"
            v-model="fullName"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกชื่อ - นามสกุล"
          />
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-gray-700 mb-1">เบอร์โทรศัพท์</label>
          <input
            type="text"
            v-model="phone"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกเบอร์โทรศัพท์"
          />
        </div>

        <!-- Address -->
        <div>
          <label class="block text-gray-700 mb-1">ที่อยู่ / บ้านเลขที่ / หมู่บ้าน</label>
          <input
            type="text"
            v-model="address"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกที่อยู่"
          />
        </div>

        <!-- Citizen ID -->
        <div>
          <label class="block text-gray-700 mb-1">รหัสทะเบียนบ้าน (11 หลัก)</label>
          <input
            type="text"
            v-model="citizenId"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="XXXXXXXXXXX"
          />
        </div>

        <!-- House Owner -->
        <div>
          <label class="block text-gray-700 mb-1">ชื่อเจ้าบ้าน</label>
          <input
            type="text"
            v-model="houseOwnerName"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกชื่อเจ้าบ้าน"
          />
        </div>

        <!-- Username -->
        <div>
          <label class="block text-gray-700 mb-1">ชื่อผู้ใช้งาน</label>
          <input
            type="text"
            v-model="username"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกชื่อผู้ใช้งาน"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-gray-700 mb-1">รหัสผ่าน</label>
          <input
            type="password"
            v-model="password"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-darkBlue focus:outline-none"
            placeholder="กรอกรหัสผ่าน"
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="w-full py-3 bg-brand-darkBlue text-white font-semibold rounded-lg hover:bg-brand-orange transition"
        >
          ส่งคำขอสมัครสมาชิก
        </button>
      </form>

      <!-- ⭐ Success Message -->
      <p v-if="success" class="text-green-600 font-medium text-center mt-4">
        {{ success }}
      </p>

      <!-- ⭐ Error Message -->
      <p v-if="error" class="text-red-600 font-medium text-center mt-4">
        {{ error }}
      </p>

      <!-- Login Link -->
      <div class="text-center mt-6">
        <router-link to="/login" class="text-brand-darkBlue hover:text-brand-orange font-medium">
          มีบัญชีอยู่แล้ว? เข้าสู่ระบบ
        </router-link>
      </div>

    </div>
  </div>
</template>
