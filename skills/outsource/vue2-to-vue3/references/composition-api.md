# Options API to Composition API Migration

## Table of Contents
1. [Basic Conversion Pattern](#basic-conversion-pattern)
2. [Data and Refs](#data-and-refs)
3. [Computed Properties](#computed-properties)
4. [Methods](#methods)
5. [Watchers](#watchers)
6. [Lifecycle Hooks](#lifecycle-hooks)
7. [Props and Emit](#props-and-emit)
8. [Provide/Inject](#provideinject)
9. [Template Refs](#template-refs)

---

## Basic Conversion Pattern

### Options API (Vue 2)
```vue
<script>
export default {
  data() {
    return {
      count: 0,
      message: 'Hello'
    }
  },
  computed: {
    doubleCount() {
      return this.count * 2
    }
  },
  methods: {
    increment() {
      this.count++
    }
  },
  mounted() {
    console.log('Component mounted')
  }
}
</script>
```

### Composition API (Vue 3 `<script setup>`)
```vue
<script setup>
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const message = ref('Hello')

const doubleCount = computed(() => count.value * 2)

function increment() {
  count.value++
}

onMounted(() => {
  console.log('Component mounted')
})
</script>
```

---

## Data and Refs

### Primitive Values → `ref()`
```js
// Vue 2
data() {
  return {
    count: 0,
    name: 'John',
    isActive: true
  }
}

// Vue 3
import { ref } from 'vue'
const count = ref(0)
const name = ref('John')
const isActive = ref(true)

// Access in script: count.value
// Access in template: {{ count }} (auto-unwrap)
```

### Objects/Arrays → `reactive()` or `ref()`
```js
// Vue 2
data() {
  return {
    user: { name: 'John', age: 30 },
    items: []
  }
}

// Vue 3 Option 1: reactive (no .value needed for properties)
import { reactive } from 'vue'
const user = reactive({ name: 'John', age: 30 })
const items = reactive([])
// Access: user.name, items.push(item)

// Vue 3 Option 2: ref (more flexible, can reassign entire object)
import { ref } from 'vue'
const user = ref({ name: 'John', age: 30 })
const items = ref([])
// Access: user.value.name, items.value.push(item)
```

### When to use `ref` vs `reactive`
- Use `ref` for primitives and when you need to reassign the entire value
- Use `reactive` for objects that won't be reassigned
- `ref` is more flexible and commonly preferred

---

## Computed Properties

```js
// Vue 2
computed: {
  fullName() {
    return `${this.firstName} ${this.lastName}`
  },
  // Writable computed
  fullNameWritable: {
    get() {
      return `${this.firstName} ${this.lastName}`
    },
    set(value) {
      const [first, last] = value.split(' ')
      this.firstName = first
      this.lastName = last
    }
  }
}

// Vue 3
import { computed } from 'vue'

const fullName = computed(() => `${firstName.value} ${lastName.value}`)

// Writable computed
const fullNameWritable = computed({
  get: () => `${firstName.value} ${lastName.value}`,
  set: (value) => {
    const [first, last] = value.split(' ')
    firstName.value = first
    lastName.value = last
  }
})
```

---

## Methods

```js
// Vue 2
methods: {
  async fetchData() {
    this.loading = true
    try {
      this.data = await api.get('/data')
    } finally {
      this.loading = false
    }
  },
  handleClick(event) {
    console.log(event.target)
  }
}

// Vue 3 - Just regular functions
const loading = ref(false)
const data = ref(null)

async function fetchData() {
  loading.value = true
  try {
    data.value = await api.get('/data')
  } finally {
    loading.value = false
  }
}

function handleClick(event) {
  console.log(event.target)
}
```

---

## Watchers

```js
// Vue 2
watch: {
  // Simple watch
  searchQuery(newVal, oldVal) {
    this.doSearch(newVal)
  },
  // Deep watch
  user: {
    handler(newVal) {
      this.saveUser(newVal)
    },
    deep: true,
    immediate: true
  },
  // Watch nested property
  'user.name'(newVal) {
    console.log('Name changed:', newVal)
  }
}

// Vue 3
import { watch, watchEffect } from 'vue'

// Simple watch
watch(searchQuery, (newVal, oldVal) => {
  doSearch(newVal)
})

// Deep watch with immediate
watch(
  user,
  (newVal) => {
    saveUser(newVal)
  },
  { deep: true, immediate: true }
)

// Watch nested property (getter function)
watch(
  () => user.value.name,
  (newVal) => {
    console.log('Name changed:', newVal)
  }
)

// Watch multiple sources
watch(
  [firstName, lastName],
  ([newFirst, newLast], [oldFirst, oldLast]) => {
    console.log('Name changed')
  }
)

// watchEffect - auto-tracks dependencies
watchEffect(() => {
  console.log('Count is:', count.value)
  // Runs immediately and re-runs when count changes
})
```

---

## Lifecycle Hooks

| Vue 2 | Vue 3 Composition API |
|-------|----------------------|
| `beforeCreate` | Not needed (use `setup`) |
| `created` | Not needed (use `setup`) |
| `beforeMount` | `onBeforeMount` |
| `mounted` | `onMounted` |
| `beforeUpdate` | `onBeforeUpdate` |
| `updated` | `onUpdated` |
| `beforeDestroy` | `onBeforeUnmount` |
| `destroyed` | `onUnmounted` |
| `activated` | `onActivated` |
| `deactivated` | `onDeactivated` |
| `errorCaptured` | `onErrorCaptured` |

```js
// Vue 2
export default {
  created() {
    this.fetchData()
  },
  mounted() {
    this.initChart()
  },
  beforeDestroy() {
    this.cleanup()
  }
}

// Vue 3
import { onMounted, onBeforeUnmount } from 'vue'

// created logic runs directly in setup/<script setup>
fetchData()

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  cleanup()
})
```

---

## Props and Emit

```vue
<!-- Vue 2 -->
<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    },
    count: {
      type: Number,
      default: 0
    }
  },
  methods: {
    submit() {
      this.$emit('submit', this.formData)
    }
  }
}
</script>

<!-- Vue 3 <script setup> -->
<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['submit', 'update'])

function submit() {
  emit('submit', formData.value)
}
</script>

<!-- Vue 3 with TypeScript -->
<script setup lang="ts">
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

const emit = defineEmits<{
  submit: [data: FormData]
  update: [value: string]
}>()
</script>
```

---

## Provide/Inject

```js
// Vue 2 - Provider
export default {
  provide() {
    return {
      theme: this.theme,
      // Not reactive by default!
    }
  }
}

// Vue 2 - Consumer
export default {
  inject: ['theme']
}

// Vue 3 - Provider (reactive by default with ref/reactive)
import { provide, ref } from 'vue'

const theme = ref('dark')
provide('theme', theme)  // Reactive!

// Provide readonly to prevent mutation
import { provide, readonly, ref } from 'vue'
const theme = ref('dark')
provide('theme', readonly(theme))

// Vue 3 - Consumer
import { inject } from 'vue'

const theme = inject('theme')
// With default value
const theme = inject('theme', 'light')
```

---

## Template Refs

```vue
<!-- Vue 2 -->
<template>
  <input ref="inputEl" />
</template>
<script>
export default {
  mounted() {
    this.$refs.inputEl.focus()
  }
}
</script>

<!-- Vue 3 -->
<template>
  <input ref="inputEl" />
</template>
<script setup>
import { ref, onMounted } from 'vue'

const inputEl = ref(null)

onMounted(() => {
  inputEl.value.focus()
})
</script>
```

---

## Composables (Replacing Mixins)

```js
// Vue 2 Mixin
// mixins/useMouse.js
export default {
  data() {
    return {
      x: 0,
      y: 0
    }
  },
  mounted() {
    window.addEventListener('mousemove', this.update)
  },
  beforeDestroy() {
    window.removeEventListener('mousemove', this.update)
  },
  methods: {
    update(e) {
      this.x = e.pageX
      this.y = e.pageY
    }
  }
}

// Usage
import useMouse from '@/mixins/useMouse'
export default {
  mixins: [useMouse]
}

// Vue 3 Composable
// composables/useMouse.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function update(e) {
    x.value = e.pageX
    y.value = e.pageY
  }

  onMounted(() => window.addEventListener('mousemove', update))
  onUnmounted(() => window.removeEventListener('mousemove', update))

  return { x, y }
}

// Usage
import { useMouse } from '@/composables/useMouse'
const { x, y } = useMouse()
```
