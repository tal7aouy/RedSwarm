<template>
  <nav
    class="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-dark-800 dark:bg-dark-900/90"
  >
    <div class="container mx-auto px-4">
      <div class="flex h-16 items-center justify-between">
        <div class="flex items-center space-x-8">
          <router-link to="/" class="flex items-center space-x-2">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600"
            >
              <Shield class="h-5 w-5 text-white" />
            </div>
            <span class="text-xl font-bold text-slate-900 dark:text-white"
              >RedSwarm</span
            >
          </router-link>

          <div class="hidden space-x-4 md:flex">
            <router-link to="/" class="nav-link">
              <Home class="h-4 w-4" />
              <span>Home</span>
            </router-link>
            <router-link to="/scenarios" class="nav-link">
              <Target class="h-4 w-4" />
              <span>Scenarios</span>
            </router-link>
            <router-link to="/reports" class="nav-link">
              <FileText class="h-4 w-4" />
              <span>Reports</span>
            </router-link>
          </div>
        </div>

        <div class="flex items-center space-x-2 md:space-x-4">
          <button
            type="button"
            :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            class="flex items-center rounded-lg border border-slate-200 bg-slate-100 p-2 text-slate-700 transition-colors hover:bg-slate-200 dark:border-dark-700 dark:bg-dark-800 dark:text-gray-300 dark:hover:bg-dark-700"
            @click="toggle"
          >
            <Sun v-if="isDark" class="h-4 w-4" />
            <Moon v-else class="h-4 w-4" />
          </button>

          <a
            href="https://github.com/tal7aouy/RedSwarm"
            target="_blank"
            rel="noopener noreferrer"
            class="hidden items-center space-x-2 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1 transition-colors hover:bg-slate-200 sm:flex dark:border-dark-800 dark:bg-dark-800 dark:hover:bg-dark-700"
          >
            <Github class="h-4 w-4 text-slate-500 dark:text-gray-400" />
            <span class="text-sm text-slate-600 dark:text-gray-400">GitHub</span>
          </a>
          <div
            class="flex items-center space-x-2 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1 dark:border-dark-800 dark:bg-dark-800"
          >
            <div class="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
            <span class="text-sm text-slate-600 dark:text-gray-400">Online</span>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { Shield, Home, Target, FileText, Github, Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'

const { isDark, toggle } = useTheme()
</script>

<style scoped>
.nav-link {
  @apply flex items-center space-x-2 rounded-lg px-3 py-2 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-gray-400 dark:hover:bg-dark-800 dark:hover:text-white;
}

.router-link-active.nav-link {
  @apply bg-slate-100 text-slate-900 dark:bg-dark-800 dark:text-white;
}
</style>
