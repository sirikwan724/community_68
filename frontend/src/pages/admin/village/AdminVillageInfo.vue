<template>
  <div class="max-w-4xl mx-auto">

    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">
        จัดการข้อมูลหมู่บ้าน
      </h1>        
      <p class="text-gray-500 text-sm">แก้ไขข้อมูลพื้นฐานของหมู่บ้านที่จะแสดงให้ผู้ใช้งานเห็น</p>
      </div>
      
      <router-link 
        to="/admin/dashboard" 
        class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- ฟอร์มแก้ไข -->
    <div class="bg-white rounded-xl shadow p-6 space-y-5">

      <!-- ชื่อหมู่บ้าน -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          ชื่อหมู่บ้าน
        </label>
        <input
          v-model="form.name"
          type="text"
          class="w-full border rounded-lg px-3 py-2 focus:ring focus:ring-blue-200"
        />
      </div>

      <!-- รายละเอียด -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          รายละเอียดหมู่บ้าน
        </label>
        <textarea
          v-model="form.description"
          rows="4"
          class="w-full border rounded-lg px-3 py-2 focus:ring focus:ring-blue-200"
        ></textarea>
      </div>

      <!-- ที่อยู่ -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          ที่อยู่
        </label>
        <input
          v-model="form.address"
          type="text"
          class="w-full border rounded-lg px-3 py-2 focus:ring focus:ring-blue-200"
        />
      </div>

      <!-- ปุ่มบันทึก -->
      <div class="flex justify-end gap-3 pt-4">
        <button
          class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
        >
          ยกเลิก
        </button>

        <button
          @click="save"
          class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          บันทึกข้อมูล
        </button>
      </div>

    </div>
  </div>
</template>
<script setup>
import { reactive } from "vue";

/**
 * mock ข้อมูลหมู่บ้าน
 * (อนาคตจะดึงจาก backend)
 */

const form = reactive({
  name: "หมู่บ้านสร้างขุนศรี",
  description: "ชุมชนเข้มแข็ง มีการบริหารจัดการร่วมกัน",
  address: "ตำบล … อำเภอ … จังหวัด …",
});

/**
 * บันทึกข้อมูล (ตอนนี้แค่จำลอง)
 */
const save = () => {
  console.log("บันทึกข้อมูลหมู่บ้าน:", form);
  alert("บันทึกข้อมูลเรียบร้อย (mock)");
};
</script>
