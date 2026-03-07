<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "@/services/api";
import VillageTab from "@/components/village/VillageTab.vue";
import VillageEditModal from "@/components/village/VillageEditModal.vue";

const villageData = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const fetchVillage = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/village/full/");
    villageData.value = res.data;
  } catch (e) {
    errorMsg.value = "ยังไม่มีข้อมูลหมู่บ้าน";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchVillage);

const sections = computed(() => {
  if (!villageData.value) return [];
  return villageData.value.sections ?? [];
});

// draft ที่แก้ได้
const draftSections = ref([]);
watch(sections, (val) => {
  if (!draftSections.value.length) {
    draftSections.value = val;
  }
}, { immediate: true });

// modal state
const showModal = ref(false);
const modalMode = ref("create");
const editingSection = ref(null);

const openCreate = () => {
  modalMode.value = "create";
  editingSection.value = null;
  showModal.value = true;
};

const openEdit = (sec) => {
  modalMode.value = "edit";
  editingSection.value = sec;
  showModal.value = true;
};

const handleSave = async (savedSection) => {
  try {
    // 1) create หรือ update section
    let sectionId = savedSection.id;

    if (modalMode.value === "create") {
      const payload = {
        type: savedSection.type,
        title: savedSection.title,
        content: savedSection.type === "RICH" ? (savedSection.content || []).join("\n") : "",
        description: savedSection.type === "PLACES" ? (savedSection.description || "") : "",
        order: 0,
      };

      const res = await api.post("/admin/village/sections/", payload);
      sectionId = res.data.id;
    } else {
      const payload = {
        type: savedSection.type,
        title: savedSection.title,
        content: savedSection.type === "RICH" ? (savedSection.content || []).join("\n") : "",
        description: savedSection.type === "PLACES" ? (savedSection.description || "") : "",
      };

      await api.patch(`/admin/village/sections/${sectionId}/`, payload);
    }

    // 2) TODO: อัปโหลดรูปไฟล์จริง (ทำในขั้นถัดไป)
    // - section images: POST /admin/village/sections/<id>/images/
    // - place images: POST /admin/village/places/<id>/images/

    // 3) โหลดใหม่จาก backend เพื่อให้ refresh แล้วไม่หาย
    await fetchVillage();

    alert("บันทึกข้อมูลลงฐานข้อมูลเรียบร้อย ✅");
  } catch (err) {
    console.error(err);
    alert("บันทึกไม่สำเร็จ");
  }
};

</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">จัดการข้อมูลหมู่บ้าน</h1>
      </div>

      <router-link
        to="/admin/dashboard"
        class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <div class="bg-white rounded-xl shadow p-6">
      <div v-if="loading">กำลังโหลดข้อมูล...</div>
      <div v-else-if="errorMsg" class="text-red-500">{{ errorMsg }}</div>

      <VillageTab
        v-else
        :sections="draftSections"
        :isAdmin="true"
        @create-section="openCreate"
        @edit-section="openEdit"
      />

      <VillageEditModal
        :open="showModal"
        :mode="modalMode"
        :initialSection="editingSection"
        @close="showModal = false"
        @save="handleSave"
      />
    </div>
  </div>
</template>