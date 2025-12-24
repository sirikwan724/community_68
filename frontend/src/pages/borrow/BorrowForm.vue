<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { BorrowService } from "@/services/borrow.service";
import api from "@/services/api";

// =========================
// STATE หลัก
// =========================
const borrowType = ref("ITEM");
const router = useRouter();
const items = ref([]);
const locations = ref([]);

const form = ref({
  // ITEM
  items: [
    { item: null, quantity: 1 },
    { item: null, quantity: 1 },
    { item: null, quantity: 1 },
  ],

  // LOCATION
  location: null,

  // common
  start_datetime: "",
  end_datetime: "",
  pickup_datetime: "",
  expected_return_datetime: "",
  purpose: "",
});

// =========================
// LOAD DATA (Item / Location)
// =========================

onMounted(async () => {
  try {
    const itemRes = await api.get("/borrow/items/");
    items.value = itemRes.data;   

    const locRes = await api.get("/borrow/locations/");
    locations.value = locRes.data;

    console.log("ITEMS =", items.value);
  } catch (err) {
    console.error(err);
    alert("โหลดข้อมูลไม่สำเร็จ");
  }
});


// =========================
// HELPER
// =========================
const getStockText = (itemId) => {
  const found = items.value.find((i) => i.id === itemId);
  if (!found) return "";
  return `คงเหลือ: ${found.stock} ${found.unit}`;
};

// =========================
// SUBMIT
// =========================
const submit = async () => {
  try {
    // -------------------------
    // 1. เตรียม items ให้สะอาด
    // -------------------------
    const cleanItems =
      borrowType.value === "ITEM"
        ? form.value.items
            .filter(i => i.item !== null && i.quantity > 0)
            .map(i => ({
              item: Number(i.item),
              quantity: Number(i.quantity),
            }))
        : [];

    if (borrowType.value === "ITEM" && cleanItems.length === 0) {
      alert("กรุณาเลือกสิ่งของอย่างน้อย 1 รายการ");
      return;
    }

    if (!form.value.start_datetime || !form.value.end_datetime) {
      alert("กรุณากรอกวันเวลาเริ่มและสิ้นสุด");
      return;
    }

    // -------------------------
    // 2. สร้าง payload ใหม่ (ห้าม spread)
    // -------------------------
    const payload = {
      borrow_type: borrowType.value,
      items: cleanItems,
      location:
        borrowType.value === "LOCATION"
          ? form.value.location
          : null,
      start_datetime: form.value.start_datetime,
      end_datetime: form.value.end_datetime,
      pickup_datetime: form.value.pickup_datetime || null,
      expected_return_datetime:
        form.value.expected_return_datetime || null,
      purpose: form.value.purpose,
    };

    console.log("PAYLOAD SENT =", payload);

    // -------------------------
    // 3. ส่ง API
    // -------------------------
    await BorrowService.createRequest(payload);

    alert("ส่งคำขอเรียบร้อย");
    router.push("/my-history");
  } catch (err) {
    console.error(err.response?.data);
    alert(JSON.stringify(err.response?.data));
  }
};

</script>

<template>
  <div class="max-w-4xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">ขออนุญาตยืม</h1>

    <!-- เลือกประเภท -->
    <div class="mb-6">
      <label class="font-semibold block mb-2">ประเภทการยืม</label>
      <select v-model="borrowType" class="border p-2 w-full">
        <option value="ITEM">ยืมสิ่งของ</option>
        <option value="LOCATION">ยืมสถานที่</option>
      </select>
    </div>

    <!-- =========================
         ยืมสิ่งของ
    ========================== -->
    <div v-if="borrowType === 'ITEM'" class="mb-6">
      <h2 class="font-semibold mb-2">เลือกสิ่งของ (สูงสุด 3 รายการ)</h2>

      <div
        v-for="(row, index) in form.items"
        :key="index"
        class="border rounded p-3 mb-3"
      >
        <select v-model="row.item" class="border p-2 w-full mb-2">
          <option :value="null">ไม่ยืม</option>
          <option
            v-for="item in items"
            :key="item.id"
            :value="item.id"
          >
            {{ item.name }}
          </option>
        </select>

        <div v-if="row.item" class="text-sm text-gray-600 mb-1">
          {{ getStockText(row.item) }}
        </div>

        <input
          type="number"
          min="1"
          v-model.number="row.quantity"
          class="border p-2 w-full"
          placeholder="จำนวนที่ต้องการยืม"
        />
      </div>
    </div>

    <!-- =========================
         ยืมสถานที่
    ========================== -->
    <div v-if="borrowType === 'LOCATION'" class="mb-6">
      <label class="font-semibold block mb-2">เลือกสถานที่</label>
      <select v-model="form.location" class="border p-2 w-full">
        <option :value="null">-- เลือกสถานที่ --</option>
        <option
          v-for="loc in locations"
          :key="loc.id"
          :value="loc.id"
        >
          {{ loc.name }}
        </option>
      </select>
    </div>

    <!-- =========================
         วันเวลา
    ========================== -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div>
        <label class="block mb-1">วัน–เวลาเริ่มยืม</label>
        <input
          type="datetime-local"
          v-model="form.start_datetime"
          class="border p-2 w-full"
        />
      </div>

      <div>
        <label class="block mb-1">วัน–เวลาสิ้นสุด</label>
        <input
          type="datetime-local"
          v-model="form.end_datetime"
          class="border p-2 w-full"
        />
      </div>

      <div>
        <label class="block mb-1">วัน–เวลารับของ</label>
        <input
          type="datetime-local"
          v-model="form.pickup_datetime"
          class="border p-2 w-full"
        />
      </div>

      <div>
        <label class="block mb-1">วัน–เวลานำมาคืน</label>
        <input
          type="datetime-local"
          v-model="form.expected_return_datetime"
          class="border p-2 w-full"
        />
      </div>
    </div>

    <!-- วัตถุประสงค์ -->
    <div class="mb-6">
      <label class="font-semibold block mb-2">วัตถุประสงค์</label>
      <textarea
        v-model="form.purpose"
        rows="4"
        class="border p-2 w-full"
      ></textarea>
    </div>

    <!-- ปุ่ม -->
    <button
      @click="submit"
      class="bg-blue-600 text-white px-6 py-2 rounded"
    >
      ส่งคำขอ
    </button>
    <button
        @click="router.push('/')"
        class="bg-blue-600 text-white px-6 py-2 rounded"
      >
        กลับหน้าหลัก
    </button>
  </div>
</template>
