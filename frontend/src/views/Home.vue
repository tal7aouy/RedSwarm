<template>
  <div class="space-y-8">
    <div class="text-center space-y-4">
      <h1 class="text-5xl font-bold text-slate-900 dark:text-white">
        🔴 <span class="text-primary-500">RedSwarm</span>
      </h1>
      <p class="mx-auto max-w-2xl text-xl text-slate-600 dark:text-gray-400">
        AI-Powered Red Team Simulation Engine
      </p>
      <p class="text-slate-500 dark:text-gray-500">
        Simulate real attackers, not just tools. Deploy AI agents to test your defenses.
      </p>
    </div>

    <div class="card max-w-3xl mx-auto glow-red">
      <h2 class="mb-6 flex items-center text-2xl font-bold text-slate-900 dark:text-white">
        <Zap class="w-6 h-6 mr-2 text-primary-500" />
        Start New Simulation
      </h2>
      
      <form @submit.prevent="startSimulation" class="space-y-6">
        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-gray-300">
            Target IP/Domain
          </label>
          <input
            v-model="config.target"
            type="text"
            placeholder="192.168.1.100 or localhost"
            class="input"
            required
          />
          <p class="mt-1 text-xs text-slate-500 dark:text-gray-500">
            Only lab/local IPs allowed (192.168.x.x, 10.x.x.x, 172.16.x.x, 127.0.0.1)
          </p>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-gray-300">
            Scenario (Optional)
          </label>
          <select v-model="config.scenario" class="input">
            <option value="">Custom Simulation</option>
            <option value="ctf_bank_heist">CTF: Hack the Bank</option>
            <option value="bypass_zero_trust">Bypass Zero Trust</option>
            <option value="insider_threat">Insider Threat</option>
            <option value="ransomware_attack">Ransomware Simulation</option>
            <option value="apt_campaign">APT Campaign</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-gray-300">
            Agent Types
          </label>
          <div class="grid grid-cols-2 gap-3">
            <label
              v-for="agent in agentTypes"
              :key="agent.type"
              class="flex cursor-pointer items-center space-x-3 rounded-lg border border-slate-200 bg-slate-50 p-3 transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
            >
              <input
                type="checkbox"
                :value="agent.type"
                v-model="config.agent_types"
                class="h-4 w-4 rounded border-slate-300 bg-white text-primary-600 focus:ring-primary-500 dark:border-dark-600 dark:bg-dark-700"
              />
              <div class="flex-1">
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ agent.name }}</div>
                <div class="text-xs text-slate-500 dark:text-gray-500">{{ agent.description }}</div>
              </div>
            </label>
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700 dark:text-gray-300">
            Agent Personas
          </label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="persona in personas"
              :key="persona.value"
              type="button"
              @click="togglePersona(persona.value)"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                selectedPersona === persona.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-dark-800 dark:text-gray-400 dark:hover:bg-dark-700'
              ]"
            >
              {{ persona.name }}
            </button>
          </div>
        </div>

        <div class="flex space-x-4">
          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary flex-1 flex items-center justify-center space-x-2"
          >
            <Play v-if="!loading" class="w-5 h-5" />
            <Loader v-else class="w-5 h-5 animate-spin" />
            <span>{{ loading ? 'Starting...' : 'Start Simulation' }}</span>
          </button>
          <button
            type="button"
            @click="resetConfig"
            class="btn btn-secondary"
          >
            Reset
          </button>
        </div>
      </form>

      <div v-if="error" class="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
        <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
      <div class="card text-center">
        <Brain class="w-12 h-12 text-primary-500 mx-auto mb-3" />
        <h3 class="mb-2 text-lg font-semibold text-slate-900 dark:text-white">AI Agents</h3>
        <p class="text-sm text-slate-600 dark:text-gray-400">
          Multi-agent swarm with unique personas and tactics
        </p>
      </div>
      
      <div class="card text-center">
        <Network class="w-12 h-12 text-primary-500 mx-auto mb-3" />
        <h3 class="mb-2 text-lg font-semibold text-slate-900 dark:text-white">Attack Graph</h3>
        <p class="text-sm text-slate-600 dark:text-gray-400">
          Real-time visualization of attack chains
        </p>
      </div>
      
      <div class="card text-center">
        <Shield class="w-12 h-12 text-primary-500 mx-auto mb-3" />
        <h3 class="mb-2 text-lg font-semibold text-slate-900 dark:text-white">God Mode</h3>
        <p class="text-sm text-slate-600 dark:text-gray-400">
          Inject defenses and watch agents adapt
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'
import { useNotifications } from '../composables/useToast'
import { Play, Loader, Zap, Brain, Network, Shield } from 'lucide-vue-next'

const router = useRouter()
const simulationStore = useSimulationStore()
const notifications = useNotifications()

const config = ref({
  target: '192.168.1.100',
  scenario: '',
  agent_types: ['recon', 'exploit', 'post_exploit'],
  personas: {}
})

const selectedPersona = ref('generic')
const loading = ref(false)
const error = ref(null)

const agentTypes = [
  { type: 'recon', name: 'Recon Agent', description: 'Discover & scan' },
  { type: 'exploit', name: 'Exploit Agent', description: 'Gain access' },
  { type: 'post_exploit', name: 'Post-Exploit', description: 'Maintain & pivot' },
  { type: 'insider', name: 'Insider Agent', description: 'Abuse trust' }
]

const personas = [
  { value: 'generic', name: 'Generic' },
  { value: 'apt28', name: 'APT28' },
  { value: 'apt29', name: 'APT29' },
  { value: 'lazarus', name: 'Lazarus' },
  { value: 'script_kiddie', name: 'Script Kiddie' },
  { value: 'ransomware', name: 'Ransomware' }
]

function togglePersona(persona) {
  selectedPersona.value = persona
  config.value.personas = {
    recon: persona,
    exploit: persona,
    post_exploit: persona,
    insider: persona
  }
}

async function startSimulation() {
  loading.value = true
  error.value = null
  
  try {
    const result = await simulationStore.startSimulation(config.value)
    notifications.simulationStarted(result.simulation_id)
    router.push(`/simulation/${result.simulation_id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to start simulation'
    notifications.error(error.value)
  } finally {
    loading.value = false
  }
}

function resetConfig() {
  config.value = {
    target: '192.168.1.100',
    scenario: '',
    agent_types: ['recon', 'exploit', 'post_exploit'],
    personas: {}
  }
  selectedPersona.value = 'generic'
  error.value = null
}
</script>
