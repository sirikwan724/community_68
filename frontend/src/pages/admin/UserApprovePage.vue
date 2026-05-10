<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
// Import useRouter เพื่อใช้ในการเปลี่ยนเส้นทาง (ถ้าจำเป็น)
import { useRouter } from "vue-router";

const pendingUsers = ref([]);
const loading = ref(true);
const error = ref(null);
const router = useRouter(); 
const selectedUser = ref(null)
const showModal = ref(false)
const rejectReason = ref("")
// =======================
// ฟิลเตอร์ ปี / เดือน
// =======================
const selectedYear = ref("");
const selectedMonth = ref("");
const selectedStatus = ref("");

// =======================
// ปี (อัตโนมัติ)
// =======================
const currentYear = new Date().getFullYear();
const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

// =======================
// เดือน (อัตโนมัติ)
// =======================
const months = [
  { value: 1, label: "มกราคม" },
  { value: 2, label: "กุมภาพันธ์" },
  { value: 3, label: "มีนาคม" },
  { value: 4, label: "เมษายน" },
  { value: 5, label: "พฤษภาคม" },
  { value: 6, label: "มิถุนายน" },
  { value: 7, label: "กรกฎาคม" },
  { value: 8, label: "สิงหาคม" },
  { value: 9, label: "กันยายน" },
  { value: 10, label: "ตุลาคม" },
  { value: 11, label: "พฤศจิกายน" },
  { value: 12, label: "ธันวาคม" },
];

// เรียก API ดึงคำขอลงทะเบียน
const fetchRequests = async () => {
    loading.value = true;
    error.value = null;
    
    // ดึง Token จาก Local Storage
    const token = localStorage.getItem('access');
    if (!token) {
        // หากไม่มี Token ให้ redirect ไปหน้า Login
        router.push('/login');
        return;
    }

    try {
        const params = {};
        if (selectedYear.value) params.year = selectedYear.value;
        if (selectedMonth.value) params.month = selectedMonth.value;
        if (selectedStatus.value) params.status = selectedStatus.value;
        // API Call จริง: ดึงข้อมูลจาก Backend ที่เราสร้างไว้
        const res = await axios.get(
            "http://localhost:8000/api/accounts/admin/requests/all/", 
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                params: params,
            }
        );
        
        // ข้อมูลที่ได้จะถูกเก็บไว้ใน pendingUsers
        pendingUsers.value = res.data;
        
    } catch (err) {
        console.error("Error fetching registration requests:", err);
        // แสดงข้อผิดพลาดที่ชัดเจนขึ้น
        if (err.response && err.response.status === 403) {
             error.value = "คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (Admin เท่านั้น)";
        } else {
             error.value = "ไม่สามารถดึงรายการคำขอได้: " + (err.response?.data?.detail || err.message);
        }
        // ถ้าเกิดข้อผิดพลาดในการดึงข้อมูล ให้เซ็ตเป็น array ว่างเพื่อไม่ให้เกิด error ใน template
        pendingUsers.value = []; 
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchRequests();
});

const openModal = (user) => {
    selectedUser.value = user
    rejectReason.value = ""
    showModal.value = true
}

const closeModal = () => {
    showModal.value = false
    selectedUser.value = null
}

// ฟังก์ชันอนุมัติ
const approveUser = async (user) => {
    if (!confirm(`ยืนยันการอนุมัติคุณ ${user.full_name}?`)) return;

    const token = localStorage.getItem('access');
    try {
        //  API Call จริง: POST /api/accounts/admin/requests/{id}/approve/
        await axios.post(
            `http://localhost:8000/api/accounts/admin/requests/${user.id}/approve/`,
            {}, // ไม่มี Body
            { headers: { Authorization: `Bearer ${token}` } }
        );
        
        const target = pendingUsers.value.find(u => u.id === user.id)
        if (target) target.status = 'approved'
        
        closeModal();
        alert("✅ อนุมัติเรียบร้อย และสร้างบัญชีผู้ใช้แล้ว");
    } catch (err) {
        console.error("Approve Error:", err);
        alert("เกิดข้อผิดพลาดในการอนุมัติ: " + (err.response?.data?.detail || "กรุณาตรวจสอบ Console"));
    }
};

