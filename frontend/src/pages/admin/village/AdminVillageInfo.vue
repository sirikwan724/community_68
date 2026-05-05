<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "@/services/api";
import VillageTab from "@/components/village/VillageTab.vue";
import VillageEditModal from "@/components/village/VillageEditModal.vue";
import AdminVillageMapEditor from "./AdminVillageMapEditor.vue";

const villageData = ref(null);
const loading = ref(false);
const errorMsg = ref("");

const mapLat = ref(null);
const mapLng = ref(null); //เก็บพิกัดที่ Admin คลิกเลือกบนแผนที่
const savingLocation = ref(false); //	ติดตามว่ากำลังบันทึกอยู่หรือเปล่า (ป้องกันการกดซ้ำ)
const locationMsg = ref(""); //แสดงข้อความสำเร็จหรือ error หลังบันทึก

const fetchVillage = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/village/full/");
    villageData.value = res.data;
    mapLat.value = res.data?.overview?.latitude ?? null;
    mapLng.value = res.data?.overview?.longitude ?? null; //ดึงพิกัดเดิมจาก overview มาแสดงบนแผนที่จะได้ไม่ต้องตั้งพิกัดใหม่ทุกครั้งที่เข้าหน้ามา
  } catch (e) {
    errorMsg.value = "ยังไม่มีข้อมูลหมู่บ้าน";
  } finally {
    loading.value = false;
  }
};

const deleteSection = async (sec) => {
  if (!confirm(`ต้องการลบหัวข้อ "${sec.title}" ใช่ไหม?`)) return;
  try {
    await api.delete(`/admin/village/sections/${sec.id}/`);
    await fetchVillage();
  } catch {
    alert("ลบหัวข้อไม่สำเร็จ");
  }
};

const saveLocation = async () => {
  if (!mapLat.value || !mapLng.value) {
    locationMsg.value = "กรุณาคลิกบนแผนที่เพื่อเลือกพิกัดก่อน";
    return;
  }
  savingLocation.value = true;
  locationMsg.value = "";
  try {
    await api.patch("/admin/village/location/", {
      latitude: mapLat.value,
      longitude: mapLng.value,
    });
    locationMsg.value = "✅ บันทึกพิกัดสำเร็จ";
  } catch (e) {
    locationMsg.value = "❌ บันทึกพิกัดไม่สำเร็จ";
  } finally {
    savingLocation.value = false;
  }
};
// เมื่อAdminคลิกย้าย marker บนแผนที่ พิกัดยังจะแค่เก็บอยู่ใน mapLat และ mapLng ในหน้าจอเท่านั้น ยังไม่ได้บันทึกลง Database จริง
// ฟังก์ชันนี้คือตัวที่ส่งพิกัดไปบันทึกลง Database โดยผ่าน API PATCH /admin/village/location/

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

const handleSave = async ({ section, existingImages, sectionItems, places }) => {
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

    // อัปเดต caption ของรูปเก่า (RICH)
    if (section.type === "RICH" && existingImages?.length) {
      for (const img of existingImages) {
        await api.patch(`/admin/village/section-images/${img.id}/`, { caption: img.caption });
      }
    }

    // upload รูปใหม่ทีละรูปพร้อม caption (RICH)
    if (section.type === "RICH" && sectionItems?.length) {
      for (const item of sectionItems) {
        const fd = new FormData();
        fd.append("image", item.file);
        fd.append("caption", item.caption || "");
        await api.post(`/admin/village/sections/${sectionId}/images/`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
    }

    // PLACES: ลบเก่า + สร้างใหม่
    if (section.type === "PLACES") {
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

    <!-- แผนที่ตั้งพิกัดหมู่บ้าน -->
    <div class="bg-white rounded-xl shadow p-6 mb-6 isolate">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">ที่ตั้งของชุมชนหมู่บ้าน (แก้ไขพิกัดหมู่บ้าน)</h2>
      <AdminVillageMapEditor
        :latitude="mapLat"
        :longitude="mapLng"
        :villageName="villageData?.overview?.name"
        @update:latitude="mapLat = $event"
        @update:longitude="mapLng = $event"  
      /> <!-- เมื่อ Admin คลิกย้าย marker แผนที่จะส่งพิกัดใหม่มา แล้วนำไปเก็บไว้ใน mapLat และ mapLng เพื่อใช้ในการบันทึก -->
      <div class="mt-4 flex items-center gap-4">
        <button
          class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          :disabled="savingLocation"
          @click="saveLocation"
        >
          {{ savingLocation ? "กำลังบันทึก..." : "บันทึกพิกัด" }}
        </button>
        <span v-if="locationMsg" class="text-sm">{{ locationMsg }}</span>
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
        @delete-section="deleteSection"
        @refresh="fetchVillage"
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