<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute(); // เพื่อดึงค่า id จาก URL
const router = useRouter();
const newsId = ref(route.params.id); // ID ของข่าวสารที่ต้องการแก้ไข

// ⭐ ตัวแปรสำหรับเก็บข้อมูลฟอร์ม
const title = ref("");
const content = ref("");
const existingImageUrl = ref(""); // URL รูปภาพเดิม
const imageFile = ref(null); // ไฟล์รูปภาพใหม่
const isLoading = ref(false);
const isFetching = ref(true); // สถานะกำลังดึงข้อมูลเดิม
const error = ref("");
const successMessage = ref("");

// ⭐ ฟังก์ชันย้อนกลับไปยังหน้าก่อนหน้า (AdminNewsList)
const goBack = () => {
    // router.back() จะย้อนไปหน้าล่าสุดใน history
    // หากต้องการย้อนกลับไปหน้าจัดการข่าวสารโดยตรง (เช่น /admin/news)
    // สามารถใช้ router.push('/admin/news') แทนได้
    router.back(); 
};

// ⭐ 1. ฟังก์ชันดึงข้อมูลข่าวสารเดิม
const fetchNewsData = async () => {
    isFetching.value = true;
    error.value = '';
    
    try {
        const res = await axios.get(`http://localhost:8000/api/accounts/news/${newsId.value}/`);
        
        // กำหนดค่าให้ฟอร์ม
        title.value = res.data.title;
        content.value = res.data.content;
        existingImageUrl.value = res.data.image;

    } catch (err) {
        console.error("API Error:", err.response || err);
        error.value = "ไม่สามารถดึงข้อมูลข่าวสารนี้ได้: " + (err.response?.data?.detail || "โปรดตรวจสอบ ID หรือ Server");
    } finally {
        isFetching.value = false;
    }
};

// ⭐ 2. ฟังก์ชันจัดการไฟล์รูปภาพ
const handleImageUpload = (event) => {
    imageFile.value = event.target.files[0];
};

// ⭐ 3. ฟังก์ชันส่งฟอร์มเพื่ออัปเดต (ใช้ PUT/PATCH)
const updateNews = async () => {
    if (!title.value || !content.value) {
        error.value = 'กรุณาใส่หัวข้อและเนื้อหาข่าวให้ครบถ้วน';
        return;
    }

    const formData = new FormData();
    formData.append('title', title.value);
    formData.append('content', content.value);
    
    // 💡 ถ้ามีการเลือกรูปภาพใหม่ ให้แนบไฟล์ไปด้วย
    if (imageFile.value) {
        formData.append('image', imageFile.value);
    }
    // 💡 ถ้าไม่ได้เลือกไฟล์ใหม่ ไม่ต้องแนบ image ไป (ใช้รูปเดิม)

    const token = localStorage.getItem('access');
    if (!token) {
        error.value = 'ไม่พบสิทธิ์การเข้าถึง กรุณาเข้าสู่ระบบใหม่';
        return;
    }

    isLoading.value = true;
    error.value = '';
    successMessage.value = '';

    try {
        const response = await axios.patch(
            // ⭐ URL ถูกต้องแล้ว: มีสแลชปิดท้าย
            `http://localhost:8000/api/accounts/news/${newsId.value}/`, 
            formData,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            }
        );

        successMessage.value = '✅ แก้ไขข่าวสารสำเร็จ!';
        // อัปเดต URL รูปภาพเดิมหากมีการเปลี่ยน
        if (response.data.image) {
            existingImageUrl.value = response.data.image;
            imageFile.value = null; // ล้างไฟล์ที่เลือกไว้
        }

    } catch (err) {
        console.error('API Error:', err.response || err);
        error.value = '❌ เกิดข้อผิดพลาดในการแก้ไขข่าวสาร: ' + (err.response?.data?.detail || 'โปรดตรวจสอบ Server');
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchNewsData);
</script>

<template>
    <div class="max-w-3xl mx-auto p-6 bg-white shadow-xl rounded-xl mt-10">
        <div class="flex justify-between items-center mb-6 border-b pb-3">
            <h2 class="text-3xl font-extrabold text-indigo-700">
                 แก้ไขข่าวสาร 
            </h2>
            <button 
                @click="goBack"
                class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800 transition p-2 rounded-lg bg-indigo-50 hover:bg-indigo-100"
            >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                กลับหน้าก่อนหน้า
            </button>
        </div>

        <div v-if="isFetching" class="text-center py-10 text-gray-500">
            กำลังโหลดข้อมูลเดิม...
        </div>

        <div v-else>
            <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
                {{ successMessage }}
            </div>
            <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                {{ error }}
            </div>

            <form @submit.prevent="updateNews" class="space-y-6">
                
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700">หัวข้อข่าวสาร</label>
                    <input 
                        type="text" 
                        id="title" 
                        v-model="title" 
                        required 
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                </div>

                <div>
                    <label for="content" class="block text-sm font-medium text-gray-700">รายละเอียดเนื้อหา</label>
                    <textarea 
                        id="content" 
                        v-model="content" 
                        rows="6" 
                        required 
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500"
                    ></textarea>
                </div>

                <div class="space-y-3">
                    <label class="block text-sm font-medium text-gray-700">รูปภาพประกอบ</label>

                    <div v-if="existingImageUrl" class="mb-4">
                        <p class="text-xs text-gray-500 mb-2">รูปภาพปัจจุบัน:</p>
                        <img :src="existingImageUrl" class="w-32 h-32 object-cover rounded-lg shadow-md border" alt="Current Image">
                    </div>

                    <div>
                        <p class="text-xs text-gray-500 mb-2">อัปโหลดรูปภาพใหม่เพื่อแทนที่:</p>
                        <input 
                            type="file" 
                            id="image" 
                            accept="image/*" 
                            @change="handleImageUpload" 
                            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                        />
                        <p v-if="imageFile" class="mt-2 text-sm text-gray-500">
                            ไฟล์ใหม่ที่เลือก: {{ imageFile.name }}
                        </p>
                    </div>
                </div>

                <button 
                    type="submit" 
                    :disabled="isLoading"
                    class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 transition"
                >
                    <span v-if="isLoading" class="flex items-center">
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        กำลังอัปเดต...
                    </span>
                    <span v-else> บันทึกการแก้ไขข่าวสาร</span>
                </button>
            </form>
        </div>
    </div>
</template>