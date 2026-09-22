# Vue Router 3 to 4 Migration Guide

## Table of Contents
1. [Router Creation](#router-creation)
2. [History Mode](#history-mode)
3. [Route Configuration](#route-configuration)
4. [Navigation Guards](#navigation-guards)
5. [Composition API Usage](#composition-api-usage)
6. [Breaking Changes](#breaking-changes)

---

## Router Creation

### Vue Router 3 (Vue 2)
```js
import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/views/Home.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    { path: '/', component: Home }
  ]
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
```

### Vue Router 4 (Vue 3)
```js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
```

---

## History Mode

### Vue Router 3
```js
const router = new VueRouter({
  mode: 'history',  // or 'hash' or 'abstract'
  base: '/app/'
})
```

### Vue Router 4
```js
import {
  createRouter,
  createWebHistory,
  createWebHashHistory,
  createMemoryHistory
} from 'vue-router'

// History mode
const router = createRouter({
  history: createWebHistory('/app/')
})

// Hash mode
const router = createRouter({
  history: createWebHashHistory()
})

// Memory mode (for SSR)
const router = createRouter({
  history: createMemoryHistory()
})
```

---

## Route Configuration

### Catch-all Routes
```js
// Vue Router 3
{ path: '*', component: NotFound }
{ path: '/user-*', component: UserGeneric }

// Vue Router 4 - Must use parameter with regex
{ path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
{ path: '/user-:afterUser(.*)', component: UserGeneric }
```

### Named Routes with params
```js
// Vue Router 3 - Optional params with ?
{ path: '/users/:id?' }

// Vue Router 4 - Same syntax, but stricter
{ path: '/users/:id?' }

// Repeatable params
{ path: '/users/:id+' }  // One or more
{ path: '/users/:id*' }  // Zero or more
```

### redirect and alias
```js
// Both versions - redirect function receives route
{
  path: '/old/:id',
  redirect: to => ({ name: 'new', params: { id: to.params.id } })
}

// Vue Router 4 - redirect can return relative path
{
  path: '/old/:id',
  redirect: to => `../new/${to.params.id}`
}
```

---

## Navigation Guards

### Global Guards
```js
// Vue Router 3
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

// Vue Router 4 - next is optional, return value controls navigation
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isLoggedIn) {
    return '/login'
    // or return { name: 'Login' }
    // or return false to cancel
  }
  // returning nothing or true allows navigation
})

// Vue Router 4 - still supports next() for compatibility
router.beforeEach((to, from, next) => {
  // same as v3
})
```

### Per-Route Guards
```js
// Vue Router 3
{
  path: '/admin',
  component: Admin,
  beforeEnter: (to, from, next) => {
    if (!isAdmin) next('/forbidden')
    else next()
  }
}

// Vue Router 4
{
  path: '/admin',
  component: Admin,
  beforeEnter: (to, from) => {
    if (!isAdmin) return '/forbidden'
  }
}
```

### In-Component Guards
```js
// Vue 2 Options API
export default {
  beforeRouteEnter(to, from, next) {
    next(vm => {
      // access component instance via vm
    })
  },
  beforeRouteUpdate(to, from, next) {
    this.fetchData(to.params.id)
    next()
  },
  beforeRouteLeave(to, from, next) {
    if (this.hasUnsavedChanges) {
      if (!confirm('Discard changes?')) {
        next(false)
        return
      }
    }
    next()
  }
}

// Vue 3 Composition API
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

onBeforeRouteUpdate((to, from) => {
  fetchData(to.params.id)
})

onBeforeRouteLeave((to, from) => {
  if (hasUnsavedChanges.value) {
    if (!confirm('Discard changes?')) {
      return false
    }
  }
})

// Note: beforeRouteEnter has no Composition API equivalent
// Use onMounted + route params instead
```

---

## Composition API Usage

### useRouter and useRoute
```vue
<!-- Vue 2 Options API -->
<script>
export default {
  methods: {
    goHome() {
      this.$router.push('/')
    }
  },
  computed: {
    userId() {
      return this.$route.params.id
    }
  }
}
</script>

<!-- Vue 3 Composition API -->
<script setup>
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

function goHome() {
  router.push('/')
}

const userId = computed(() => route.params.id)
</script>
```

### RouterLink
```vue
<!-- Vue Router 3 -->
<router-link :to="{ name: 'User', params: { id: 1 }}" tag="button">
  Go to User
</router-link>

<!-- Vue Router 4 - tag removed, use v-slot instead -->
<router-link :to="{ name: 'User', params: { id: 1 }}" custom v-slot="{ navigate }">
  <button @click="navigate">Go to User</button>
</router-link>

<!-- Or simpler with component wrapping -->
<router-link :to="{ name: 'User', params: { id: 1 }}">
  <button>Go to User</button>
</router-link>
```

---

## Breaking Changes

### 1. Missing required params throws error
```js
// Vue Router 3 - silently fails
router.push({ name: 'User' }) // missing :id param

// Vue Router 4 - throws error
router.push({ name: 'User' }) // Error: Missing required param "id"
```

### 2. Empty path children require named routes
```js
// Vue Router 3
{
  path: '/parent',
  children: [
    { path: '', component: ParentDefault }
  ]
}

// Vue Router 4 - name required for empty path child
{
  path: '/parent',
  children: [
    { path: '', name: 'ParentDefault', component: ParentDefault }
  ]
}
```

### 3. router.match removed
```js
// Vue Router 3
const match = router.match('/users/1')

// Vue Router 4
const match = router.resolve('/users/1')
```

### 4. scrollBehavior changes
```js
// Vue Router 3
scrollBehavior(to, from, savedPosition) {
  if (savedPosition) {
    return savedPosition
  } else {
    return { x: 0, y: 0 }
  }
}

// Vue Router 4 - use left/top instead of x/y
scrollBehavior(to, from, savedPosition) {
  if (savedPosition) {
    return savedPosition
  } else {
    return { left: 0, top: 0 }
  }
}
```

### 5. Keep-alive and transition on RouterView
```vue
<!-- Vue Router 3 -->
<transition>
  <keep-alive>
    <router-view />
  </keep-alive>
</transition>

<!-- Vue Router 4 - must use slot -->
<router-view v-slot="{ Component }">
  <transition>
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </transition>
</router-view>
```

### 6. Navigation failures
```js
// Vue Router 4 - navigation returns promise with failure info
import { NavigationFailureType, isNavigationFailure } from 'vue-router'

router.push('/admin').catch(failure => {
  if (isNavigationFailure(failure, NavigationFailureType.aborted)) {
    // Navigation was aborted
  }
})

// Or with async/await
const failure = await router.push('/admin')
if (failure) {
  // handle failure
}
```
