<script setup>
import { ref, reactive, computed, watch } from "vue";
import RichSection from "./sections/RichSection.vue";
import PlacesSection from "./sections/PlacesSection.vue";

const isHydrating = ref(false);
const sectionPreviews = ref([]);
const props = defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: "create" },
  initialSection: { type: Object, default: null },
});

const emit = defineEmits(["close", "save"]);

/** ---------- helpers ---------- */
const uid = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

const TYPE_OPTIONS = [
  { value: "RICH", label: "ข้อมูล/บทความ (หัวข้อ + รายละเอียด + รูป)" },
  { value: "PLACES", label: "รายการสถานที่ (หัวข้อ + รายละเอียด + หลายรายการย่อย)" },
];

const onPickSectionFiles = (e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;

  form.imageFiles = [...(form.imageFiles || []), ...files];
  sectionPreviews.value = form.imageFiles.map((f) => URL.createObjectURL(f));

  // reset input เพื่อให้เลือกไฟล์เดิมซ้ำได้
  e.target.value = "";
};

const onPickPlaceFiles = (place, e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;

  place.imageFiles = [...(place.imageFiles || []), ...files];
  place._previews = place.imageFiles.map((f) => URL.createObjectURL(f));

  e.target.value = "";
};

/** ---------- form state ---------- */
const form = reactive({
  id: "",
  type: "RICH",
  title: "",

  // RICH
  contentText: "",
  imagesText: "",      // เอาไว้รองรับ URL เดิมหรือรูปเก่าที่มีอยู่แล้ว
  imageFiles: [],      // ใหม่: เก็บไฟล์ที่ผู้ใช้เลือก

  // PLACES
  description: "",
  places: [
    {
      id: uid(),
      name: "",
      detail: "",
      imagesText: "",   // URL เดิม/รูปเก่า
      imageFiles: [],   // ใหม่: เก็บไฟล์ของสถานที่นี้
    },
  ],
});

const resetForm = () => {
  form.id = uid();
  form.type = "RICH";
  form.title = "";
  form.contentText = "";
  form.imagesText = "";
  form.imageFiles = [];
  form.description = "";
  form.places = [
    {
      id: uid(),
      name: "",
      detail: "",
      imagesText: "",
      imageFiles: [],
    },
  ];
  sectionPreviews.value = [];
};

/** เติมข้อมูลเมื่อ edit */
const loadFromInitial = (sec) => {
  isHydrating.value = true;
  resetForm();
  if (!sec) { isHydrating.value = false; return; }

  form.id = sec.id || uid();
  form.type = sec.type || "RICH";
  form.title = sec.title || "";

  if (form.type === "RICH") {
  const lines = Array.isArray(sec.content) ? sec.content : [];
  form.contentText = lines.join("\n");

  const imgs = Array.isArray(sec.images) ? sec.images : [];
  form.imagesText = imgs
    .map((x) => (typeof x === "string" ? x : x?.url))
    .filter(Boolean)
    .join("\n");

  form.imageFiles = [];
  sectionPreviews.value = [];
  }

  if (form.type === "PLACES") {
    form.description = sec.description || "";
    const items = Array.isArray(sec.items) ? sec.items : (Array.isArray(sec.places) ? sec.places : []);
    form.places = items.length
      ? items.map((p) => ({
          id: p.id || uid(),
          name: p.name || "",
          detail: p.detail || "",
          imagesText: (p.images || [])
            .map((x) => (typeof x === "string" ? x : x?.url))
            .filter(Boolean)
            .join("\n"),
          imageFiles: [],
          _previews: [],
        }))
      : [{ id: uid(), name: "", detail: "", imagesText: "", imageFiles: [], _previews: [] }];
  }

  isHydrating.value = false;
};

/** เมื่อ modal เปิด: create => reset, edit => load */
watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return;
    if (props.mode === "edit" && props.initialSection) loadFromInitial(props.initialSection);
    else resetForm();
  },
  { immediate: true }
);