// ฟังก์ชันปฏิเสธ
const rejectUser = async (user) => {
    let reason = rejectReason.value.trim()

    if (!reason) {
        reason = prompt("กรุณาระบุเหตุผลที่ไม่อนุมัติ:")
        if (!reason) return
    }

    const token = localStorage.getItem('access');
    try {
        await axios.post(
            `http://localhost:8000/api/accounts/admin/requests/${user.id}/reject/`,
            { reason: reason },
            { headers: { Authorization: `Bearer ${token}` } }
        );

        const target = pendingUsers.value.find(u => u.id === user.id)
        if (target) target.status = 'rejected'

        closeModal();
        alert("❌ ปฏิเสธคำร้องเรียบร้อย");
    } catch (err) {
        console.error("Reject Error:", err);
        alert("เกิดข้อผิดพลาดในการปฏิเสธ: " + (err.response?.data?.detail || "กรุณาตรวจสอบ Console"));
    }
};
</script>

<template>
    <div class="min-h-screen bg-gray-50 p-6">
        <div class="max-w-5xl mx-auto">
            
            <div class="mb-6 flex items-center justify-between">
                <h1 class="text-3xl font-bold text-gray-800 flex items-center gap-3">
                    คำขอลงทะเบียนผู้ใช้ใหม่
                </h1>

                <div class="flex items-center gap-3">
                  <select v-model="selectedYear" class="border rounded px-5 py-2">
                    <option value="">ทุกปี</option>
                    <option v-for="year in years" :key="year" :value="year">
                      {{ year }}
                    </option>
                  </select>
                  <select v-model="selectedMonth" class="border rounded px-5 py-2">
                    <option value="">ทุกเดือน</option>
                    <option
                      v-for="m in months"
                      :key="m.value"
                      :value="m.value"
                    >
                      {{ m.label }}
                    </option>
                  </select>
                  <select v-model="selectedStatus" class="border rounded px-5 py-2">
                    <option value="">ทุกสถานะ</option>
                    <option value="pending">รออนุมัติ</option>
                    <option value="approved">อนุมัติแล้ว</option>
                    <option value="rejected">ปฏิเสธแล้ว</option>
                  </select>
              
                  <button
                    @click="fetchRequests"
                    class="bg-blue-600 text-white px-4 py-2 rounded"
                  >
                    ค้นหา
                  </button>

                  <router-link 
                     to="/admin/dashboard"
                     class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
                  >
                     กลับหน้าหลัก
                  </router-link>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                
                <div v-if="loading" class="p-10 text-center text-gray-500">
                    กำลังโหลดข้อมูล...
                </div>
                
                <div v-else-if="error" class="p-5 bg-red-100 text-red-700 border-l-4 border-red-500">
                    <p class="font-bold">เกิดข้อผิดพลาดในการโหลดข้อมูล:</p>
                    <p>{{ error }}</p>
                </div>
                <div v-else-if="pendingUsers.length === 0" class="p-10 text-center">
                    <div class="text-4xl mb-2">✅</div>
                    <h3 class="text-lg font-medium text-gray-900">ไม่มีคำร้องค้าง</h3>
                    <p class="text-gray-500">จัดการคำร้องทั้งหมดเรียบร้อยแล้ว</p>
                </div>

                <div v-else class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-gray-50 text-gray-600 uppercase font-medium border-b">
                            <tr>
                                <th class="px-6 py-4">วันที่สมัคร</th>
                                <th class="px-6 py-4">ชื่อ-นามสกุล</th>
                                <th class="px-6 py-4">ที่อยู่ / รหัสทะเบียนบ้าน</th>
                                <th class="px-6 py-4">เบอร์โทร</th>
                                <th class="px-6 py-4">สถานะ</th>
                                <th class="px-6 py-4 text-center">อนุมัติ/ปฏิเสธ</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            <tr v-for="user in pendingUsers" :key="user.id" class="hover:bg-gray-50 transition">
                                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                                    {{ user.created_at_formatted }} 
                                    </td>
                                <td class="px-6 py-4 font-medium text-brand-darkBlue cursor-pointer hover:underline"
                                    @click="openModal(user)" >
                                    {{ user.prefix }} {{ user.full_name }}
                                </td>
                                <td class="px-6 py-4">
                                    <p class="text-gray-800">{{ user.address }}</p>
                                    <p class="text-xs text-gray-400 mt-1">ID: {{ user.citizen_id }}</p>
                                </td>
                                <td class="px-6 py-4 text-gray-600">{{ user.phone }}</td>
                                <td class="px-6 py-4">
                                    <span 
                                        v-if="user.status === 'approved'" 
                                        class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs"
                                    >
                                         อนุมัติแล้ว
                                    </span>

                                    <span 
                                        v-else-if="user.status === 'rejected'" 
                                        class="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs"
                                    >
                                        ✖ ปฏิเสธแล้ว
                                    </span>

                                    <span 
                                        v-else
                                        class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-xs"
                                    >
                                         รออนุมัติ
                                    </span>
                                </td>

                                <td class="px-6 py-4 flex justify-center gap-2">

    <!--  แสดงปุ่มเฉพาะคำขอที่รออนุมัติ -->
    <template v-if="user.status === 'pending'">
        <button 
            @click="approveUser(user)"
            class="bg-green-100 text-green-700 hover:bg-green-600 hover:text-white px-3 py-1.5 rounded-lg transition font-medium text-xs flex items-center gap-1"
        >
            ✓ อนุมัติ
        </button>

        <button 
            @click="rejectUser(user)"
            class="bg-red-100 text-red-700 hover:bg-red-600 hover:text-white px-3 py-1.5 rounded-lg transition font-medium text-xs flex items-center gap-1"
        >
            ✕ ปฏิเสธ
        </button>
    </template>

    <!-- 🟢 แสดงข้อความเมื่ออนุมัติแล้ว -->
    <template v-else-if="user.status === 'approved'">
        <span class="text-green-700 bg-green-50 px-3 py-1 rounded-full text-xs">
            ✔ ดำเนินการแล้ว
        </span>
    </template>

    <!-- 🔴 แสดงข้อความเมื่อถูกปฏิเสธ -->
    <template v-else-if="user.status === 'rejected'">
        <span class="text-red-700 bg-red-50 px-3 py-1 rounded-full text-xs">
            ✖ ถูกปฏิเสธแล้ว
        </span>
    </template>

