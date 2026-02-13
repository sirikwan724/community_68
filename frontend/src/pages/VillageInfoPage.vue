<script setup>
import { ref, computed } from "vue";
import VillageTab from "@/components/village/VillageTab.vue";
import LeaderTab from "@/components/village/LeaderTab.vue";
import FundTab from "@/components/village/FundTab.vue";

const activeTab = ref("village");

// ตรวจสอบสิทธิ์จากระบบจริง
const isAuthenticated = computed(() => {
  return !!localStorage.getItem("access");
});

const isAdmin = computed(() => {
  return localStorage.getItem("role") === "admin";
});

const tabs = computed(() => {
  const list = [
    { key: "village", label: "ข้อมูลหมู่บ้าน" },
    { key: "leader", label: "โปรไฟล์ผู้นำ" },
  ];

  if (isAuthenticated.value) {
    list.push({ key: "fund", label: "ข้อมูลกองทุน" });
  }

  return list;
});
</script>

<template>
  <div class="max-w-5xl mx-auto p-6 bg-white rounded-xl shadow">

    <!-- หัวข้อหน้า -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">
        ข้อมูลชุมชน
      </h1>

      <router-link
        to="/"
        class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <!-- TAB -->
    <div class="flex gap-6 border-b mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="pb-2 font-medium"
        :class="activeTab === tab.key
          ? 'border-b-2 border-blue-500 text-blue-600'
          : 'text-gray-500 hover:text-blue-500'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- CONTENT -->
    <div class="space-y-6">

      <VillageTab
        v-if="activeTab === 'village'"
        :isAdmin="isAdmin"
      />

      <LeaderTab
        v-if="activeTab === 'leader'"
        :isAdmin="isAdmin"
      />

      <FundTab
        v-if="activeTab === 'fund'"
        :isAdmin="isAdmin"
      />

    </div>
  </div>
</template>
