import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import i18n from './i18n'

// Views
import Home from './views/Home.vue'
import ImageEdit from './views/ImageEdit.vue'
import Workflow from './views/Workflow.vue'
import PromptsGallery from './views/PromptsGallery.vue'
import ImgGen from './views/ImgGen.vue'
import AdGenerator from './views/AdGenerator.vue'
import AiAvatar from './views/AiAvatar.vue'
import UgcAdsCreator from './views/UgcAdsCreator.vue'

const routes = [
  {
    path: '/',
    redirect: '/text2img'
  },
  {
    path: '/text2img',
    name: 'text2img',
    component: Home,
    meta: { mode: 'text2img', title: 'nav.text2img' }
  },
  {
    path: '/imgedit',
    name: 'imgedit',
    component: ImageEdit,
    meta: { title: 'nav.imgedit' }
  },
  {
    path: '/txt2video',
    name: 'txt2video',
    component: Home,
    meta: { mode: 'txt2video', title: 'nav.txt2video' }
  },
  {
    path: '/img2video',
    name: 'img2video',
    component: Home,
    meta: { mode: 'img2video', title: 'nav.img2video' }
  },
  {
    path: '/prompts',
    name: 'prompts',
    component: PromptsGallery,
    meta: { title: 'nav.prompts' }
  },
  {
    path: '/workflow',
    name: 'workflow',
    component: Workflow,
    meta: { title: 'nav.workflow' }
  },
  {
    path: '/img-gen',
    name: 'img-gen',
    component: ImgGen,
    meta: { title: 'nav.imgGen' }
  },
  {
    path: '/ads',
    name: 'ads',
    component: AdGenerator,
    meta: { title: 'nav.ads' }
  },
  {
    path: '/avatar',
    name: 'avatar',
    component: AiAvatar,
    meta: { title: 'nav.avatar' }
  },
  {
    path: '/ugc-ads',
    name: 'ugc-ads',
    component: UgcAdsCreator,
    meta: { title: 'UGC AI Ads Creator' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.use(i18n)
app.mount('#app')