</td>

                            </tr>
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    </div>
    <!-- Modal Popup -->
    <div
        v-if="showModal && selectedUser"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
    >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 relative">

            <!-- ปุ่มปิด -->
            <button
                @click="closeModal"
                class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 text-xl font-bold"
            >
                ✕
            </button>

            <!-- หัวข้อ -->
            <h2 class="text-xl font-bold text-brand-darkBlue mb-4">
                ข้อมูลคำขอลงทะเบียน
            </h2>

            <!-- ข้อมูล -->
            <div class="space-y-3 text-sm text-gray-700">
                <div class="flex gap-2">
                    <span class="font-medium w-36">คำนำหน้า:</span>
                    <span>{{ selectedUser.prefix || '-' }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">ชื่อ-นามสกุล:</span>
                    <span>{{ selectedUser.full_name }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">วันเดือนปีเกิด:</span>
                    <span>{{ selectedUser.birth_date || '-' }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">เบอร์โทรศัพท์:</span>
                    <span>{{ selectedUser.phone }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">ที่อยู่:</span>
                    <span>{{ selectedUser.address }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">รหัสทะเบียนบ้าน:</span>
                    <span>{{ selectedUser.citizen_id }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">ชื่อเจ้าบ้าน:</span>
                    <span>{{ selectedUser.house_owner_name }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">ชื่อผู้ใช้งาน:</span>
                    <span>{{ selectedUser.username }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">วันที่สมัคร:</span>
                    <span>{{ selectedUser.created_at_formatted }}</span>
                </div>
                <div class="flex gap-2">
                    <span class="font-medium w-36">สถานะ:</span>
                    <span
                        :class="{
                            'text-green-600': selectedUser.status === 'approved',
                            'text-red-600': selectedUser.status === 'rejected',
                            'text-yellow-600': selectedUser.status === 'pending',
                        }"
                    >
                        {{
                            selectedUser.status === 'approved' ? 'อนุมัติแล้ว' :
                            selectedUser.status === 'rejected' ? 'ปฏิเสธแล้ว' : 'รออนุมัติ'
                        }}
                    </span>
                </div>
            </div>

            <!-- ช่องเหตุผลปฏิเสธ + ปุ่ม (เฉพาะ pending) -->
            <template v-if="selectedUser.status === 'pending'">
                <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        เหตุผลที่ปฏิเสธ (กรอกเมื่อต้องการปฏิเสธ)
                    </label>
                    <textarea
                        v-model="rejectReason"
                        rows="2"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-300"
                        placeholder="ระบุเหตุผล..."
                    />
                </div>
                <div class="flex gap-3 mt-4">
                    <button
                        @click="approveUser(selectedUser)"
                        class="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg font-medium text-sm transition"
                    >
                        ✓ อนุมัติ
                    </button>
                    <button
                        @click="rejectUser(selectedUser)"
                        class="flex-1 bg-red-500 hover:bg-red-600 text-white py-2 rounded-lg font-medium text-sm transition"
                    >
                        ✕ ปฏิเสธ
                    </button>
                </div>
            </template>

        </div>
    </div>
</template>