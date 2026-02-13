<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

/* =========================
   AUTH GUARD
========================= */
const router = useRouter();
const role = localStorage.getItem("role");

if (role !== "admin") {
  router.replace("/");
}

/* =========================
   STATE
========================= */
const fundTypes = ref([]);
const selectedFund = ref(null);

const fundRecords = ref([]);
const selectedRecord = ref(null);

const loans = ref([]);

const year = ref(new Date().getFullYear() + 543);
const interestRate = ref("");

const excelFile = ref(null);

const loading = ref(false);
const message = ref("");
const error = ref("");

const handleFileChange = (e) => {
  excelFile.value = e.target.files[0];
  message.value = "";
  error.value = "";
};

/* =========================
   LOAD DATA
========================= */
const loadFundTypes = async () => {
  try {
    const res = await api.get("/village/funds/");
    fundTypes.value = res.data;
  } catch {
    error.value = "ไม่สามารถโหลดประเภทกองทุนได้";
  }
};

const loadFundRecords = async () => {
  if (!selectedFund.value) return;
  try {
    const res = await api.get(
      `/village/funds/${selectedFund.value.id}/years/`
    );
    fundRecords.value = res.data;
    selectedRecord.value = null;
    loans.value = [];
  } catch {
    error.value = "โหลดปีงบประมาณไม่สำเร็จ";
  }
};

const loadLoans = async () => {
  if (!selectedRecord.value) return;
  try {
    const res = await api.get(
      `/village/funds/records/${selectedRecord.value.id}/loans/`
    );
    loans.value = res.data;
  } catch {
    error.value = "โหลดรายชื่อผู้กู้ไม่สำเร็จ";
  }
};

/* =========================
   ACTIONS (ADMIN)
========================= */
const addFundRecord = async () => {
  if (!year.value || !interestRate.value) return;

  loading.value = true;
  try {
    await api.post(
      `/admin/funds/${selectedFund.value.id}/records/`,
      {
        fund_type: selectedFund.value.id,
        year: year.value,
        interest_rate: interestRate.value,
      }
    );
    message.value = "เพิ่มปีงบประมาณสำเร็จ";
    interestRate.value = "";
    await loadFundRecords();
  } catch {
    error.value = "เพิ่มปีงบประมาณไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
};

const uploadExcel = async () => {
  if (!excelFile.value || !selectedRecord.value) return;

  if (!confirm("การนำเข้าใหม่จะลบข้อมูลเดิมทั้งหมด ต้องการดำเนินการหรือไม่?")) {
    return;
  }

  const formData = new FormData();
  formData.append("file", excelFile.value);

  loading.value = true;
  try {
    await api.post(
      `/admin/funds/records/${selectedRecord.value.id}/import-excel/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    message.value = "นำเข้าไฟล์ Excel สำเร็จ";
    excelFile.value = null;
    await loadFundRecords();
    await loadLoans();
  } catch (err) {
    console.error(err);
    error.value = "นำเข้าไฟล์ไม่สำเร็จ";
  } finally {
    loading.value = false;
  }
};

/* =========================
   WATCH
========================= */
watch(selectedFund, () => {
  message.value = "";
  error.value = "";
  loadFundRecords();
});

watch(selectedRecord, () => {
  message.value = "";
  error.value = "";
  loadLoans();
});

onMounted(loadFundTypes);
</script>

<template>
  <div class="bg-white p-6 rounded-xl shadow">
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-2xl font-bold mb-6">จัดการกองทุนหมู่บ้าน</h1>
        <p class="text-gray-500 text-sm">จัดการข้อมูล</p>
      </div>
      
      <router-link 
        to="/admin/dashboard" 
        class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
      >
        กลับหน้าหลัก
      </router-link>
    </div>

    <p v-if="message" class="text-green-600 mb-2">{{ message }}</p>
    <p v-if="error" class="text-red-600 mb-2">{{ error }}</p>

    <!-- =========================
         FUND TYPES
    ========================= -->
    <section>
      <h2 class="font-semibold mb-2">ประเภทกองทุน</h2>
      <div class="flex gap-3 flex-wrap">
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
    </section>

    <!-- =========================
         FUND RECORDS
    ========================= -->
    <section v-if="selectedFund" class="mt-8">
      <h2 class="font-semibold mb-3">
        ปีงบประมาณ ({{ selectedFund.name }})
      </h2>

      <div class="flex gap-2 items-center mb-4">
        <input
          v-model="year"
          type="number"
          class="border px-3 py-2 rounded w-28"
        />
        <input
          v-model="interestRate"
          type="number"
          placeholder="ดอกเบี้ย (%)"
          class="border px-3 py-2 rounded w-32"
        />
        <button
          @click="addFundRecord"
          class="px-4 py-2 bg-green-600 text-white rounded"
        >
          เพิ่มปี
        </button>
      </div>

      <div class="mb-4">
        <select
          v-model="selectedRecord"
          class="border px-3 py-2 rounded w-40"
        >
          <option disabled value="">-- เลือกปีงบประมาณ --</option>

          <option
            v-for="r in fundRecords"
            :key="r.id"
            :value="r"
          >
            {{ r.year }}
          </option>
        </select>
      </div>
    </section>

    <!-- =========================
         LOANS
    ========================= -->
    <section v-if="selectedRecord" class="mt-8">
      <h2 class="font-semibold mb-3">
        รายชื่อผู้กู้ ปี {{ selectedRecord.year }}
      </h2>

      <input
        type="file"
        @change="handleFileChange"
        class="mb-2"
      />
      <p class="text-sm text-gray-500 mb-2">
        {{ selectedRecord?.last_uploaded_file || "ไม่มีไฟล์ที่เลือก" }}
      </p>

      <button
        @click="uploadExcel"
        class="px-4 py-2 bg-blue-600 text-white rounded mb-4"
      >
        นำเข้า Excel
      </button>

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
    </section>
  </div>
</template>
