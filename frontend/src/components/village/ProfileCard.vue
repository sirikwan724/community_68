<template>
  <div class="bg-white rounded-xl shadow p-5">

    <img
      v-if="profile.image"
      :src="getImageUrl(profile.image)"
      class="w-24 h-24 mx-auto rounded-full object-cover mb-4"
    />

    <div v-else class="w-24 h-24 mx-auto rounded-full bg-gray-200 mb-4" />

    <h3 class="text-center font-bold text-lg">
      {{ profile.prefix }} {{ profile.full_name }}
    </h3>

    <p class="text-center text-sm text-gray-600">
      {{ profile.position }}
    </p>

    <p v-if="profile.phone" class="text-center text-sm text-gray-500">
      📞 {{ profile.phone }}
    </p>

    <p v-if="profile.email" class="text-center text-sm text-gray-500">
      ✉️ {{ profile.email }}
    </p>

    <p v-if="profile.description" class="text-center text-xs mt-3 text-gray-400">
      {{ profile.description }}
    </p>

    <div v-if="isAdmin" class="flex justify-center gap-4 mt-4">
      <router-link
        :to="`/admin/profiles/${profile.id}/edit`"
        class="text-blue-600 hover:underline text-sm"
      >
        แก้ไข
      </router-link>

      <button
        @click="$emit('delete', profile.id)"
        class="text-red-600 hover:underline text-sm"
      >
        ลบ
      </button>
    </div>

  </div>
</template>

<script setup>

const getImageUrl = (path) => {
  if (!path) return null

  if (path.startsWith("http")) {
    return path
  }

  return `http://localhost:8000${path}`
}

defineProps({
  profile: Object,
  isAdmin: {
    type: Boolean,
    default: true
  }
})

</script>
