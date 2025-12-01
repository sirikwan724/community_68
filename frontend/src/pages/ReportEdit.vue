<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const id = route.params.id;

const category = ref("");
const description = ref("");
const area = ref("");
const image = ref(null);
const status = ref("");

const loading = ref(true);
const error = ref("");

onMounted(async () => {
    try {
        const token = localStorage.getItem("access");
        //  frontend ยิงข้อมูลไปที่
        const res = await axios.get(`http://localhost:8000/api/reports/${id}/`, 
        { 
            headers: { Authorization: `Bearer ${token}` }
        });

        if (res.data.status !== "pending") {
            error.value = "รายงานนี้ถูกผู้ใหญ่บ้านรับเรื่องแล้ว คุณไม่สามารถแก้ไขได้";
            return;
        }

        category.value = res.data.category;
        description.value = res.data.description;
        area.value = res.data.area;
        status.value = res.data.status;

    } catch (err) {
        console.error(err);
        error.value = "ไม่พบรายงานนี้";
    } finally {
        loading.value = false;
    }
});

const submitEdit = async () => {
    const token = localStorage.getItem("access");

    const formData = new FormData();
    formData.append("category", category.value);
    formData.append("description", description.value);
    formData.append("area", area.value);
    if (image.value) formData.append("image", image.value);

    await axios.put(`http://localhost:8000/api/reports/${route.params.id}/`, formData, {
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
        }
    });

    alert("แก้ไขรายงานสำเร็จ");
    router.push("/report/list");
};
</script>

<template>
    <div class="p-6 max-w-xl mx-auto">

        <h1 class="text-2xl font-bold mb-4">แก้ไขรายงาน</h1>

        <div v-if="loading">กำลังโหลดข้อมูล...</div>
        <div v-if="error" class="text-red-600">{{ error }}</div>

        <form v-if="!error" @submit.prevent="submitEdit" class="space-y-4">

            <div>
                <label class="font-bold">หัวข้อปัญหา</label>
                <select v-model="category" class="w-full border p-2 rounded">
                    <option value="ไฟฟ้า">ไฟฟ้า</option>
                    <option value="น้ำ">น้ำ</option>
                    <option value="ถนน">ถนน</option>
                    <option value="บุคคล">บุคคล</option>
                    <option value="เสียง">เสียง</option>
                    <option value="กลิ่น">กลิ่น</option>
                </select>
            </div>

            <div>
                <label class="font-bold">รายละเอียด</label>
                <textarea v-model="description" class="w-full border p-2 rounded"></textarea>
            </div>

            <div>
                <label class="font-bold">พื้นที่/บริเวณ</label>
                <input v-model="area" class="w-full border p-2 rounded" />
            </div>

            <div>
                <label class="font-bold">อัปโหลดภาพใหม่ (ถ้ามี)</label>
                <input type="file" @change="e => image.value = e.target.files[0]" />
            </div>

            <button class="px-4 py-2 bg-blue-600 text-white rounded">
                บันทึกการแก้ไข
            </button>
        </form>

    </div>
</template>
