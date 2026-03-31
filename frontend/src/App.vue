<template>
  <div class="min-h-screen bg-slate-50 dark:bg-dark-950">
    <Navbar />
    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'

const router = useRouter()

function isEditableTarget(el) {
  if (!el || !el.tagName) return false
  const tag = el.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true
  return el.isContentEditable
}

function onKeydown(e) {
  if (e.metaKey || e.altKey) return
  if (isEditableTarget(e.target)) return

  if (e.ctrlKey) {
    const k = e.key.toLowerCase()
    if (k === 'n') {
      e.preventDefault()
      router.push('/')
      return
    }
    if (k === 's') {
      e.preventDefault()
      window.dispatchEvent(new CustomEvent('redswarm:stop-simulation'))
      return
    }
    if (k === 'r') {
      e.preventDefault()
      router.push('/reports')
      return
    }
  }
  if (e.key === 'Escape') {
    window.dispatchEvent(new CustomEvent('redswarm:close-modals'))
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>
