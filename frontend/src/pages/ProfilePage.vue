<script setup>
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const user = ref({});
const loading = ref(false);
const editing = ref(false);

// ฟอร์มสำหรับแก้ไขข้อมูล (แยกออกมาเพื่อเปรียบเทียบค่า)
const editForm = reactive({
  first_name: "",
  last_name: "",
  phone: "",
  address: "",
  citizen_id: "",     // รหัสทะเบียนบ้าน/บัตรประชาชน
  house_owner_name: "" // ชื่อเจ้าบ้าน
});

// โหลดข้อมูล User
onMounted(() => {
  loadUserData();
});

const loadUserData = () => {
  const storedUser = localStorage.getItem("user");
  if (storedUser) {
    user.value = JSON.parse(storedUser);
    // map ข้อมูลเข้าฟอร์มแก้ไขเตรียมไว้
    Object.assign(editForm, user.value);
  }
};

const logout = () => {
  localStorage.clear();
  window.location.href = "/login";
};

// --- ฟังก์ชันบันทึกข้อมูล ---
const saveChanges = async () => {
  loading.value = true;

  try {
    // 1. ส่วนที่แก้ไขได้ทันที (General Info)
    // เช็คว่ามีการเปลี่ยนแปลงไหม
    const generalChanged = 
        editForm.first_name !== user.value.first_name || 
        editForm.last_name !== user.value.last_name || 
        editForm.phone !== user.value.phone;

    if (generalChanged) {
        // TODO: ยิง API อัปเดตข้อมูลทั่วไป (PUT /api/accounts/me/)
        // await axios.patch('http://localhost:8000/api/accounts/me/', {
        //     first_name: editForm.first_name,
        //     last_name: editForm.last_name,
        //     phone: editForm.phone
        // });

        // จำลองว่าอัปเดตสำเร็จ
        user.value.first_name = editForm.first_name;
        user.value.last_name = editForm.last_name;
        user.value.phone = editForm.phone;
        localStorage.setItem("user", JSON.stringify(user.value)); // อัปเดต LocalStorage
    }

    // 2. ส่วนที่ต้องส่งคำร้อง (Sensitive Info)
    const sensitiveChanged = 
        editForm.address !== user.value.address || 
        editForm.citizen_id !== user.value.citizen_id || 
        editForm.house_owner_name !== user.value.house_owner_name;

    if (sensitiveChanged) {
        // TODO: ยิง API สร้างคำร้อง (POST /api/requests/change-info/)
        // await axios.post('http://localhost:8000/api/requests/change-info/', {
        //     type: 'change_info',
        //     new_data: {
        //         address: editForm.address,
        //         citizen_id: editForm.citizen_id,
        //         house_owner_name: editForm.house_owner_name
        //     }
        // });

        // แจ้งเตือน User
        alert("✅ ข้อมูลส่วนตัวอัปเดตเรียบร้อย \n📝 ส่วนที่อยู่/ทะเบียนบ้าน ได้ส่งคำร้องไปยังผู้ใหญ่บ้านเพื่อตรวจสอบแล้วครับ");
    } else if (generalChanged) {
        alert("✅ บันทึกข้อมูลส่วนตัวเรียบร้อยแล้ว");
    }

    // ออกจากโหมดแก้ไข
    editing.value = false;

  } catch (err) {
    console.error(err);
    alert("เกิดข้อผิดพลาดในการบันทึกข้อมูล");
  } finally {
    loading.value = false;
  }
};

// --- ฟังก์ชันขอลบบัญชี ---
const requestDeleteAccount = async () => {
  const confirmDelete = confirm("⚠️ คำเตือน: คุณต้องการลบบัญชีนี้ถาวรใช่หรือไม่? \nการกระทำนี้ไม่สามารถย้อนกลับได้");
  
  if (confirmDelete) {
    try {
        // TODO: ยิง API ลบบัญชี (DELETE /api/accounts/me/)
        // await axios.delete('http://localhost:8000/api/accounts/me/');
        
        alert("บัญชีของคุณถูกลบเรียบร้อยแล้ว");
        logout(); // เด้งออกไปหน้า Login
    } catch (err) {
        alert("ไม่สามารถลบบัญชีได้ กรุณาติดต่อผู้ดูแลระบบ");
    }
  }
};

