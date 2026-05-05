<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const props = defineProps({
  latitude: { type: [Number, String], default: null },
  longitude: { type: [Number, String], default: null },
  villageName: { type: String, default: "หมู่บ้านสร้างขุนศรี" },
  height: { type: String, default: "300px" },
});

const mapEl = ref(null);
let mapInstance = null;
let marker = null;

const getLat = () => props.latitude ? parseFloat(props.latitude) : null;
const getLng = () => props.longitude ? parseFloat(props.longitude) : null;

const googleMapsUrl = computed(() => {
  const lat = getLat();
  const lng = getLng();
  if (!lat || !lng) return null;
  return `https://www.google.com/maps?q=${lat},${lng}`;
});

const initMap = () => {
  const lat = getLat();
  const lng = getLng();

  mapInstance = L.map(mapEl.value, { zoomControl: true }).setView([lat, lng], 15);

  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
    maxZoom: 19,
  }).addTo(mapInstance);

  marker = L.marker([lat, lng])
    .addTo(mapInstance)
    .bindPopup(`<b>${props.villageName}</b>`)
    .openPopup();
};

onMounted(() => {
  const lat = getLat();
  const lng = getLng();
  if (mapEl.value && lat !== null && lng !== null) {
    initMap();
  }
});

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
});

watch(
  () => [props.latitude, props.longitude],
  async () => {
    const lat = getLat();
    const lng = getLng();
    if (lat === null || lng === null) return;

    if (!mapInstance) {
      await nextTick();
      if (mapEl.value) initMap();
      return;
    }

    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      marker = L.marker([lat, lng])
        .addTo(mapInstance)
        .bindPopup(`<b>${props.villageName}</b>`)
        .openPopup();
    }
    mapInstance.setView([lat, lng], 15);
  }
);
</script>

<template>
  <div class="w-full rounded-xl overflow-hidden border border-gray-200 shadow-sm">
    <div
      v-if="!latitude || !longitude"
      class="bg-gray-50 flex items-center justify-center text-gray-400 text-sm"
      :style="{ height }"
    >
      ยังไม่ได้ตั้งพิกัดหมู่บ้าน
    </div>

    <div v-else>
      <div ref="mapEl" :style="{ height }" />
      <a
        :href="googleMapsUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="flex items-center justify-center gap-2 py-2 bg-white border-t border-gray-200 text-sm text-blue-600 hover:bg-blue-50 transition"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        เปิดใน Google Maps
      </a>
    </div>
  </div>
</template>