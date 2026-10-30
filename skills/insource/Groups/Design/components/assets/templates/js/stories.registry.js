/**
 * stories.registry.js — the single source of truth for the component gallery.
 *
 * Pure data: no DOM, no functions, no imports. The shell (js/stories.js) renders from this, the
 * descriptor filter reads the state keys from this, and scripts/stories_check.mjs validates this.
 *
 * Rules the checker enforces:
 *   - id: kebab-case, unique, stable (it appears in URLs)
 *   - states: at least one; keys kebab-case and unique per component
 *   - a state may declare  via: "props"  when the renderer takes no branch on its key and the
 *     difference lives entirely in props (value/error/disabled data). The checker then verifies the
 *     props differ instead of demanding a dead if-branch - gaming a check is not implementing a state.
 *   - props: keyed by state key — an unknown key is a typo and fails
 *   - renderer: the id of the renderer implemented in js/components/ (or the story-local map)
 *   - facets: only the declared facet names and values may appear in a URL
 *
 * Copy the shape, replace the content with the project's real components and real subject matter.
 * Never Lorem, never "Item 1" — a card with fake copy hides real layout bugs.
 */

export const meta = {
  title: "كتالوج المكوّنات",
  caption: "كل حالة لها renderer مستقل و descriptor مشتق من الـ props.",
  // Global switches. These are facets, not states: they change the whole gallery, not one card.
  facets: {
    dir: ["rtl", "ltr"],
    theme: ["light", "dark", "system"],
    density: ["comfortable", "compact"],
  },
  defaults: { dir: "rtl", theme: "system", density: "comfortable" },
};

export const components = [
  {
    id: "toggle",
    name: "مفتاح",
    renderer: "toggle",
    caption: "قيمة منطقية واحدة، تتبدّل فورًا دون انتظار حفظ.",
    states: [
      { key: "valid", via: "props", label: "صحيح" },
      { key: "disabled", label: "معطل", note: "قراءة فقط أثناء المزامنة" },
      { key: "required-off", label: "إيقاف مطلوب", note: "يُمنع الإطفاء ويظهر السبب" },
    ],
    props: {
      valid: { on: true, label: "تتبع المشاريع المفعلة" },
      disabled: { on: false, label: "تتبع المشاريع المفعلة" },
      "required-off": { on: false, label: "تجميع التنبيهات", hint: "مفتاح على مستوى النظام فقط" },
    },
  },
  {
    id: "numeric-field",
    name: "رقم ذو حدين",
    renderer: "numeric-field",
    caption: "min/max/step من الـ descriptor، ورسالة الخطأ جزء من الحالة.",
    states: [
      { key: "valid", via: "props", label: "صحيح" },
      { key: "empty", via: "props", label: "فارغ" },
      { key: "invalid", label: "خطأ", note: "القيمة خارج الحد الأعلى" },
      { key: "disabled", label: "معطل" },
    ],
    props: {
      valid: { value: 30, unit: "ثانية", min: 0, max: 3600 },
      empty: { value: null, unit: "طلب/دقيقة", min: 1, max: 60 },
      invalid: { value: 5000, unit: "ثانية", min: 10, max: 3600, error: "القيمة يجب أن تكون بين 10 و3600" },
      disabled: { value: 4, unit: "بانتظار", min: 1, max: 10 },
    },
  },
  {
    id: "text-entry",
    name: "نص",
    renderer: "text-entry",
    caption: "إدخال نص قصير داخل واجهة عربية.",
    states: [
      { key: "valid", via: "props", label: "صحيح" },
      { key: "invalid", label: "خطأ", note: "يرفض الوسوم ولا يمررها" },
      { key: "long", via: "props", label: "نص طويل", note: "الالتفاف لا القص" },
    ],
    props: {
      valid: { value: "category=development&sort=latest", label: "معاملات البحث" },
      invalid: { value: "q<<script>", label: "معاملات البحث", error: "الرمز '<' غير مسموح في روابط المعاملات" },
      long: { value: "تقرير أداء الحملة التسويقية للربع المالي الأول مع مقارنة سنوية", label: "العنوان" },
    },
  },
  {
    id: "slider",
    name: "مؤشر متدرج",
    renderer: "slider",
    caption: "مدى محدود مع قيمة حية بجانب المقبض.",
    states: [
      { key: "valid", via: "props", label: "صحيح" },
      { key: "disabled", label: "معطل" },
      { key: "min", via: "props", label: "أدنى القيمة" },
    ],
    props: {
      valid: { value: 12, min: 0, max: 60, label: "سقف الطلبات في الدقيقة" },
      disabled: { value: 30, min: 0, max: 60, label: "سقف الطلبات في الدقيقة" },
      min: { value: 0, min: 0, max: 60, label: "سقف الطلبات في الدقيقة" },
    },
  },
  {
    id: "file-picker",
    name: "اختيار ملف",
    renderer: "file-picker",
    caption: "اسم الملف فقط يظهر، والمحتوى لا يُقرأ في المتصفح.",
    states: [
      { key: "empty", via: "props", label: "فارغ" },
      { key: "selected", via: "props", label: "ملف محدد" },
      { key: "invalid", via: "props", label: "نوع مرفوض" },
    ],
    props: {
      empty: { label: "ملف الجلسة", hint: "لم يتم اختيار ملف بعد" },
      selected: { label: "ملف الجلسة", file: "cookies.txt", action: "تغيير" },
      invalid: { label: "ملف الجلسة", file: "session.exe", error: "النوع غير مدعوم" },
    },
  },
];
