# Vue CLI to Vite Migration Guide

## Table of Contents
1. [Quick Migration Steps](#quick-migration-steps)
2. [Configuration Mapping](#configuration-mapping)
3. [Environment Variables](#environment-variables)
4. [Path Aliases](#path-aliases)
5. [CSS Preprocessing](#css-preprocessing)
6. [Static Assets](#static-assets)
7. [Build Output](#build-output)
8. [Common Issues](#common-issues)

---

## Quick Migration Steps

### 1. Update package.json

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### 2. Install Dependencies

```bash
# Remove Vue CLI
npm uninstall @vue/cli-service @vue/cli-plugin-*

# Install Vite
npm install -D vite @vitejs/plugin-vue

# If using Vue 2
npm install -D @vitejs/plugin-vue2
```

### 3. Create vite.config.js

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
```

### 4. Move index.html

Move `public/index.html` to project root and update:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>My App</title>
</head>
<body>
  <div id="app"></div>
  <!-- Add script module -->
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

### 5. Update Entry File

```js
// src/main.js (Vue 3)
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

---

## Configuration Mapping

### vue.config.js → vite.config.js

```js
// vue.config.js (Vue CLI)
module.exports = {
  publicPath: '/my-app/',
  outputDir: 'dist',
  assetsDir: 'static',
  devServer: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  css: {
    loaderOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  chainWebpack: config => {
    config.resolve.alias.set('@', path.resolve(__dirname, 'src'))
  }
}

// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: '/my-app/',
  build: {
    outDir: 'dist',
    assetsDir: 'static'
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  plugins: [vue()]
})
```

---

## Environment Variables

### Vue CLI (.env files)
```bash
# .env
VUE_APP_API_URL=https://api.example.com
VUE_APP_TITLE=My App

# Usage in code
process.env.VUE_APP_API_URL
process.env.VUE_APP_TITLE
```

### Vite (.env files)
```bash
# .env
VITE_API_URL=https://api.example.com
VITE_TITLE=My App

# Usage in code
import.meta.env.VITE_API_URL
import.meta.env.VITE_TITLE

# Built-in variables
import.meta.env.MODE        # 'development' or 'production'
import.meta.env.BASE_URL    # base URL from config
import.meta.env.PROD        // true in production
import.meta.env.DEV         // true in development
```

### Migration Search & Replace

```
process.env.VUE_APP_  →  import.meta.env.VITE_
process.env.NODE_ENV  →  import.meta.env.MODE
process.env.BASE_URL  →  import.meta.env.BASE_URL
```

---

## Path Aliases

### Vue CLI (tsconfig.json / jsconfig.json)
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"]
    }
  }
}
```

### Vite
```js
// vite.config.js
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components')
    }
  }
})
```

For TypeScript, also update tsconfig.json:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"]
    }
  }
}
```

---

## CSS Preprocessing

### Vue CLI
```js
// vue.config.js
module.exports = {
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/styles/variables.scss";`
      },
      less: {
        lessOptions: {
          modifyVars: {
            'primary-color': '#1890ff'
          },
          javascriptEnabled: true
        }
      }
    }
  }
}
```

### Vite
```js
// vite.config.js
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      },
      less: {
        modifyVars: {
          'primary-color': '#1890ff'
        },
        javascriptEnabled: true
      }
    }
  }
})
```

Install preprocessors:
```bash
# SCSS
npm install -D sass

# Less
npm install -D less

# Stylus
npm install -D stylus
```

---

## Static Assets

### Vue CLI
- Place in `public/` folder
- Reference with absolute paths: `/favicon.ico`
- Access in templates: `<%= BASE_URL %>favicon.ico`

### Vite
- Place in `public/` folder (same behavior)
- Reference with absolute paths: `/favicon.ico`
- No template syntax in HTML

### Asset Imports

```js
// Vue CLI & Vite - both support
import imgUrl from '@/assets/logo.png'

// Vite - explicit URL import
import imgUrl from '@/assets/logo.png?url'

// Vite - raw string import
import raw from '@/assets/file.txt?raw'
```

---

## Build Output

### Vue CLI (GitHub Pages)
```js
// vue.config.js
module.exports = {
  publicPath: process.env.NODE_ENV === 'production'
    ? '/my-repo/'
    : '/',
  outputDir: 'docs'  // For GitHub Pages
}
```

### Vite (GitHub Pages)
```js
// vite.config.js
export default defineConfig({
  base: '/my-repo/',
  build: {
    outDir: 'docs'
  }
})
```

### Build Commands

```bash
# Vue CLI
npm run build

# Vite
npm run build     # Production build
npm run preview   # Preview production build locally
```

---

## Common Issues

### 1. require() Not Supported

```js
// Vue CLI (works)
const img = require('@/assets/logo.png')

// Vite (ESM only)
import img from '@/assets/logo.png'

// Dynamic imports
const modules = import.meta.glob('@/modules/*.js')
```

### 2. CommonJS Dependencies

Some packages may need optimization:
```js
// vite.config.js
export default defineConfig({
  optimizeDeps: {
    include: ['some-cjs-package']
  }
})
```

### 3. Global SCSS Variables

```js
// vite.config.js
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "@/styles/_variables.scss";
          @import "@/styles/_mixins.scss";
        `
      }
    }
  }
})
```

### 4. index.html Template Variables

```html
<!-- Vue CLI -->
<title><%= htmlWebpackPlugin.options.title %></title>

<!-- Vite - use vite-plugin-html or hardcode -->
<title>My App</title>
```

Or use vite-plugin-html:
```js
import { createHtmlPlugin } from 'vite-plugin-html'

export default defineConfig({
  plugins: [
    vue(),
    createHtmlPlugin({
      inject: {
        data: {
          title: 'My App'
        }
      }
    })
  ]
})
```

### 5. Polyfills

```bash
# Install polyfill plugin
npm install -D @vitejs/plugin-legacy
```

```js
// vite.config.js
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  plugins: [
    vue(),
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ]
})
```

---

## File Changes Checklist

- [ ] Create `vite.config.js` in project root
- [ ] Move `public/index.html` to project root
- [ ] Add `<script type="module" src="/src/main.js">` to index.html
- [ ] Rename `.env` variables: `VUE_APP_*` → `VITE_*`
- [ ] Update code: `process.env.VUE_APP_*` → `import.meta.env.VITE_*`
- [ ] Replace `require()` with `import`
- [ ] Update `package.json` scripts
- [ ] Remove Vue CLI dependencies
- [ ] Install Vite dependencies
- [ ] Delete `vue.config.js` (after migration)
