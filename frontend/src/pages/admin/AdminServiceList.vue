<template>
  <div class="p-6">

    <!-- ปุ่มกลับ -->
    <router-link
      to="/admin/dashboard"
      class="inline-block bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
    >
      กลับหน้าหลัก
    </router-link>

    <h1 class="text-2xl font-bold mt-4 mb-6">บริหารจัดการบริการสาธารณะ</h1>

    <!-- ปุ่มฟิลเตอร์ -->
    <div class="flex gap-2 mb-4">
      <button
        @click="filterType = 'all'"
        :class="filterType === 'all' ? active : inactive"
      >ทั้งหมด</button>

      <button
        @click="filterType = 'washer'"
        :class="filterType === 'washer' ? active : inactive"
      >ตู้ซักผ้า</button>

      <button
        @click="filterType = 'water'"
        :class="filterType === 'water' ? active : inactive"
      >ตู้กดน้ำ</button>

      <button
        @click="filterType = 'other'"
        :class="filterType === 'other' ? active : inactive"
      >อื่น ๆ</button>
    </div>

    <!-- ปุ่มเพิ่ม -->
    <router-link
      to="/admin/services/create"
      class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
    >
      ➕ เพิ่มบริการใหม่
    </router-link>

    <!-- ถ้าไม่มีรายการ -->
    <div v-if="filteredServices.length === 0" class="mt-10 text-gray-500">
      ไม่มีบริการที่พบตามเงื่อนไข
    </div>

    <!-- รายการบริการ -->
    <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="item in filteredServices"
        :key="item.id"
        class="bg-white shadow border rounded-lg p-4 relative"
      >
        <!-- เมนู 3 จุด -->
        <div class="absolute right-3 top-3 cursor-pointer" @click="openMenu(item.id)">
          ⋮
        </div>

        <!-- เมนูแก้ไข/ลบ -->
        <div
          v-if="menuOpen === item.id"
          class="absolute right-3 top-8 bg-white border rounded shadow-lg z-10"
        >
          <div @click="editService(item.id)" class="px-4 py-2 hover:bg-gray-100 cursor-pointer">
            แก้ไข
          </div>
          <div @click="deleteService(item.id)" class="px-4 py-2 hover:bg-red-100 cursor-pointer text-red-600">
            ลบ
          </div>
        </div>

        <!-- รูป -->
        <img v-if="item.image" :src="item.image" class="w-full h-40 rounded object-cover" />

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
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const services = ref([]);
const menuOpen = ref(null);
const router = useRouter();

const filterType = ref("all"); // <-- ค่า default

// โหลดข้อมูล
onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/services/");
    services.value = res.data;
    console.log("SERVICES:", services.value);
  } catch (err) {
    console.error(err);
  }
});

// ฟิลเตอร์รายการตาม category
const filteredServices = computed(() => {
  if (filterType.value === "all") return services.value;

  return services.value.filter(
    (s) => s.category === filterType.value  // << ใช้ category ที่มาจาก API
  );
});

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
</script>