/** ถ้าเปลี่ยน type ให้เคลียร์เฉพาะบางส่วน */
watch(() => form.type, (t) => {
  if (isHydrating.value) return;

  if (t === "RICH") {
    form.description = "";
    form.places = [{ id: uid(), name: "", detail: "", imagesText: "", imageFiles: [], _previews: [] }];
  } else if (t === "PLACES") {
    form.contentText = "";
    form.imagesText = "";
  }
});

/** ---------- computed: preview section ---------- */
const previewSection = computed(() => {
  if (form.type === "RICH") {
    const content = form.contentText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);

    const images = form.imagesText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);

    return {
      id: form.id,
      type: "RICH",
      title: form.title || "(ยังไม่ใส่หัวข้อ)",
      content,
      images,
    };
  }

  // PLACES
  const items = form.places.map((p) => ({
    id: p.id,
    name: p.name || "(ยังไม่ใส่ชื่อสถานที่)",
    detail: p.detail || "",
    images: p.imagesText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
  }));

  return {
    id: form.id,
    type: "PLACES",
    title: form.title || "(ยังไม่ใส่หัวข้อ)",
    description: form.description || "",
    items,
  };
});

const addPlace = () => {
  form.places.push({ id: uid(), name: "", detail: "", imagesText: "", imageFiles: [], _previews: [] });
};

const removePlace = (id) => {
  if (form.places.length <= 1) return;
  form.places = form.places.filter((p) => p.id !== id);
};

/** ---------- actions ---------- */
const close = () => emit("close");

