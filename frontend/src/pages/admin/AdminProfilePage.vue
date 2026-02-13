<script setup>
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router"; // 1. Import useRouter

const router = useRouter(); // 2. ประกาศตัวแปร router
const user = ref({});
const editing = ref(false);
const loading = ref(false);

const form = reactive({
  first_name: "",
  last_name: "",
  phone: "",
  position: "ผู้ใหญ่บ้าน"
});

onMounted(() => {
  loadUserData();
});

const loadUserData = () => {
  const stored = localStorage.getItem("user");
  if (stored) {
    user.value = JSON.parse(stored);
    form.first_name = user.value.first_name;
    form.last_name = user.value.last_name;
    form.phone = user.value.phone;
  }
};

const saveProfile = async () => {
  loading.value = true;
  setTimeout(() => {
    user.value.first_name = form.first_name;
    user.value.last_name = form.last_name;
    user.value.phone = form.phone;
    localStorage.setItem("user", JSON.stringify(user.value));
    
    alert("✅ บันทึกข้อมูลส่วนตัวเรียบร้อยแล้ว");
    
    editing.value = false;
    loading.value = false;
  }, 800);
};

const cancelEdit = () => {
  form.first_name = user.value.first_name;
  form.last_name = user.value.last_name;
  form.phone = user.value.phone;
  editing.value = false;
};
</script>

<template>
  <div class="max-w-4xl mx-auto">
    
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">ข้อมูลส่วนตัว</h1>
        <p class="text-gray-500 text-sm">จัดการข้อมูลบัญชีและช่องทางการติดต่อ</p>
      </div>
      
      <router-link 
        to="/admin/dashboard" 
        class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
      
      <div class="h-32 bg-gradient-to-r from-brand-darkBlue to-blue-800"></div>

      <div class="px-8 pb-8 relative">
        
        <div class="relative -top-10 mb-[-20px] flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div class="flex items-end gap-4">
                <div class="w-24 h-24 rounded-xl border-4 border-white bg-white shadow-md flex items-center justify-center text-4xl overflow-hidden">
                    👮
                </div>
                <div class="mb-2">
                    <h2 class="text-2xl font-bold text-gray-800">
                        {{ user.first_name }} {{ user.last_name }}
                    </h2>
                    <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-semibold border border-blue-200">
                        {{ form.position }}
                    </span>
                </div>
            </div>
            
            <button 
                v-if="!editing"
                @click="editing = true"
                class="mb-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition flex items-center justify-center gap-2"
            >
                 แก้ไขข้อมูล
            </button>
        </div>

        <div class="border-t border-gray-100 my-6"></div>

        <div v-if="!editing" class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
                <label class="text-sm text-gray-500 block mb-1">ชื่อ - นามสกุล</label>
                <p class="text-lg font-medium text-gray-800">{{ user.first_name }} {{ user.last_name }}</p>
            </div>
            <div>
                <label class="text-sm text-gray-500 block mb-1">ตำแหน่ง</label>
                <p class="text-lg font-medium text-gray-800">{{ form.position }}</p>
            </div>
            <div>
                <label class="text-sm text-gray-500 block mb-1">เบอร์โทรศัพท์ติดต่อ</label>
                <p class="text-lg font-medium text-gray-800">{{ user.phone || '-' }}</p>
            </div>
            <div>
                <label class="text-sm text-gray-500 block mb-1">ชื่อผู้ใช้งาน (Username)</label>
                <p class="text-lg font-medium text-gray-500 font-mono">@{{ user.username }}</p>
            </div>
        </div>

        <form v-else @submit.prevent="saveProfile" class="space-y-6 max-w-2xl">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">ชื่อจริง</label>
                    <input v-model="form.first_name" type="text" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">นามสกุล</label>
                    <input v-model="form.last_name" type="text" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border">
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">ตำแหน่ง</label>
                <input v-model="form.position" type="text" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">เบอร์โทรศัพท์</label>
                <input v-model="form.phone" type="text" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border">
            </div>

            <div class="flex items-center gap-3 pt-4">
                <button type="submit" :disabled="loading" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm font-medium transition">
                    {{ loading ? 'กำลังบันทึก...' : 'บันทึกการเปลี่ยนแปลง' }}
                </button>
                <button type="button" @click="cancelEdit" class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition">
                    ยกเลิก
                </button>
            </div>
        </form>

      </div>
    </div>
  </div>
</template>