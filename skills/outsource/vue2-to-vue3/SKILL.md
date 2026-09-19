---
name: vue2-to-vue3
description: |
  Complete Vue 2 to Vue 3 migration toolkit with automated analysis and step-by-step guidance. Use this skill when: (1) Upgrading a Vue 2 project to Vue 3, (2) Converting Options API to Composition API, (3) Migrating Vue Router 3 to 4, (4) Migrating Vuex to Pinia, (5) Converting Vue CLI project to Vite, (6) Analyzing Vue 2 codebase for breaking changes, (7) User asks about Vue 2/3 differences or migration strategy.
---

# Vue 2 to Vue 3 Migration Skill

## Quick Start

### 1. Analyze Project
Run the analysis script to identify migration issues:
```bash
python scripts/analyze-vue2.py /path/to/vue2-project
```

Output JSON format for programmatic use:
```bash
python scripts/analyze-vue2.py /path/to/vue2-project --json
```

### 2. Review Breaking Changes
The analyzer categorizes issues by severity:
- **Breaking** (must fix): Removed APIs, renamed hooks, syntax changes
- **Warning** (review): Changed behavior, deprecated patterns
- **Info** (optional): Composition API conversion opportunities

---

## Migration Workflow

### Phase 1: Preparation
1. Run `analyze-vue2.py` to get migration report
2. Update Node.js to v16+ (required for Vue 3)
3. Ensure all dependencies have Vue 3 compatible versions

### Phase 2: Core Migration
Execute in order:

1. **Update build tooling**
   - Vue CLI → Vite: See [references/vite.md](references/vite.md)

2. **Update Vue core**
   ```bash
   npm install vue@3
   npm install -D @vitejs/plugin-vue
   ```

3. **Update entry point** (main.js)
   ```js
   // Before (Vue 2)
   import Vue from 'vue'
   new Vue({ render: h => h(App) }).$mount('#app')

   // After (Vue 3)
   import { createApp } from 'vue'
   createApp(App).mount('#app')
   ```

4. **Fix breaking changes** identified by analyzer

### Phase 3: Ecosystem Migration
- Vue Router 3→4: See [references/vue-router.md](references/vue-router.md)
- Vuex→Pinia: See [references/pinia.md](references/pinia.md)

### Phase 4: Composition API (Optional)
Convert components from Options API to Composition API:
- See [references/composition-api.md](references/composition-api.md)

---

## Critical Breaking Changes

### Global API
| Vue 2 | Vue 3 |
|-------|-------|
| `new Vue()` | `createApp()` |
| `Vue.component()` | `app.component()` |
| `Vue.directive()` | `app.directive()` |
| `Vue.mixin()` | `app.mixin()` |
| `Vue.use()` | `app.use()` |
| `Vue.prototype.$x` | `app.config.globalProperties.$x` |

### Lifecycle Hooks
| Vue 2 | Vue 3 |
|-------|-------|
| `beforeDestroy` | `beforeUnmount` |
| `destroyed` | `unmounted` |

### Removed Features
- **Filters**: Use computed or methods
- **$on/$off/$once**: Use mitt or tiny-emitter
- **$children**: Use template refs
- **$listeners**: Merged into $attrs
- **$scopedSlots**: Use $slots (all slots are functions)
- **.sync modifier**: Use v-model:propName

### Template Changes
- **v-model**: prop `value`→`modelValue`, event `input`→`update:modelValue`
- **v-if/v-for precedence**: v-if now has higher precedence
- **Transition classes**: `v-enter`→`v-enter-from`, `v-leave`→`v-leave-from`
- **key on template v-for**: Now required on `<template>` tag

---

## Reference Guides

| Topic | File |
|-------|------|
| Options→Composition API | [references/composition-api.md](references/composition-api.md) |
| Vue Router 3→4 | [references/vue-router.md](references/vue-router.md) |
| Vuex→Pinia | [references/pinia.md](references/pinia.md) |
| Vue CLI→Vite | [references/vite.md](references/vite.md) |

---

## Common Patterns

### Convert a Component

```vue
<!-- Vue 2 Options API -->
<script>
export default {
  props: ['title'],
  data() {
    return { count: 0 }
  },
  computed: {
    doubled() { return this.count * 2 }
  },
  methods: {
    increment() { this.count++ }
  },
  mounted() {
    console.log('mounted')
  }
}
</script>

<!-- Vue 3 Composition API -->
<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps(['title'])
const count = ref(0)
const doubled = computed(() => count.value * 2)

function increment() {
  count.value++
}

onMounted(() => {
  console.log('mounted')
})
</script>
```

### Event Bus Replacement

```js
// Vue 2 - Event Bus
const bus = new Vue()
bus.$on('event', handler)
bus.$emit('event', data)

// Vue 3 - Use mitt
import mitt from 'mitt'
const emitter = mitt()
emitter.on('event', handler)
emitter.emit('event', data)
```

### Filters to Computed/Methods

```vue
<!-- Vue 2 -->
<template>
  {{ price | currency }}
</template>
<script>
filters: {
  currency(val) { return '$' + val.toFixed(2) }
}
</script>

<!-- Vue 3 -->
<template>
  {{ formatCurrency(price) }}
</template>
<script setup>
function formatCurrency(val) {
  return '$' + val.toFixed(2)
}
</script>
```
