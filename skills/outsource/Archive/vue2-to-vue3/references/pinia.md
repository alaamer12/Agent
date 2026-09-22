# Vuex to Pinia Migration Guide

## Table of Contents
1. [Why Pinia](#why-pinia)
2. [Store Setup](#store-setup)
3. [State](#state)
4. [Getters](#getters)
5. [Actions (and Mutations)](#actions-and-mutations)
6. [Component Usage](#component-usage)
7. [Modules to Stores](#modules-to-stores)
8. [Plugins](#plugins)

---

## Why Pinia

- Official recommended state management for Vue 3
- Full TypeScript support
- No mutations (simpler API)
- No nested modules (flat store structure)
- Devtools support
- Smaller bundle size

---

## Store Setup

### Vuex 3/4 Store
```js
// store/index.js
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    INCREMENT(state) {
      state.count++
    }
  },
  actions: {
    increment({ commit }) {
      commit('INCREMENT')
    }
  },
  getters: {
    doubleCount: state => state.count * 2
  }
})

// main.js
import store from './store'
new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
```

### Pinia Store
```js
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),
  getters: {
    doubleCount: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++
    }
  }
})

// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
```

### Pinia Store (Composition API Style)
```js
// stores/counter.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  // state
  const count = ref(0)

  // getters
  const doubleCount = computed(() => count.value * 2)

  // actions
  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})
```

---

## State

### Vuex State
```js
// store/index.js
state: {
  user: null,
  items: [],
  loading: false
}

// component access
this.$store.state.user
this.$store.state.items

// with mapState
import { mapState } from 'vuex'
computed: {
  ...mapState(['user', 'items']),
  ...mapState({
    currentUser: 'user',
    allItems: 'items'
  })
}
```

### Pinia State
```js
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    items: [],
    loading: false
  })
})

// component access
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()

// Direct access
userStore.user
userStore.items

// Reactive destructuring (for use in template)
const { user, items } = storeToRefs(userStore)

// $patch for batch updates
userStore.$patch({
  user: { name: 'John' },
  loading: false
})

// $patch with function
userStore.$patch((state) => {
  state.items.push(newItem)
  state.loading = false
})
```

---

## Getters

### Vuex Getters
```js
// store/index.js
getters: {
  activeItems: state => state.items.filter(i => i.active),
  itemById: state => id => state.items.find(i => i.id === id),
  // access other getters
  activeCount: (state, getters) => getters.activeItems.length
}

// component
this.$store.getters.activeItems
this.$store.getters.itemById(123)

// mapGetters
import { mapGetters } from 'vuex'
computed: {
  ...mapGetters(['activeItems', 'itemById'])
}
```

### Pinia Getters
```js
// stores/items.js
export const useItemsStore = defineStore('items', {
  state: () => ({
    items: []
  }),
  getters: {
    activeItems: (state) => state.items.filter(i => i.active),
    // getter that returns function
    itemById: (state) => (id) => state.items.find(i => i.id === id),
    // access other getters via this
    activeCount() {
      return this.activeItems.length
    }
  }
})

// component
const itemsStore = useItemsStore()
itemsStore.activeItems
itemsStore.itemById(123)

// reactive destructuring
const { activeItems } = storeToRefs(itemsStore)
```

---

## Actions (and Mutations)

### Vuex Mutations + Actions
```js
// store/index.js
mutations: {
  SET_USER(state, user) {
    state.user = user
  },
  SET_LOADING(state, value) {
    state.loading = value
  }
},
actions: {
  async fetchUser({ commit }, userId) {
    commit('SET_LOADING', true)
    try {
      const user = await api.getUser(userId)
      commit('SET_USER', user)
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

// component
this.$store.dispatch('fetchUser', 123)

// mapActions
import { mapActions } from 'vuex'
methods: {
  ...mapActions(['fetchUser'])
}
```

### Pinia Actions (No Mutations!)
```js
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    loading: false
  }),
  actions: {
    async fetchUser(userId) {
      this.loading = true
      try {
        this.user = await api.getUser(userId)
      } finally {
        this.loading = false
      }
    }
  }
})

// component
const userStore = useUserStore()
await userStore.fetchUser(123)

// Actions can call other actions
actions: {
  async fetchAndProcess(id) {
    await this.fetchUser(id)
    this.processUser()
  }
}

// Access other stores in actions
import { useOtherStore } from './other'
actions: {
  async complexAction() {
    const otherStore = useOtherStore()
    await otherStore.doSomething()
    this.localAction()
  }
}
```

---

## Component Usage

### Vuex in Options API
```vue
<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapState(['user', 'loading']),
    ...mapGetters(['isLoggedIn'])
  },
  methods: {
    ...mapActions(['fetchUser', 'logout'])
  },
  created() {
    this.fetchUser(this.$route.params.id)
  }
}
</script>
```

### Pinia in Options API
```vue
<script>
import { mapState, mapActions } from 'pinia'
import { useUserStore } from '@/stores/user'

export default {
  computed: {
    ...mapState(useUserStore, ['user', 'loading']),
    ...mapState(useUserStore, {
      myUser: 'user'
    })
  },
  methods: {
    ...mapActions(useUserStore, ['fetchUser', 'logout'])
  },
  created() {
    this.fetchUser(this.$route.params.id)
  }
}
</script>
```

### Pinia in Composition API
```vue
<script setup>
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()

// Destructure state/getters with storeToRefs for reactivity
const { user, loading, isLoggedIn } = storeToRefs(userStore)

// Actions can be destructured directly (not reactive)
const { fetchUser, logout } = userStore

onMounted(() => {
  fetchUser(route.params.id)
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else>{{ user.name }}</div>
</template>
```

---

## Modules to Stores

### Vuex Modules
```js
// store/modules/user.js
export default {
  namespaced: true,
  state: () => ({ user: null }),
  mutations: { SET_USER(state, user) { state.user = user } },
  actions: { fetchUser({ commit }) { /* ... */ } }
}

// store/modules/cart.js
export default {
  namespaced: true,
  state: () => ({ items: [] }),
  // ...
}

// store/index.js
import user from './modules/user'
import cart from './modules/cart'

export default new Vuex.Store({
  modules: { user, cart }
})

// Usage
this.$store.state.user.user
this.$store.dispatch('user/fetchUser')
this.$store.dispatch('cart/addItem', item)
```

### Pinia Stores (Flat Structure)
```js
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({ user: null }),
  actions: {
    async fetchUser() { /* ... */ }
  }
})

// stores/cart.js
export const useCartStore = defineStore('cart', {
  state: () => ({ items: [] }),
  actions: {
    addItem(item) {
      this.items.push(item)
    }
  }
})

// Usage - import specific stores
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

const userStore = useUserStore()
const cartStore = useCartStore()

userStore.fetchUser()
cartStore.addItem(item)
```

### Cross-Store Communication
```js
// stores/cart.js
import { useUserStore } from './user'

export const useCartStore = defineStore('cart', {
  actions: {
    async checkout() {
      const userStore = useUserStore()
      if (!userStore.isLoggedIn) {
        throw new Error('Must be logged in')
      }
      // proceed with checkout
    }
  }
})
```

---

## Plugins

### Vuex Plugin
```js
// plugins/logger.js
export default function createLogger() {
  return store => {
    store.subscribe((mutation, state) => {
      console.log('Mutation:', mutation.type)
      console.log('Payload:', mutation.payload)
    })
  }
}

// store/index.js
import createLogger from './plugins/logger'

export default new Vuex.Store({
  plugins: [createLogger()]
})
```

### Pinia Plugin
```js
// plugins/logger.js
export function loggerPlugin({ store }) {
  store.$subscribe((mutation, state) => {
    console.log('Store:', store.$id)
    console.log('Mutation type:', mutation.type)
    console.log('State:', state)
  })
}

// main.js
import { createPinia } from 'pinia'
import { loggerPlugin } from './plugins/logger'

const pinia = createPinia()
pinia.use(loggerPlugin)

// Pinia plugin with context
export function myPlugin(context) {
  context.pinia    // the pinia instance
  context.app      // the Vue app
  context.store    // the store being extended
  context.options  // the options passed to defineStore

  // Add properties to all stores
  return {
    secret: 'my secret'
  }
}

// Pinia plugin for persistence
import { watch } from 'vue'

export function persistPlugin({ store }) {
  const key = `pinia-${store.$id}`

  // Restore
  const saved = localStorage.getItem(key)
  if (saved) {
    store.$patch(JSON.parse(saved))
  }

  // Persist on change
  watch(
    () => store.$state,
    (state) => {
      localStorage.setItem(key, JSON.stringify(state))
    },
    { deep: true }
  )
}
```