// ยกเลิกแก้ไข (Reset ค่ากลับเป็นเดิม)
const cancelEdit = () => {
  Object.assign(editForm, user.value);
  editing.value = false;
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-softYellow via-brand-cream to-white p-6">

    <div class="w-full max-w-2xl bg-white/90 shadow-xl rounded-3xl p-10 border border-brand-cream backdrop-blur-sm relative">

      <div class="text-center mb-8">
        <h1 class="text-3xl font-extrabold text-brand-darkBlue">
          โปรไฟล์ของฉัน
        </h1>
        <p class="text-gray-600 mt-1 text-sm">จัดการข้อมูลส่วนตัวและบัญชีผู้ใช้</p>
      </div>

      <div v-if="!editing" class="space-y-5">
        
        <div class="flex flex-col items-center pb-4 border-b border-gray-100">
            <div class="w-20 h-20 rounded-full bg-brand-yellow text-brand-darkBlue flex items-center justify-center text-3xl font-bold shadow-md mb-3">
                {{ user.first_name ? user.first_name[0] : 'U' }}
            </div>
            <h2 class="text-xl font-bold text-gray-800">{{ user.first_name }} {{ user.last_name }}</h2>
            <span class="text-sm text-gray-500">@{{ user.username }}</span>
            <span class="mt-2 px-3 py-1 rounded-full text-xs font-medium"
                  :class="user.verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                {{ user.verified ? 'ยืนยันตัวตนแล้ว' : 'รอการตรวจสอบ' }}
            </span>
        </div>

        <div class="grid grid-cols-1 gap-4">
            <div class="profile-row">
                <span class="label">เบอร์โทรศัพท์</span>
                <span class="value">{{ user.phone || '-' }}</span>
            </div>
            <div class="profile-row">
                <span class="label">ที่อยู่</span>
                <span class="value">{{ user.address || '-' }}</span>
            </div>
            <div class="profile-row">
                <span class="label">รหัสทะเบียนบ้าน</span>
                <span class="value">{{ user.citizen_id || '-' }}</span>
            </div>
            <div class="profile-row">
                <span class="label">ชื่อเจ้าบ้าน</span>
                <span class="value">{{ user.house_owner_name || '-' }}</span>
            </div>
        </div>

        <div class="mt-8 flex justify-center gap-4">
          <button @click="editing = true" class="btn-primary">
             แก้ไขข้อมูล
          </button>
          <button @click="logout" class="btn-secondary">
            ออกจากระบบ
          </button>
        </div>

      </div>

      <div v-else class="space-y-6">
        
        <div class="bg-green-50 p-4 rounded-xl border border-green-100">

            <div class="grid grid-cols-2 gap-4 mb-3">
                <div>
                    <label class="text-xs text-gray-500 ml-1">ชื่อจริง</label>
                    <input v-model="editForm.first_name" type="text" class="input-field">
                </div>
                <div>
                    <label class="text-xs text-gray-500 ml-1">นามสกุล</label>
                    <input v-model="editForm.last_name" type="text" class="input-field">
                </div>
            </div>
            <div>
                <label class="text-xs text-gray-500 ml-1">เบอร์โทรศัพท์</label>
                <input v-model="editForm.phone" type="text" class="input-field">
            </div>
        </div>

        <div class="bg-yellow-50 p-4 rounded-xl border border-yellow-100">
 
            <div class="space-y-3">
                <div>
                    <label class="text-xs text-gray-500 ml-1">ที่อยู่ปัจจุบัน</label>
                    <textarea v-model="editForm.address" rows="2" class="input-field"></textarea>
                </div>
                <div>
                    <label class="text-xs text-gray-500 ml-1">รหัสทะเบียนบ้าน </label>
                    <input v-model="editForm.citizen_id" type="text" class="input-field">
                </div>
                <div>
                    <label class="text-xs text-gray-500 ml-1">ชื่อเจ้าบ้าน</label>
                    <input v-model="editForm.house_owner_name" type="text" class="input-field">
                </div>
            </div>
        </div>

        <div class="flex justify-center gap-4 pt-4">
          <button @click="router.push('/')" class="btn-secondary">
            กลับหน้าหลัก
          </button>
          <button @click="cancelEdit" class="btn-secondary">
            ยกเลิก
          </button>
          <button @click="saveChanges" class="btn-primary w-32" :disabled="loading">
            {{ loading ? 'กำลังบันทึก...' : 'บันทึกข้อมูล' }}
          </button>
        </div>

      </div>

    </div>
  </div>
</template>

<style scoped>
.profile-row {
  @apply flex justify-between py-3 border-b border-gray-100 last:border-0;
}
.label {
  @apply text-gray-500 font-medium;
}
.value {
  @apply text-brand-darkBlue font-semibold text-right;
}

.input-field {
  @apply w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 
         focus:outline-none focus:ring-2 focus:ring-brand-yellow focus:border-transparent transition;
}

.btn-primary {
  @apply px-6 py-2.5 rounded-xl bg-brand-yellow hover:bg-brand-orange 
         text-brand-dark font-semibold shadow active:scale-95 transition;
}

.btn-secondary {
  @apply px-6 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 
         text-gray-700 font-semibold transition active:scale-95;
}
</style>