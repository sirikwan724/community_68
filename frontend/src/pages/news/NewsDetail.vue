<template>
  <div class="min-h-screen bg-brand-softYellow py-10 px-4">
    <div class="max-w-4xl mx-auto bg-white shadow-md rounded-xl p-8">

      <!-- รูปภาพข่าว -->
      <div v-if="news.image" class="w-full mb-6">
        <img
          :src="news.image"
          class="w-full h-72 object-cover rounded-lg shadow"
        />
      </div>

      <!-- หัวข้อข่าว -->
      <h1 class="text-3xl font-extrabold text-brand-darkBlue mb-4">
        {{ news.title }}
      </h1>

      <!-- วันที่ -->
      <div class="text-sm text-gray-500 mb-6">
        เผยแพร่เมื่อ: {{ news.created_at }}
      </div>

      <!-- เนื้อหา -->
      <p class="text-gray-700 leading-relaxed whitespace-pre-line text-lg">
        {{ news.content }}
      </p>

      <!-- ปุ่มย้อนกลับ -->
      <div class="mt-10">
        <router-link
          to="/"
          class="inline-block px-5 py-2 bg-brand-darkBlue text-white rounded-lg shadow hover:bg-blue-900 transition"
        >
          ← กลับไปหน้าข่าวสาร
        </router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const route = useRoute();
const news = ref({});

onMounted(async () => {
  const id = route.params.id;
  try {
    const res = await axios.get(`http://localhost:8000/api/accounts/news/${id}/`);
    news.value = res.data;
  } catch (err) {
    console.error("โหลดข่าวไม่สำเร็จ", err);
  }
});
</script>

<style scoped>
/* ใช้แบรนด์สีของคุณ */
.bg-brand-softYellow {
  background-color: #faf7dc;
}
.text-brand-darkBlue {
  color: #243b53;
}
</style>
