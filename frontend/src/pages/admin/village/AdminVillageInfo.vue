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
  draftSections.value = val;
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

const handleSave = async ({ section, sectionFiles, places }) => {
  try {
    let sectionId = section.id;

    // create / update section
    if (modalMode.value === "create") {
      const payload = {
        type: section.type,
        title: section.title,
        content: section.type === "RICH" ? (section.content || []).join("\n") : "",
        description: section.type === "PLACES" ? (section.description || "") : "",
        order: 0,
      };
      const res = await api.post("/admin/village/sections/", payload);
      sectionId = res.data.id;
    } else {
      const payload = {
        type: section.type,
        title: section.title,
        content: section.type === "RICH" ? (section.content || []).join("\n") : "",
        description: section.type === "PLACES" ? (section.description || "") : "",
      };
      await api.patch(`/admin/village/sections/${sectionId}/`, payload);
    }

    // upload รูปของหัวข้อ (section)
    if (sectionFiles?.length) {
      const fd = new FormData();
      sectionFiles.forEach((f) => fd.append("images", f));
      await api.post(`/admin/village/sections/${sectionId}/images/`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    }

    // ถ้าเป็น PLACES: สร้างสถานที่ + upload รูปสถานที่
    if (section.type === "PLACES") {
        // ถ้าเป็นโหมดแก้ไข: ลบสถานที่เดิมของ section นี้ก่อน (กันซ้ำ)
      if (modalMode.value === "edit") {
        const oldPlaces = editingSection.value?.places || [];
        for (const old of oldPlaces) {
          await api.delete(`/admin/village/places/${old.id}/`);
        }
      }

      for (const p of (places || [])) {
        const placeRes = await api.post(`/admin/village/sections/${sectionId}/places/`, {
          name: p.name,
          detail: p.detail,
          order: 0,
        });
        const placeId = placeRes.data.id;

        if (p.files?.length) {
          const fd = new FormData();
          p.files.forEach((f) => fd.append("images", f));
          await api.post(`/admin/village/places/${placeId}/images/`, fd, {
            headers: { "Content-Type": "multipart/form-data" },
          });
        }
      }
    }

    // reload
    await fetchVillage();
    showModal.value = false;
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
      <div class="flex items-center gap-3">
        <button
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          @click="openCreate"
        >
          + เพิ่มหัวข้อ
        </button>

        <router-link
          to="/admin/dashboard"
          class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
        >
          กลับหน้าหลัก
        </router-link>
      </div>
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