<template>
  <div class="p-6">
    <div class="flex gap-3 mb-4 items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">บริหารจัดการบริการสาธารณะ</h1>

      <div class="flex items-center gap-3">
        <select
        v-model="activeFilter"
        @change="changeFilter(activeFilter)"
        class="px-4 py-2 border rounded-lg shadow-sm"
      >
        <option value="all">ทั้งหมด</option>
        <option value="washer">ตู้ซักผ้า</option>
        <option value="water">ตู้กดน้ำ</option>
        <option value="other">อื่น ๆ</option>
      </select>
      
        <router-link
          to="/admin/services/create"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
             เพิ่มบริการใหม่
        </router-link>
        
        <router-link
          to="/admin/dashboard"
          class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
        >
          กลับหน้าหลัก
        </router-link>
        
      </div>
    </div>

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
        <div class="absolute right-2 top-1 cursor-pointer text-2xl" @click="openMenu(item.id)">
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

/* ===============================
   1) ตัวแปรฟิลเตอร์
================================ */
const activeFilter = ref("all");

const changeFilter = (type) => {
  activeFilter.value = type;
};

/* ===============================
   2) map ค่าให้ตรงกับ backend
   (backend ใช้ category)
================================ */
const typeMap = {
  washer: "washer",
  water: "water",
  other: "other",
};

/* ===============================
   3) โหลดข้อมูลจาก backend
================================ */
onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:8000/api/services/");
    services.value = res.data;

    // ใช้ตรวจสอบชั่วคราว (ลบได้ภายหลัง)
    console.log(
      "SERVICE CATEGORIES:",
      services.value.map(s => s.category)
    );
  } catch (err) {
    console.error(err);
  }
});

/* ===============================
   4) ฟิลเตอร์ (จุดสำคัญที่สุด)
================================ */
const filteredServices = computed(() => {
  if (activeFilter.value === "all") {
    return services.value;
  }

  return services.value.filter(
    service => service.category === typeMap[activeFilter.value]
  );
});

/* ===============================
   5) เมนู / แก้ไข / ลบ
   (ไม่แตะ ไม่กระทบ)
================================ */
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

