<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
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
});

const emit = defineEmits(["update:latitude", "update:longitude"]); // ส่งข้อมูลออกไปให้หน้าหลัก
//เมื่อ Admin คลิกย้าย marker component นี้จะ ส่งพิกัดใหม่ ออกไปให้ AdminVillageInfo.vue เก็บไว้ก่อน แล้วค่อยกดปุ่มบันทึกทีหลัง
const mapEl = ref(null);
const currentLat = ref(props.latitude ? parseFloat(props.latitude) : null);
const currentLng = ref(props.longitude ? parseFloat(props.longitude) : null);

const DEFAULT_LAT = 15.2;
const DEFAULT_LNG = 104.85;

let mapInstance = null;
let marker = null;

const placeMarker = (lat, lng) => {
  if (marker) { // ถ้ามี marker อยู่แล้ว → ย้ายตำแหน่ง
    marker.setLatLng([lat, lng]);
  } else { // ถ้ายังไม่มีให้สร้างใหม่ และให้ลากได้ (draggable: true)
    marker = L.marker([lat, lng], { draggable: true })
      .addTo(mapInstance)
      .bindPopup(`<b>${props.villageName}</b><br>คลิกแผนที่หรือลาก marker เพื่อย้ายพิกัด`)
      .openPopup();

    marker.on("dragend", (e) => {
      const pos = e.target.getLatLng();
      currentLat.value = parseFloat(pos.lat.toFixed(6));
      currentLng.value = parseFloat(pos.lng.toFixed(6));
      emit("update:latitude", currentLat.value);
      emit("update:longitude", currentLng.value);
    });
  }

  currentLat.value = parseFloat(lat.toFixed(6));
  currentLng.value = parseFloat(lng.toFixed(6));
  emit("update:latitude", currentLat.value);
  emit("update:longitude", currentLng.value);
};

const initMap = () => {
  const hasCoords = props.latitude && props.longitude;
  const centerLat = hasCoords ? parseFloat(props.latitude) : DEFAULT_LAT;
  const centerLng = hasCoords ? parseFloat(props.longitude) : DEFAULT_LNG;
  const zoom = hasCoords ? 15 : 10;

  mapInstance = L.map(mapEl.value).setView([centerLat, centerLng], zoom);

  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
    maxZoom: 19,
  }).addTo(mapInstance);

  if (hasCoords) {
    placeMarker(parseFloat(props.latitude), parseFloat(props.longitude));
  }

  mapInstance.on("click", (e) => { 
    placeMarker(e.latlng.lat, e.latlng.lng);
  }); //รับ event คลิกบนแผนที่ เพื่อวางหรือย้าย marker ไปที่ตำแหน่งที่คลิก 
}; //ทุกครั้งที่ Admin คลิกบนแผนที่จะเรียก placeMarker พร้อมพิกัดของจุดที่คลิก

onMounted(() => {
  if (mapEl.value) initMap();
});

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
    marker = null;
  }
});

watch(
  () => [props.latitude, props.longitude],
  ([newLat, newLng]) => {
    if (!mapInstance || !newLat || !newLng) return;
    const lat = parseFloat(newLat);
    const lng = parseFloat(newLng);
    if (!isNaN(lat) && !isNaN(lng)) {
      placeMarker(lat, lng);
      mapInstance.setView([lat, lng], 15);
    }
  }
);
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between text-sm text-gray-600">
      <span>คลิกบนแผนที่หรือลาก marker เพื่อตั้งพิกัดหมู่บ้าน</span>
      <span v-if="currentLat && currentLng" class="font-mono text-xs text-blue-600"> <!--Template แสดงพิกัดปัจจุบัน -->
        {{ currentLat }}, {{ currentLng }} <!--แสดงตัวเลขพิกัดให้ Admin เห็น ขณะreal-time ในตอนที่ทำการคลิกย้าย marker -->
      </span>
      <span v-else class="text-gray-400 text-xs">ยังไม่ได้ตั้งพิกัด</span>
    </div>
    <div ref="mapEl" class="w-full rounded-xl border border-gray-300 overflow-hidden" style="height: 380px;" />
  </div>
</template>