<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

// ⭐ ตัวแปรสำหรับเก็บข้อมูลฟอร์ม
const title = ref('');
const content = ref('');
const imageFile = ref(null);
const isLoading = ref(false);
const error = ref('');
const successMessage = ref('');

// ⭐ ฟังก์ชันนำทางกลับไปยัง Dashboard หลัก
const goToDashboard = () => {
    router.push('/admin/dashboard');
};

// ⭐ NEW: ฟังก์ชันยกเลิกและกลับไปหน้าก่อนหน้า
const cancelAndGoBack = () => {
    if (confirm('ยืนยันที่จะยกเลิกและละทิ้งข้อมูลที่กรอกหรือไม่?')) {
        // ใช้ router.back() เพื่อกลับไปหน้าจอก่อนหน้า
        router.back();
    }
};

// ⭐ ฟังก์ชันจัดการไฟล์รูปภาพ
const handleImageUpload = (event) => {
    imageFile.value = event.target.files[0];
};

// ⭐ ฟังก์ชันส่งฟอร์มไปยัง API
const submitNews = async () => {
    // 1. ตรวจสอบข้อมูลเบื้องต้น
    if (!title.value || !content.value) {
        error.value = 'กรุณาใส่หัวข้อและเนื้อหาข่าวให้ครบถ้วน';
        return;
    }

    // 2. สร้าง FormData (จำเป็นสำหรับส่งไฟล์และข้อความพร้อมกัน)
    const formData = new FormData();
    formData.append('title', title.value);
    formData.append('content', content.value);
    if (imageFile.value) {
        formData.append('image', imageFile.value);
    }
    
    // 3. ดึง Token เพื่อยืนยันตัวตน (Admin)
    const token = localStorage.getItem('access');
    if (!token) {
        error.value = 'ไม่พบสิทธิ์การเข้าถึง กรุณาเข้าสู่ระบบใหม่';
        return;
    }

    isLoading.value = true;
    error.value = '';
    successMessage.value = '';

    try {
        // 4. ส่ง POST Request ไปยัง API
        const response = await axios.post(
            'http://localhost:8000/api/accounts/news/',
            formData,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        // 5. หากสำเร็จ
        successMessage.value = '✅ สร้างข่าวสารสำเร็จ! ระบบจะนำกลับไปหน้าตารางข่าวสารใน 3 วินาที';
        
        // เคลียร์ฟอร์ม
        title.value = '';
        content.value = '';
        imageFile.value = null;

        // นำทางกลับไปหน้าตารางข่าวสารอัตโนมัติ
        setTimeout(() => {
            router.push('/admin/news-list');
        }, 3000);

    } catch (err) {
        console.error('API Error:', err.response || err);
        error.value = '❌ เกิดข้อผิดพลาดในการสร้างข่าวสาร: ' + (err.response?.data?.detail || 'โปรดตรวจสอบ Server');
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div class="max-w-3xl mx-auto p-6 bg-white shadow-xl rounded-xl mt-10">
        
        <div class="flex items-center justify-start mb-4">
            <button @click="goToDashboard" class="text-sm text-indigo-600 hover:text-indigo-800 transition flex items-center">
                กลับหน้าหลัก
            </button>
        </div>

        <h2 class="text-3xl font-extrabold text-blue-700 mb-6 border-b pb-3">
            สร้างประกาศ/ข่าวสารใหม่
        </h2>

        <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
            {{ successMessage }}
        </div>
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
            {{ error }}
        </div>

        <form @submit.prevent="submitNews" class="space-y-6">
            
            <div>
                <label for="title" class="block text-sm font-medium text-gray-700">หัวข้อข่าวสาร</label>
                <input 
                    type="text" 
                    id="title" 
                    v-model="title" 
                    required 
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="เช่น: ประกาศเรื่องน้ำประปาจะหยุดไหลวันที่..."
                />
            </div>

            <div>
                <label for="content" class="block text-sm font-medium text-gray-700">รายละเอียดเนื้อหา</label>
                <textarea 
                    id="content" 
                    v-model="content" 
                    rows="6" 
                    required 
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="ระบุรายละเอียดทั้งหมด"
                ></textarea>
            </div>

            <div>
                <label for="image" class="block text-sm font-medium text-gray-700">รูปภาพประกอบ (ถ้ามี)</label>
                <input 
                    type="file" 
                    id="image" 
                    accept="image/*" 
                    @change="handleImageUpload" 
                    class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                <p v-if="imageFile" class="mt-2 text-sm text-gray-500">
                    ไฟล์ที่เลือก: {{ imageFile.name }}
                </p>
            </div>

            <div class="flex space-x-4 pt-4">
                 <button 
                    type="button" 
                    @click="cancelAndGoBack"
                    class="flex-1 flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-lg font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300 transition"
                >
                     ยกเลิก
                </button>
                <button 
                    type="submit" 
                    :disabled="isLoading"
                    class="flex-1 flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 transition"
                >
                    <span v-if="isLoading" class="flex items-center">
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        กำลังสร้าง...
                    </span>
                    <span v-else> ประกาศข่าวสาร</span>
                </button>
            </div>
        </form>
    </div>
</template>