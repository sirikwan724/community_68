<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
// ⭐ 1. Import useRouter เพื่อใช้ในการเปลี่ยนเส้นทาง (ถ้าจำเป็น)
import { useRouter } from "vue-router";

const pendingUsers = ref([]);
const loading = ref(true);
const error = ref(null);
const router = useRouter(); 

// ⭐ 2. ฟังก์ชันเรียก API ดึงคำขอลงทะเบียน
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
        // ⭐ API Call จริง: ดึงข้อมูลจาก Backend ที่เราสร้างไว้
        const res = await axios.get(
            "http://localhost:8000/api/accounts/admin/requests/all/", 
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        
        // ⭐ 3. ข้อมูลที่ได้จะถูกเก็บไว้ใน pendingUsers
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
        
        // ลบออกจากรายการหน้าจอ และดึงข้อมูลใหม่ (หรือแค่ลบออกจาก list ก็ได้)
        pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id);
        alert("✅ อนุมัติเรียบร้อย และสร้างบัญชีผู้ใช้แล้ว");
    } catch (err) {
        console.error("Approve Error:", err);
        alert("เกิดข้อผิดพลาดในการอนุมัติ: " + (err.response?.data?.detail || "กรุณาตรวจสอบ Console"));
    }
};

// ฟังก์ชันปฏิเสธ
const rejectUser = async (user) => {
    const reason = prompt("กรุณาระบุเหตุผลที่ไม่อนุมัติ:");
    if (!reason) return;

    const token = localStorage.getItem('access');
    try {
        // API Call จริง: POST /api/accounts/admin/requests/{id}/reject/
        await axios.post(
            `http://localhost:8000/api/accounts/admin/requests/${user.id}/reject/`,
            { reason: reason }, // ส่งเหตุผลไป Backend
            { headers: { Authorization: `Bearer ${token}` } }
        );

        pendingUsers.value = pendingUsers.value.filter(u => u.id !== user.id);
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
                <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    คำขอลงทะเบียนผู้ใช้ใหม่
                </h1>
                <router-link 
                   to="/admin/dashboard"
                   class="bg-brand-darkBlue text-white px-4 py-2 rounded-lg shadow hover:bg-blue-800 transition"
                >
                   กลับหน้าหลัก
                </router-link>
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
                                <th class="px-6 py-4">ที่อยู่ / บัตร ปชช.</th>
                                <th class="px-6 py-4">เบอร์โทร</th>
                                <th class="px-6 py-4">สถานะ</th>
                                <th class="px-6 py-4 text-center">จัดการ</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            <tr v-for="user in pendingUsers" :key="user.id" class="hover:bg-gray-50 transition">
                                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                                    {{ new Date(user.id * 1000).toLocaleDateString('th-TH') }} 
                                    </td>
                                <td class="px-6 py-4 font-medium text-gray-900">
                                    {{ user.full_name }} </td>
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

    <!-- 🌟 แสดงปุ่มเฉพาะคำขอที่รออนุมัติ -->
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
</template>