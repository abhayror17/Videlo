import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Views
import Home from './views/Home.vue'
import ImageEdit from './views/ImageEdit.vue'
import AdGenerator from './views/AdGenerator.vue'

const routes = [
  {
    path: '/',
    redirect: '/text2img'
  },
  {
    path: '/text2img',
    name: 'text2img',
    component: Home,
    meta: { mode: 'text2img', title: 'Text to Image' }
  },
  {
    path: '/imgedit',
    name: 'imgedit',
    component: ImageEdit,
    meta: { title: 'Image Edit' }
  },
  {
    path: '/txt2video',
    name: 'txt2video',
    component: Home,
    meta: { mode: 'txt2video', title: 'Text to Video' }
  },
  {
    path: '/img2video',
    name: 'img2video',
    component: Home,
    meta: { mode: 'img2video', title: 'Image to Video' }
  },
  {
    path: '/ads',
    name: 'ads',
    component: AdGenerator,
    meta: { title: 'AI Ads Generator' }
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: Home,
    meta: { mode: 'gallery', title: 'Gallery' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')