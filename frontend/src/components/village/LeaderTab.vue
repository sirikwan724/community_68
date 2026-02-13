<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";
import ProfileCard from "@/components/village/ProfileCard.vue";

const profiles = ref([]);
const loading = ref(false);
const errorMsg = ref("");

// โหลดข้อมูลโปรไฟล์ทั้งหมด
const fetchProfiles = async () => {
  loading.value = true;
  try {
    const res = await api.get("/village/profiles/");
    console.log("PROFILE DATA:", res.data);
    profiles.value = res.data;
  } catch (err) {
    console.error("ERROR:", err);
    errorMsg.value = "ไม่สามารถโหลดข้อมูลผู้นำและคณะกรรมการได้";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchProfiles);

// =========================
// แยกข้อมูลตามกลุ่ม
// =========================
const leaders = computed(() =>
  profiles.value.filter(p => p.group === "leader")
);

const committees = computed(() =>
  profiles.value.filter(p => p.group === "committee")
);

const volunteers = computed(() =>
  profiles.value.filter(p => p.group === "volunteer")
);

// helper แปลงตำแหน่ง
const positionLabel = (pos) => {
  if (pos === "president") return "ประธาน";
  if (pos === "vice") return "รองประธาน";
  return "สมาชิก";
};
</script>

<template>
  <div class="space-y-10">

    <!-- Loading / Error -->
    <div v-if="loading" class="text-gray-500">
      กำลังโหลดข้อมูล...
    </div>

    <div v-else-if="errorMsg" class="text-red-500">
      {{ errorMsg }}
    </div>

    <!-- =========================
         ผู้นำชุมชน
    ========================== -->
    <section v-if="leaders.length">
      <h2 class="text-xl font-semibold mb-4">ผู้นำชุมชน</h2>

      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProfileCard
          v-for="p in leaders"
          :key="p.id"
          :profile="p"
          :is-admin="false"
        />
      </div>
    </section>

    <!-- =========================
         คณะกรรมการหมู่บ้าน
    ========================== -->
    <section v-if="committees.length">
      <h2 class="text-xl font-semibold mb-4">คณะกรรมการหมู่บ้าน</h2>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <ProfileCard
          v-for="p in committees"
          :key="p.id"
          :profile="p"
          :is-admin="false"
        />
      </div>
    </section>

    <!-- =========================
         อสม.
    ========================== -->
    <section v-if="volunteers.length">
      <h2 class="text-xl font-semibold mb-4">อสม.</h2>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <ProfileCard
          v-for="p in volunteers"
          :key="p.id"
          :profile="p"
          :is-admin="false"
        />
      </div>
    </section>

    <!-- กรณีไม่มีข้อมูลเลย -->
    <div
      v-if="!loading && profiles.length === 0"
      class="text-gray-500"
    >
      ยังไม่มีข้อมูลผู้นำ คณะกรรมการ หรืออสม.
    </div>

  </div>
</template>
