<template>
  <div class="max-w-6xl mx-auto">

    <!-- Header -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">
          โครงสร้างผู้นำหมู่บ้าน
        </h1>
        <p class="text-gray-500 text-sm">
          เพิ่ม แก้ไข หรือลบโปรไฟล์ผู้นำ กรรมการ และ อสม.
        </p>
      </div>

      <div class="flex gap-3">
        <router-link
          to="/admin/dashboard"
          class="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300"
        >
          กลับหน้าหลัก
        </router-link>

        <router-link
          to="/admin/profiles/create"
          class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
        >
          + เพิ่มโปรไฟล์
        </router-link>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-10 text-gray-500">
      กำลังโหลดข้อมูล...
    </div>

    <!-- No Data -->
    <div v-else-if="profiles.length === 0" class="text-center py-10 text-gray-400">
      ยังไม่มีข้อมูลโปรไฟล์
    </div>

    <div v-else>

      <!-- ================== ผู้นำ ================== -->
      <div v-if="leaders.length">
        <h2 class="text-xl font-bold mt-6 mb-4 text-center">
          ผู้นำชุมชน
        </h2>

        <div class="grid md:grid-cols-3 gap-6">
          <ProfileCard
            v-for="profile in leaders"
            :key="profile.id"
            :profile="profile"
            @delete="deleteProfile"
          />
        </div>
      </div>

      <!-- ================== คณะกรรมการ ================== -->
      <div v-if="committees.length">
        <h2 class="text-xl font-bold mt-10 mb-4 text-center">
          คณะกรรมการ
        </h2>

        <div class="grid md:grid-cols-3 gap-6">
          <ProfileCard
            v-for="profile in committees"
            :key="profile.id"
            :profile="profile"
            @delete="deleteProfile"
          />
        </div>
      </div>

      <!-- ================== อสม ================== -->
      <div v-if="volunteers.length">
        <h2 class="text-xl font-bold mt-10 mb-4 text-center">
          อสม.
        </h2>

        <div class="grid md:grid-cols-3 gap-6">
          <ProfileCard
            v-for="profile in volunteers"
            :key="profile.id"
            :profile="profile"
            @delete="deleteProfile"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import api from "@/services/api"
import ProfileCard from "@/components/village/ProfileCard.vue"

const profiles = ref([])
const loading = ref(true)

const leaders = computed(() =>
  profiles.value
    .filter(p => p.group === "leader")
    .sort((a, b) => a.level - b.level)
)

const committees = computed(() =>
  profiles.value.filter(p => p.group === "committee")
)

const volunteers = computed(() =>
  profiles.value.filter(p => p.group === "volunteer")
)

const fetchProfiles = async () => {
  try {
    const res = await api.get("/admin/village/profiles/")
    profiles.value = res.data
  } catch (err) {
    alert("โหลดข้อมูลไม่สำเร็จ")
  } finally {
    loading.value = false
  }
}

const deleteProfile = async (id) => {
  console.log("Deleting id:", id)

  if (!confirm("ต้องการลบโปรไฟล์นี้ใช่หรือไม่?")) return

  try {
    await api.delete(`/admin/village/profiles/${id}/`)
    profiles.value = profiles.value.filter(p => p.id !== id)
  } catch (err) {
    console.log(err.response?.data)
    alert("ลบไม่สำเร็จ")
  }
}

const displayGroup = (group) => {
  if (group === "leader") return "ผู้นำชุมชน"
  if (group === "committee") return "คณะกรรมการ"
  if (group === "volunteer") return "อสม."
  return group
}

onMounted(fetchProfiles)
</script>
