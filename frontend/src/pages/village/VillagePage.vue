<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

import VillageTab from "@/components/village/VillageTab.vue";
import LeaderTab from "@/components/village/LeaderTab.vue";
import FundTab from "@/components/village/FundTab.vue";
import VillageMap from "@/components/village/VillageMap.vue";

const router = useRouter();

const isLoggedIn = computed(() => !!localStorage.getItem("access"));

const activeTab = ref("overview");

const villageData = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const tabs = computed(() => {
  const base = [
    { key: "overview", label: "ชุมชนบ้านสร้างขุนศรี" },
    { key: "leader", label: "บอร์ดหมู่บ้าน" },
  ];

  if (isLoggedIn.value) {
    base.push({ key: "fund", label: "กองทุนหมู่บ้าน" });
  }

  return base;
});

const fetchVillage = async () => {
  loading.value = true;
  try {
    const res = await api.get("/village/full/");
    villageData.value = res.data;
  } catch (e) {
    errorMsg.value = "ยังไม่มีข้อมูลหมู่บ้าน";
  } finally {
    loading.value = false;
  }
};

const sections = computed(() => villageData.value?.sections ?? []);
const overview = computed(() => villageData.value?.overview ?? {}); //เป็นส่วนของ overview ข้อมูลหมู่บ้านและพิกัด กับ sectionsที่เป็นหัวข้อต่างๆ เพราะฉะนั้นต้องทำการดึง overview ออกมาเพื่อที่จะเอาพิกัดไปแสดงบนแผนที่

onMounted(fetchVillage);
</script>

<template>
  <div class="min-h-screen bg-brand-softYellow">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-5xl mx-auto bg-white rounded-xl shadow border p-6">

        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-3xl font-bold text-brand-darkBlue">ข้อมูลหมู่บ้าน</h1>
          <button
            class="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200"
            @click="router.push('/')"
          >
            กลับหน้าหลัก
          </button>
        </div>

        <!-- Tabs -->
        <div class="border-b mb-6 flex gap-6">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="pb-3 text-sm font-medium"
            :class="activeTab === t.key ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'"
            @click="activeTab = t.key"
          >
            {{ t.label }}
          </button>
        </div>

        <!-- Content -->
        <div v-if="loading">กำลังโหลดข้อมูล...</div>
        <div v-else-if="errorMsg" class="text-red-500">{{ errorMsg }}</div>

        <div v-if="activeTab === 'overview'">
          <div class="mb-8">
            <h2 class="text-lg font-semibold text-gray-700 mb-3">ที่ตั้งหมู่บ้าน</h2>
            <VillageMap
              :latitude="overview.latitude"
              :longitude="overview.longitude"
              :villageName="overview.name"
              height="340px"
            />
          </div>
          <VillageTab :sections="sections" :isAdmin="false" />
        </div>

        <LeaderTab
          v-else-if="activeTab === 'leader'"
        />

        <FundTab
          v-else-if="activeTab === 'fund'"
        />

      </div>
    </div>
  </div>
</template> 
