<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const reports = ref([]);
const loading = ref(true);
const showNoteBox = ref(null); // id ของรายงานที่กำลังกดเพิ่มโน้ต
const noteMessage = ref("");

const loadData = async () => {
  try {
    const token = localStorage.getItem("access");
    const res = await axios.get(
      "http://localhost:8000/api/reports/admin/processing/",
      { headers: { Authorization: `Bearer ${token}` } }
    );

    reports.value = res.data;
  } catch (err) {
    console.error("load error:", err);
  } finally {
    loading.value = false;
  }
};

// ------- เพิ่มโน้ต -------
const addNote = async (id) => {
  if (!noteMessage.value.trim()) return alert("กรุณากรอกโน้ต");

  try {
    const token = localStorage.getItem("access");

    const res = await axios.post(
      `http://localhost:8000/api/reports/${id}/add-note/`,
      { message: noteMessage.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    // push note ลงรายงาน
    const report = reports.value.find((x) => x.id === id);
    report.notes.push(res.data.note);

    noteMessage.value = "";
    showNoteBox.value = null;
  } catch (err) {
    console.error("Add note error:", err);
    alert("เพิ่มโน้ตไม่สำเร็จ");
  }
};

// ------- ปุ่มแก้ไขแล้วเสร็จ -------
const doneReport = async (id) => {
  if (!confirm("ระบุว่าแก้ไขแล้วเสร็จใช่ไหม?")) return;

  try {
    const token = localStorage.getItem("access");

    await axios.patch(
      `http://localhost:8000/api/reports/${id}/done/`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );

    // remove จากหน้า processing
    reports.value = reports.value.filter((r) => r.id !== id);
  } catch (err) {
    console.error("Done error:", err);
  }
};

onMounted(loadData);
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">📌 รายงานหมู่บ้าน (กำลังดำเนินการ)</h1>

    <router-link 
        to="/admin/dashboard" 
        class="flex items-center gap-2 text-gray-500 hover:text-blue-700 transition font-medium px-4 py-2 rounded-lg hover:bg-blue-50 border border-transparent hover:border-blue-100"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
        กลับหน้าหลัก
    </router-link>

    <div v-if="loading">กำลังโหลด...</div>

    <div v-else-if="reports.length === 0" class="text-gray-500">
      ไม่มีรายงานกำลังดำเนินการ
    </div>

    <div v-else class="space-y-4">
      <div v-for="r in reports" :key="r.id" class="p-4 bg-white rounded shadow">
        <p class="font-bold text-lg">{{ r.category }}</p>
        <p>พื้นที่: {{ r.area }}</p>
        <p>{{ r.description }}</p>

        <!-- ปุ่ม -->
        <div class="flex gap-3 mt-3">
          <button
            @click="showNoteBox = r.id"
            class="px-4 py-1 bg-yellow-500 text-white rounded"
          >
            อัปเดตงาน
          </button>

          <button
            @click="doneReport(r.id)"
            class="px-4 py-1 bg-green-600 text-white rounded"
          >
            แก้ไขแล้วเสร็จ
          </button>
        </div>

        <!-- กล่องเพิ่มโน้ต -->
        <div v-if="showNoteBox === r.id" class="mt-3">
          <textarea
            v-model="noteMessage"
            class="w-full border rounded p-2"
            rows="3"
            placeholder="เพิ่มโน้ต..."
          ></textarea>

          <button
            @click="addNote(r.id)"
            class="mt-2 px-4 py-1 bg-blue-600 text-white rounded"
          >
            บันทึกโน้ต
          </button>
        </div>

        <!-- แสดงโน้ต -->
        <div class="mt-3" v-if="r.notes.length > 0">
          <p class="font-semibold">โน้ตงาน:</p>
          <ul class="text-sm text-gray-600 space-y-1">
            <li v-for="n in r.notes" :key="n.id">
              - {{ n.message }} ({{ n.created_at }})
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
