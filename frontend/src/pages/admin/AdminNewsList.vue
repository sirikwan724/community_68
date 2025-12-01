<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const newsList = ref([]);
const isLoading = ref(true);
const error = ref('');
const successMessage = ref('');

// ⭐ NEW: ฟังก์ชันนำทางกลับไปยัง Dashboard
const goToDashboard = () => {
    router.push('/admin/dashboard');
};

// ⭐ ฟังก์ชันดึงรายการข่าวสารทั้งหมด
const fetchAllNews = async () => {
    isLoading.value = true;
    error.value = '';
    
    try {
        // ดึงข่าวสารจาก Backend
        const res = await axios.get('http://localhost:8000/api/accounts/news/');
        newsList.value = res.data;
    } catch (err) {
        console.error('API Error:', err.response || err);
        error.value = 'ไม่สามารถดึงรายการข่าวสารได้: โปรดตรวจสอบ Backend Server';
    } finally {
        isLoading.value = false;
    }
};

//  ฟังก์ชันลบข่าวสาร
const deleteNews = async (newsId) => {
    if (!confirm('ยืนยันการลบข่าวสารนี้หรือไม่?')) {
        return;
    }

    const token = localStorage.getItem('access');
    if (!token) {
        alert('กรุณาเข้าสู่ระบบในฐานะแอดมิน');
        return;
    }

    try {
        await axios.delete(`http://localhost:8000/api/accounts/news/${newsId}/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        successMessage.value = '✅ ลบข่าวสารสำเร็จ!';
        await fetchAllNews(); 
        setTimeout(() => successMessage.value = '', 3000);

    } catch (err) {
        console.error('Delete Error:', err.response || err);
        error.value = '❌ เกิดข้อผิดพลาดในการลบข่าวสาร: ' + (err.response?.data?.detail || 'โปรดตรวจสอบสิทธิ์การเข้าถึง');
    }
};

onMounted(fetchAllNews);

// ⭐ ฟังก์ชันนำทางไปหน้าแก้ไข
const editNews = (newsId) => {
    router.push(`/admin/news/${newsId}/edit`);
};

// ⭐ ฟังก์ชันนำทางไปหน้าสร้างข่าว
const goToCreateNews = () => {
    router.push('/admin/news/create');
};
</script>

<template>
    <div class="p-6 max-w-7xl mx-auto">

        <div class="flex items-center justify-between mb-6">

            <!-- หัวข้อ -->
            <h1 class="text-3xl font-extrabold text-gray-800">
                ตารางจัดการข่าวประชาสัมพันธ์
            </h1>

            <!-- ปุ่มด้านขวา -->
            <div class="flex items-center gap-3">

                <button
                  @click="goToDashboard"
                  class="flex items-center bg-[#0F1A2C] text-white px-5 py-2 rounded-lg shadow hover:bg-[#152238] transition"
                >
                  กลับหน้าหลัก
                </button>

                <button
                  @click="goToCreateNews"
                  class="bg-[#0F1A2C] text-white px-5 py-2 rounded-lg shadow hover:bg-[#152238] transition"
                >
                  + สร้างข่าวสารใหม่
                </button>

            </div>
        </div> 
        <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
            {{ successMessage }}
        </div>
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
            {{ error }}
        </div>

        <div v-if="isLoading" class="text-center py-10 text-gray-500">
            กำลังโหลดข้อมูลข่าวสาร...
        </div>

        <div v-else class="bg-white shadow-lg rounded-lg overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/12">ID</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-6/12">หัวข้อข่าวสาร</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-3/12">วันที่เผยแพร่</th>
                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-2/12">จัดการ</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-if="newsList.length === 0">
                        <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                            ยังไม่มีข่าวสารในระบบ
                        </td>
                    </tr>
                    <tr v-for="news in newsList" :key="news.id" class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ news.id }}</td>
                        <td class="px-6 py-4 text-sm text-gray-800 font-semibold">{{ news.title }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ news.created_at_formatted }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium space-x-2">
                            <button @click="editNews(news.id)" class="text-indigo-600 hover:text-indigo-900 transition">
                                แก้ไข
                            </button>
                            <button @click="deleteNews(news.id)" class="text-red-600 hover:text-red-900 transition">
                                ลบ
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>