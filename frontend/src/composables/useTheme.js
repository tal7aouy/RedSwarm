import { ref } from 'vue'

const STORAGE_KEY = 'redswarm-theme'

export function applyStoredTheme() {
  if (typeof document === 'undefined') return
  const stored = localStorage.getItem(STORAGE_KEY)
  const dark = stored !== 'light'
  document.documentElement.classList.toggle('dark', dark)
}

export function useTheme() {
  const isDark = ref(
    typeof document !== 'undefined' &&
      document.documentElement.classList.contains('dark')
  )

  function setDark(value) {
    isDark.value = value
    document.documentElement.classList.toggle('dark', value)
    localStorage.setItem(STORAGE_KEY, value ? 'dark' : 'light')
  }

  function toggle() {
    setDark(!isDark.value)
  }

  return { isDark, setDark, toggle }
}
