<template>
  <div class="p-6">

    <!-- ปุ่มกลับหน้าแดชบอร์ด -->
    <div class="mb-4">
      <router-link
        to="/admin/dashboard"
        class="inline-block bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
      >
       กลับหน้าหลัก
      </router-link>
    </div>

    <h1 class="text-2xl font-bold mb-6">บริหารจัดการบริการสาธารณะ</h1>

    <!-- ปุ่มเพิ่ม -->
    <router-link
      to="/admin/services/create"
      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
    >
      ➕ เพิ่มบริการใหม่
    </router-link>

    <!-- ไม่มีข้อมูล -->
    <div v-if="services.length === 0" class="mt-10 text-gray-500">
      ยังไม่มีบริการสาธารณะ
    </div>

    <!-- ตารางข้อมูล -->
    <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="item in services"
        :key="item.id"
        class="bg-white shadow border rounded-lg p-4 relative"
      >
        <!-- เมนู 3 จุด -->
        <div class="absolute right-3 top-3 cursor-pointer" @click="openMenu(item.id)">
          ⋮
        </div>

        <!-- เมนูดรอปดาวน์ -->
        <div
          v-if="menuOpen === item.id"
          class="absolute right-3 top-8 bg-white border rounded shadow-lg z-10"
        >
          <div
            class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
            @click="editService(item.id)"
          >
             แก้ไข
          </div>
          <div
            class="px-4 py-2 hover:bg-red-100 cursor-pointer text-red-600"
            @click="deleteService(item.id)"
          >
             ลบ
          </div>
        </div>

        <img
          v-if="item.image"
          :src="item.image"
          class="w-full h-40 rounded object-cover"
        />

        <h2 class="font-bold text-lg mt-2">{{ item.name }}</h2>
        <p class="text-sm text-gray-600">{{ item.location }}</p>

        <span
          class="inline-block mt-2 px-2 py-1 text-xs rounded-full"
          :class="{
            'bg-green-100 text-green-700': item.status === 'normal',
            'bg-yellow-100 text-yellow-700': item.status === 'maintenance',
            'bg-red-100 text-red-700': item.status === 'broken'
          }"
        >
          {{
            item.status === "normal"
              ? "ใช้งานปกติ"
              : item.status === "maintenance"
              ? "กำลังซ่อม"
              : "ชำรุด"
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

const services = ref([]);
const menuOpen = ref(null);
const router = useRouter();

const openMenu = (id) => {
  menuOpen.value = menuOpen.value === id ? null : id;
};

const editService = (id) => {
  router.push(`/admin/services/${id}/edit`);
};

const deleteService = async (id) => {
  if (!confirm("ต้องการลบบริการนี้หรือไม่?")) return;

  try {
    await axios.delete(`http://localhost:8000/api/services/${id}/`);
    services.value = services.value.filter((s) => s.id !== id);
    alert("ลบสำเร็จ");
  } catch (err) {
    console.error(err);
  }
};

onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/services/");
    services.value = res.data;
  } catch (err) {
    console.error(err);
  }
});
</script>
