<template>
  <div class="max-w-3xl mx-auto">
    <!-- Header -->
    <div class="mb-6 border-b pb-4 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">
        {{ isEdit ? "แก้ไขโปรไฟล์" : "เพิ่มโปรไฟล์ใหม่" }}
      </h1>

      <router-link
        to="/admin/profiles"
        class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
      >
        กลับ
      </router-link>
    </div>

    <!-- Form -->
    <div class="bg-white shadow rounded-xl p-6 space-y-5">
      <!-- Group -->
      <div>
        <label class="block text-sm font-medium mb-1">กลุ่ม</label>
        <select v-model="form.group" class="w-full border rounded-lg px-3 py-2">
          <option value="leader">ผู้นำชุมชน</option>
          <option value="committee">คณะกรรมการ</option>
          <option value="volunteer">อสม.(อาสาสาธารณสุขประจำหมู่บ้าน) </option>
        </select>
      </div>

      <!-- Prefix -->
      <div>
        <label class="block text-sm font-medium mb-1">คำนำหน้า</label>
        <select v-model="form.prefix" class="w-full border rounded-lg px-3 py-2">
          <option value="" disabled>-- เลือกคำนำหน้า --</option>
          <option value="นาย">นาย</option>
          <option value="นาง">นาง</option>
          <option value="นางสาว">นางสาว</option>
          <option value="อื่นๆ">อื่นๆ</option>
        </select>
      </div>

      <!-- Custom Prefix (แสดงเมื่อเลือก อื่นๆ) -->
      <div v-if="form.prefix === 'อื่นๆ'">
        <label class="block text-sm font-medium mb-1">ระบุคำนำหน้า</label>
        <input
          v-model="customPrefix"
          class="w-full border rounded-lg px-3 py-2"
          placeholder="กรอกคำนำหน้า"
        />
      </div>

      <!-- Name -->
      <div>
        <label class="block text-sm font-medium mb-1">ชื่อ - สกุล</label>
        <input v-model="form.full_name" class="w-full border rounded-lg px-3 py-2" />
      </div>

      <!-- Position -->
      <div>
        <label class="block text-sm font-medium mb-1">ตำแหน่ง</label>
        <select v-model="form.position" class="w-full border rounded-lg px-3 py-2">
          <option value="" disabled>-- เลือกตำแหน่ง --</option>
          <option v-for="pos in availablePositions" :key="pos.name" :value="pos.name">
            {{ pos.name }}
          </option>
        </select>
      </div>

      <!-- Phone -->
      <div>
        <label class="block text-sm font-medium mb-1">เบอร์โทร</label>
        <input v-model="form.phone" class="w-full border rounded-lg px-3 py-2" />
      </div>

      <!-- Email -->
      <div>
        <label class="block text-sm font-medium mb-1">อีเมล</label>
        <input v-model="form.email" type="email" class="w-full border rounded-lg px-3 py-2" />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-1">รายละเอียด</label>
        <textarea v-model="form.description" rows="4"
          class="w-full border rounded-lg px-3 py-2"></textarea>
      </div>

      <!-- Image -->
      <div>
        <label class="block text-sm font-medium mb-1">รูปโปรไฟล์</label>
        <input type="file" @change="handleFile" />

        <img
          v-if="previewImage"
          :src="previewImage"
          class="w-24 h-24 mt-3 rounded-full object-cover"
        />
      </div>

      <!-- Buttons -->
      <div class="flex justify-end gap-3 pt-4">
        <button
          @click="submitForm"
          class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          บันทึก
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch, nextTick } from "vue"
import { useRoute, useRouter } from "vue-router"
import api from "@/services/api"

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)

const POSITION_CONFIG = {
  leader: [
    { name: "ผู้ใหญ่บ้าน" },
    { name: "ผู้ช่วยผู้ใหญ่บ้าน" },
    { name: "อาสาเกษตรหมู่บ้าน" },
    { name: "อบต." },
    { name: "อปพร." },
  ],
  volunteer: [
    { name: "ประธานอาสาสาธารณสุขประจำหมู่บ้าน" },
    { name: "รองประธานอาสาสาธารณสุขประจำหมู่บ้าน" },
    { name: "อาสาสาธารณสุขประจำหมู่บ้าน" },
  ],
  committee: [
    { name: "ประธานคณะกรรมการหมู่บ้าน" },
    { name: "รองประธานคณะกรรมการ" },
    { name: "กรรมการหมู่บ้าน" },
  ],
}

const form = reactive({
  group: "leader",
  prefix: "",
  position: "",
  full_name: "",
  phone: "",
  email: "",
  description: "",
})

const customPrefix = ref("")

const finalPrefix = computed(() =>
  form.prefix === "อื่นๆ" ? customPrefix.value : form.prefix)

const availablePositions = computed(() => POSITION_CONFIG[form.group] || [])

let isLoadingProfile = false

watch(() => form.group, () => {
  if (!isLoadingProfile) {
    form.position = ""
  }
})

const imageFile = ref(null)
const previewImage = ref(null)

const handleFile = (e) => {
  imageFile.value = e.target.files[0]
  previewImage.value = URL.createObjectURL(imageFile.value)
}

const fetchProfile = async () => {
  isLoadingProfile = true
  const res = await api.get(`/admin/village/profiles/${route.params.id}/`)
  Object.assign(form, res.data)
  previewImage.value = res.data.image
  await nextTick()
  isLoadingProfile = false
}

const submitForm = async () => {
  try {
    const formData = new FormData()

    Object.entries(form).forEach(([key, value]) => {
      if (key === "image") return
      if (key === "email" && (!value || value === "-")) return

      if (key === "prefix") {
        formData.append("prefix", finalPrefix.value)
      } else {
        formData.append(key, value)
      }
    })

    if (imageFile.value) {
      formData.append("image", imageFile.value)
    }

    if (isEdit.value) {
      await api.put(`/admin/village/profiles/${route.params.id}/`, formData)
    } else {
      await api.post("/admin/village/profiles/", formData)
    }

    router.push("/admin/profiles")

  } catch (err) {
    console.log("FULL ERROR:", err.response?.data)
    alert(JSON.stringify(err.response?.data))
  }
}

onMounted(() => {
  if (isEdit.value) {
    fetchProfile()
  }
})
</script>
