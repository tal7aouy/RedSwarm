<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">CTF Scenarios</h1>
      <p class="mt-2 text-slate-600 dark:text-gray-400">Pre-built attack scenarios for training and testing</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="scenario in scenarios"
        :key="scenario.id"
        class="card hover:border-primary-600 transition-colors cursor-pointer"
        @click="selectScenario(scenario)"
      >
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="mb-2 text-xl font-semibold text-slate-900 dark:text-white">{{ scenario.name }}</h3>
            <span :class="getDifficultyClass(scenario.difficulty)">
              {{ scenario.difficulty }}
            </span>
          </div>
          <Target class="w-8 h-8 text-primary-500" />
        </div>
        
        <p class="mb-4 text-slate-600 dark:text-gray-400">{{ scenario.description }}</p>
        
        <div class="space-y-3">
          <div>
            <h4 class="mb-2 text-sm font-medium text-slate-700 dark:text-gray-300">Objectives:</h4>
            <ul class="space-y-1">
              <li
                v-for="(objective, idx) in scenario.objectives"
                :key="idx"
                class="flex items-start text-sm text-slate-600 dark:text-gray-400"
              >
                <CheckCircle class="w-4 h-4 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                <span>{{ objective }}</span>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 class="mb-2 text-sm font-medium text-slate-700 dark:text-gray-300">Recommended Agents:</h4>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="agent in scenario.recommended_agents"
                :key="agent"
                class="badge badge-info"
              >
                {{ agent }}
              </span>
            </div>
          </div>
        </div>
        
        <button
          @click.stop="startScenario(scenario)"
          class="btn btn-primary w-full mt-4 flex items-center justify-center space-x-2"
        >
          <Play class="w-4 h-4" />
          <span>Start Scenario</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8">
      <Loader class="w-8 h-8 animate-spin text-primary-500 mx-auto" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'
import { Target, CheckCircle, Play, Loader } from 'lucide-vue-next'
import api from '../services/api'

const router = useRouter()
const simulationStore = useSimulationStore()

const scenarios = ref([])
const loading = ref(false)

onMounted(async () => {
  await fetchScenarios()
})

async function fetchScenarios() {
  loading.value = true
  try {
    const response = await api.get('/scenarios/list')
    scenarios.value = response.data
  } catch (err) {
    console.error('Failed to fetch scenarios:', err)
  } finally {
    loading.value = false
  }
}

async function startScenario(scenario) {
  loading.value = true
  try {
    const config = {
      target: scenario.target_config.target,
      scenario: scenario.id,
      agent_types: scenario.recommended_agents,
      personas: scenario.target_config.personas || {}
    }
    
    const result = await simulationStore.startSimulation(config)
    router.push(`/simulation/${result.simulation_id}`)
  } catch (err) {
    console.error('Failed to start scenario:', err)
  } finally {
    loading.value = false
  }
}

function selectScenario(scenario) {
  console.log('Selected scenario:', scenario)
}

function getDifficultyClass(difficulty) {
  const classes = {
    easy: 'badge badge-success',
    medium: 'badge badge-warning',
    hard: 'badge badge-danger',
    very_hard: 'badge badge-danger'
  }
  return classes[difficulty] || 'badge badge-info'
}
</script>
