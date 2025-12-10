<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios"; // เพิ่ม axios เพื่อใช้เรียก API จริง

const router = useRouter();
const user = ref({});
const stats = ref({
  pendingUsers: 0,
  pendingEdits: 0,
  newReports: 0,
  todayBookings: 0
});

// ฟังก์ชันสำหรับดึงข้อมูลสถิติจาก Backend
const fetchStats = async () => {
    // ในโค้ดจริง แอดมินต้องเรียก API (เช่น /api/admin/dashboard/stats/)
    // เพื่อดึงตัวเลขการแจ้งเตือนต่างๆ มาใส่ใน stats.value
    
    // จำลองข้อมูลตัวเลขแจ้งเตือน (Mock Data)
    stats.value = {
      pendingUsers: 3, // รออนุมัติสมาชิกใหม่
      pendingEdits: 1, // รออนุมัติแก้ไขข้อมูล
      newReports: 5,   // เรื่องร้องเรียนใหม่
      todayBookings: 2 // รายการจองวันนี้
    };
}

onMounted(() => {
  // 1. โหลดข้อมูล Admin
  const userData = localStorage.getItem("user");
  if (userData) {
    user.value = JSON.parse(userData);
  }

  // 2. โหลดตัวเลขแจ้งเตือน
  fetchStats(); // เรียกใช้ฟังก์ชันดึงสถิติ
});

// ฟังก์ชันนำทางไปยังหน้าแสดงรายการข่าวสาร (ที่เราทำในขั้นตอนที่แล้ว)
const goToNewsList = () => {
    router.push('/admin/dashboard'); 
    // เนื่องจากเราใช้ AdminDashboard เป็นหน้าแสดงรายการข่าวด้วย
    // ถ้าคุณแยกหน้า NewsList ออกมา ควรเปลี่ยนเป็น router.push('/admin/news');
};
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <h1 class="text-3xl font-bold text-gray-800">
        ยินดีต้อนรับ, {{ user.full_name || user.username }} 
    </h1>

    <section>
        <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
             เมนูระบบ
        </h3>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            
            <router-link to="/admin/users/approve" class="admin-card group">

                <div class="text-center">
                    <h4 class="font-bold text-gray-800">อนุมัติสมาชิกใหม่</h4>
                    <p class="text-xs text-gray-500 mt-1">คำร้องขอเปิดบัญชี</p>
                </div>
                <!-- <span v-if="stats.pendingUsers > 0" class="badge bg-red-500">{{ stats.pendingUsers }}</span> -->
            </router-link>

            <router-link to="/admin/reports" class="admin-card group">

                <div class="text-center">
                    <h4 class="font-bold text-gray-800">จัดการเรื่องร้องเรียน</h4>
                    <p class="text-xs text-gray-500 mt-1">รับเรื่อง/อัปเดตสถานะ</p>
                </div>
                <!-- <span v-if="stats.newReports > 0" class="badge bg-red-500">{{ stats.newReports }}</span> -->
            </router-link>

            <!-- <router-link to="/admin/bookings" class="admin-card group">

                <div class="text-center">
                    <h4 class="font-bold text-gray-800">รายการยืม/จอง</h4>
                    <p class="text-xs text-gray-500 mt-1">อนุมัติการใช้งาน</p>
                </div>
            </router-link> -->
            
            <router-link to="/admin/helps" class="admin-card group">

                <div class="text-center">
                    <h4 class="font-bold text-gray-800">คำขออนุเคราะห์</h4>
                    <p class="text-xs text-gray-500 mt-1">อนุมัติการใช้งาน</p>
                </div>
            </router-link>

            <router-link to="/admin/appointments" class="admin-card group">

                <div class="text-center">
                    <h4 class="font-bold text-gray-800">ตารางการนัดหมาย</h4>
                    <p class="text-xs text-gray-500 mt-1">จัดการรายการนัดหมายทั้งหมด</p>
                </div>
            </router-link>

            <router-link to="/admin/services" class="admin-card group">
                <div class="text-center">
                    <h4 class="font-bold text-gray-800">บริการสาธารณะ</h4>
                    <p class="text-xs text-gray-500 mt-1">เพิ่ม/ลบ จุดให้บริการ</p>
                </div>
            </router-link>

            <router-link to="/admin/news-list" class="admin-card group">
                <div class="text-center">
                    <h4 class="font-bold text-gray-800">ข่าวประชาสัมพันธ์</h4>
                    <p class="text-xs text-gray-500 mt-1">จัดการ/โพสต์ข่าวสาร</p>
                </div>
            </router-link>
            <router-link to="/admin/stats" class="admin-card group">
                <div class="text-center">
                    <h4 class="font-bold text-gray-800">สถิติระบบ</h4>
                </div>                
            </router-link>

        </div>
    </section>

  </div>
</template>

<style scoped>
.admin-card {
    /* ใช้ @apply เพื่อรวม Tailwind classes */
    @apply relative bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all 
           border border-gray-100 hover:border-gray-300 hover:-translate-y-1 cursor-pointer
           flex flex-col items-center gap-4;
}

.icon-bg {
    @apply w-16 h-16 rounded-2xl flex items-center justify-center text-3xl transition-colors duration-300;
}

.badge {
    /* ปรับขนาด badge ให้เล็กลงและจัดตำแหน่งให้สวยขึ้น */
    @apply absolute top-3 right-3 text-white text-[11px] font-semibold px-2 py-0.5 rounded-full shadow-md;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
</style>