const save = () => {
  // validation แบบเบา ๆ
  if (!form.title.trim()) {
    alert("กรุณาใส่หัวข้อ");
    return;
  }

  // ส่งออกเป็น section ตาม schema ที่ VillageTab ใช้
  emit("save", {
    section: previewSection.value,
    sectionFiles: form.imageFiles,
    places: form.places.map((p) => ({
      name: p.name,
      detail: p.detail,
      files: p.imageFiles || [],
    })),
  });
  emit("close");
};
</script>
<template>
  <div v-if="open" class="fixed inset-0 z-50">
    <!-- overlay -->
    <div class="absolute inset-0 bg-black/40" @click="close"></div>

    <!-- modal -->
    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="w-full max-w-6xl bg-white rounded-2xl shadow-xl overflow-hidden max-h-[90vh] flex flex-col">
        <!-- header -->
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-gray-900">
              {{ mode === "edit" ? "แก้ไขหัวข้อ" : "เพิ่มหัวข้อใหม่" }}
            </h2>
            <p class="text-sm text-gray-500">
              กรอกข้อมูล แล้วดูตัวอย่าง (Preview) ก่อนบันทึก
            </p>
          </div>

          <button class="px-3 py-2 rounded hover:bg-gray-100" @click="close">
            ปิด
          </button>
        </div>

        <!-- body -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-0 overflow-y-auto flex-1">
          <!-- left: form -->
          <div class="p-6 border-b lg:border-b-0 lg:border-r">
            <div class="space-y-4">
              <!-- type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">ประเภทหัวข้อ</label>
                <select v-model="form.type" class="w-full border rounded-lg px-3 py-2">
                  <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>

              <!-- title -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">หัวข้อ</label>
                <input
                  v-model="form.title"
                  type="text"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="เช่น ข้อมูลหมู่บ้าน / ประวัติความเป็นมา / สถานที่สาธารณะ"
                />
              </div>

              <!-- RICH form -->
              <div v-if="form.type === 'RICH'" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">รายละเอียด (พิมพ์หลายบรรทัดได้)</label>
                  <textarea
                    v-model="form.contentText"
                    rows="6"
                    class="w-full border rounded-lg px-3 py-2"
                    placeholder="พิมพ์รายละเอียด... (แต่ละบรรทัดจะแสดงเป็นย่อหน้า)"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    รูปภาพ (ใส่ URL ได้หลายบรรทัด — เว้นว่างได้)
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    class="w-full border rounded-lg px-3 py-2"
                    @change="onPickSectionFiles"
                  />
                  <p v-if="sectionPreviews.length" class="text-xs text-gray-500 mt-1">
                    เลือกแล้ว {{ sectionPreviews.length }} ไฟล์
                  </p>

                  <div v-if="sectionPreviews.length" class="mt-3 grid grid-cols-3 gap-2">
                    <img
                      v-for="(src,i) in sectionPreviews"
                      :key="i"
                      :src="src"
                      class="w-full h-24 object-cover rounded"
                    />
                  </div>
                  <p class="text-xs text-gray-500 mt-1">
                    เลือกได้หลายไฟล์ (จะอัปโหลดเข้าระบบ)
                  </p>
                </div>
              </div>

              <!-- PLACES form -->
              <div v-else class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">รายละเอียดหัวข้อ</label>
                  <textarea
                    v-model="form.description"
                    rows="3"
                    class="w-full border rounded-lg px-3 py-2"
                    placeholder="เช่น รวมสถานที่สำคัญที่ประชาชนใช้ร่วมกัน"
                  ></textarea>
                </div>

                <div class="flex items-center justify-between">
                  <h3 class="font-semibold text-gray-900">รายการสถานที่</h3>
                  <button class="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" @click="addPlace">
                    + เพิ่มสถานที่
                  </button>
                </div>

                <div class="space-y-4">
                  <div
                    v-for="(p, idx) in form.places"
                    :key="p.id"
                    class="border rounded-xl p-4 bg-gray-50"
                  >
                    <div class="flex items-center justify-between mb-3">
                      <div class="font-medium text-gray-800">สถานที่ที่ {{ idx + 1 }}</div>
                      <button
                        class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300"
                        @click="removePlace(p.id)"
                        :disabled="form.places.length <= 1"
                        title="ต้องมีอย่างน้อย 1 รายการ"
                      >
                        ลบ
                      </button>
                    </div>

                    <div class="space-y-3">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">ชื่อสถานที่</label>
                        <input
                          v-model="p.name"
                          type="text"
                          class="w-full border rounded-lg px-3 py-2"
                          placeholder="เช่น วัดประจำหมู่บ้าน / สนามเด็กเล่น"
                        />
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">รายละเอียดสถานที่</label>
                        <textarea
                          v-model="p.detail"
                          rows="3"
                          class="w-full border rounded-lg px-3 py-2"
                          placeholder="รายละเอียด..."
                        ></textarea>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                          รูปสถานที่ (URL หลายบรรทัด — เว้นว่างได้)
                        </label>
                        <input
                          type="file"
                          multiple
                          accept="image/*"
                          class="w-full border rounded-lg px-3 py-2"
                          @change="(e) => onPickPlaceFiles(p, e)"
                        />
                        <div v-if="p._previews?.length" class="mt-3 grid grid-cols-3 gap-2">
                          <img
                            v-for="(src,i) in p._previews"
                            :key="i"
                            :src="src"
                            class="w-full h-24 object-cover rounded"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- footer buttons -->
              <div class="pt-2 flex justify-end gap-3">
                <button class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300" @click="close">
                  ยกเลิก
                </button>
                <button class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" @click="save">
                  บันทึก
                </button>
              </div>
            </div>
          </div>

          <!-- right: preview -->
          <div class="p-6">
            <div class="mb-4">
              <h3 class="text-lg font-bold text-gray-900">Preview (เหมือนหน้าผู้ใช้)</h3>
              <p class="text-sm text-gray-500">ตัวอย่างการแสดงผลจริงตามประเภทหัวข้อ</p>
            </div>

            <div class="border rounded-xl p-5 bg-white">
              <RichSection v-if="previewSection.type === 'RICH'" :section="previewSection" />
              <PlacesSection v-else :section="previewSection" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>