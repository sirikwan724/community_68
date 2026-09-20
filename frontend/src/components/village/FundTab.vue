<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

/* =========================
   AUTH CHECK
========================= */
const router = useRouter();
const isLoggedIn = !!localStorage.getItem("access");

if (!isLoggedIn) {
  router.replace("/login");
}

/* =========================
   STATE
========================= */
const fundTypes = ref([]);
const selectedFund = ref(null);

const fundRecords = ref([]);
const selectedRecord = ref(null);

const loans = ref([]);

const loading = ref(false);
const error = ref("");        

/* =========================
   LOAD
========================= */
const loadFundTypes = async () => {
  try {
    const res = await api.get("/village/funds/");
    fundTypes.value = res.data;
  } catch {
    error.value = "ไม่สามารถโหลดข้อมูลกองทุนได้";
  }
};

const loadFundRecords = async () => {
  if (!selectedFund.value) return;
  try {
    const res = await api.get(`/village/funds/${selectedFund.value.id}/years/`);
    fundRecords.value = res.data;
    selectedRecord.value = null;
    loans.value = [];
  } catch {
    error.value = "ไม่สามารถโหลดปีงบประมาณได้";
  }
};

const loadLoans = async () => {
  if (!selectedRecord.value) return;
  try {
    const res = await api.get(`/village/funds/records/${selectedRecord.value.id}/loans/`);
    loans.value = res.data;
  } catch {
    error.value = "ไม่สามารถโหลดรายชื่อผู้กู้ได้";
  }
};

watch(selectedFund, loadFundRecords);
watch(selectedRecord, loadLoans);

onMounted(loadFundTypes);
</script>

<template>
  <div>

    <h2 class="text-xl font-semibold mb-4">กองทุนหมู่บ้าน</h2>
    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <!-- FUND TYPES -->
    <div class="flex gap-3 mb-6">
      <button
        v-for="f in fundTypes"
        :key="f.id"
        @click="selectedFund = f"
        class="px-4 py-2 rounded border"
        :class="selectedFund?.id === f.id
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100'"
      >
        {{ f.name }}
      </button>
    </div>

    <!-- YEARS -->
    <div v-if="selectedFund" class="mb-6">
      <h3 class="font-medium mb-2">เลือกปีเพื่อดูงบประมาณกองทุน</h3>

      <select
        v-model="selectedRecord"
        class="border px-3 py-2 rounded w-52"
      >
        <option disabled :value="null">-- เลือกปีเพื่อดู --</option>
        <option
          v-for="r in fundRecords"
          :key="r.id"
          :value="r"
        >
          {{ r.year }}
        </option>
      </select>
    </div>

    <!-- TABLE -->
    <div v-if="selectedRecord">
      <h3 class="font-medium mb-3">
        รายชื่อผู้กู้ ปี {{ selectedRecord.year }}
      </h3>

      <table class="w-full border text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="border px-2 py-1">ชื่อ</th>
            <th class="border px-2 py-1">เลขบัญชี</th>
            <th class="border px-2 py-1">เงินกู้</th>
            <th class="border px-2 py-1">ดอกเบี้ย</th>
            <th class="border px-2 py-1">วัตถุประสงค์</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in loans" :key="l.id">
            <td class="border px-2 py-1">{{ l.full_name }}</td>
            <td class="border px-2 py-1">{{ l.masked_account }}</td>
            <td class="border px-2 py-1">{{ l.loan_amount }}</td>
            <td class="border px-2 py-1">{{ l.interest_amount }}</td>
            <td class="border px-2 py-1">{{ l.purpose }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
