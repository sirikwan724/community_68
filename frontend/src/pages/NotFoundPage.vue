<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50 text-center p-6">
    <h1 class="text-9xl font-extrabold text-brand-softYellow drop-shadow-sm">404</h1>
    <h2 class="text-3xl font-bold text-brand-darkBlue mt-4">ขออภัย ไม่พบหน้านี้</h2>
    <p class="text-gray-500 mt-2 text-lg">หน้าที่คุณกำลังค้นหาอาจถูกย้ายหรือไม่มีอยู่จริง</p>
    
    <router-link 
      to="/" 
      class="mt-8 px-8 py-3 bg-brand-darkBlue text-white rounded-xl shadow-lg hover:bg-brand-dark transition transform active:scale-95"
    >
      กลับหน้าหลัก
    </router-link>
  </div>
</template>

<script setup>
// ไม่ต้องมี Logic อะไร
</script>