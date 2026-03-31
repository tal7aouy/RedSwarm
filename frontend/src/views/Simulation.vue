<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Simulation Dashboard</h1>
        <p class="mt-1 text-slate-600 dark:text-gray-400">ID: {{ simulationId }}</p>
      </div>
      
      <div class="flex items-center space-x-4">
        <div :class="statusBadgeClass">
          {{ status?.status || 'Loading...' }}
        </div>
        <div class="flex items-center space-x-2">
          <button
            v-if="status?.status === 'running'"
            @click="stopSimulation"
            class="btn btn-danger flex items-center space-x-2"
          >
            <StopCircle class="w-4 h-4" />
            <span>Stop</span>
          </button>
          <button
            v-if="['completed', 'failed', 'stopped'].includes(status?.status)"
            @click="exportReport"
            class="btn btn-primary flex items-center space-x-2"
          >
            <Download class="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Attack Graph -->
      <AttackGraph 
        :attackChain="attackChain"
        :agents="status?.agents"
        :target="status?.target || 'Unknown'"
        @showReasoning="viewReasoning"
      />
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Agents</h3>
            <Users class="w-5 h-5 text-primary-500" />
          </div>
        <div class="space-y-3">
          <div
            v-for="(agent, id) in status?.agents"
            :key="id"
            class="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-dark-700 dark:bg-dark-800"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-slate-900 dark:text-white">{{ agent.type }}</span>
              <span :class="getAgentStatusClass(agent.status)">
                {{ agent.status }}
              </span>
            </div>
            <div class="text-xs text-gray-500">
              Actions: {{ agent.actions_count }}
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2 card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Attack Chain</h3>
          <Activity class="w-5 h-5 text-primary-500" />
        </div>
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <div
            v-for="action in attackChain"
            :key="action.id"
            class="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-dark-700 dark:bg-dark-800 border-l-4"
            :class="action.success ? 'border-l-green-500' : 'border-l-red-500'"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-1">
                  <CheckCircle v-if="action.success" class="w-4 h-4 text-green-500" />
                  <XCircle v-else class="w-4 h-4 text-red-500" />
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ action.action_type }}</span>
                  <button
                    v-if="action.llm_reasoning"
                    @click="viewReasoning(action)"
                    class="ml-2 p-1 text-blue-400 hover:text-blue-300 transition-colors"
                    title="View AI Reasoning"
                  >
                    <Brain class="w-3 h-3" />
                  </button>
                </div>
                <p class="mb-2 text-xs text-slate-600 dark:text-gray-400">
                  {{ action.result?.description || 'No description' }}
                </p>
                <div class="flex items-center space-x-2">
                  <span class="badge badge-info text-xs">{{ action.mitre_technique }}</span>
                  <span class="text-xs text-slate-500 dark:text-gray-500">{{ formatTime(action.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!attackChain.length" class="py-8 text-center text-slate-500 dark:text-gray-500">
            No actions yet...
          </div>
        </div>
      </div>
    </div>

    <div class="card glow-green">
      <div class="flex items-center justify-between mb-4">
        <h3 class="flex items-center text-lg font-semibold text-slate-900 dark:text-white">
          <Zap class="w-5 h-5 mr-2 text-yellow-500" />
          God Mode - Inject Defenses
        </h3>
      </div>
      
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <button
          @click="injectDefense('firewall')"
          class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
        >
          <Shield class="w-6 h-6 text-blue-500 mx-auto mb-2" />
          <div class="text-sm font-medium text-slate-900 dark:text-white">Firewall</div>
        </button>
        
        <button
          @click="injectDefense('edr')"
          class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
        >
          <Eye class="w-6 h-6 text-purple-500 mx-auto mb-2" />
          <div class="text-sm font-medium text-slate-900 dark:text-white">EDR</div>
        </button>
        
        <button
          @click="injectDefense('patch')"
          class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
        >
          <Wrench class="w-6 h-6 text-green-500 mx-auto mb-2" />
          <div class="text-sm font-medium text-slate-900 dark:text-white">Patch</div>
        </button>
        
        <button
          @click="injectDefense('block_port')"
          class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
        >
          <Lock class="w-6 h-6 text-red-500 mx-auto mb-2" />
          <div class="text-sm font-medium text-slate-900 dark:text-white">Block Port</div>
        </button>
        
        <button
          @click="injectDefense('rate_limit')"
          class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center transition-colors hover:bg-slate-100 dark:border-dark-700 dark:bg-dark-800 dark:hover:bg-dark-700"
        >
          <Timer class="w-6 h-6 text-orange-500 mx-auto mb-2" />
          <div class="text-sm font-medium text-slate-900 dark:text-white">Rate Limit</div>
        </button>
      </div>

      <div v-if="injections.length" class="mt-4 space-y-2">
        <h4 class="text-sm font-medium text-slate-600 dark:text-gray-400">Active Defenses:</h4>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="injection in injections"
            :key="injection.id"
            class="badge badge-success"
          >
            {{ injection.type }}
          </span>
        </div>
      </div>
      </div>
    </div>
    
    <!-- Reasoning Modal -->
    <ReasoningModal
      :show="showReasoningModal"
      :action="reasoningAction"
      :agentType="getAgentType(reasoningAction?.agent_id)"
      @close="showReasoningModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'
import { useNotifications } from '../composables/useToast'
import {
  Users, Activity, CheckCircle, XCircle, StopCircle, Zap,
  Shield, Eye, Wrench, Lock, Timer, Download, Brain
} from 'lucide-vue-next'
import { formatDistanceToNow } from 'date-fns'
import ReasoningModal from '../components/ReasoningModal.vue'
import AttackGraph from '../components/AttackGraph.vue'

const route = useRoute()
const router = useRouter()
const simulationStore = useSimulationStore()
const notifications = useNotifications()

const simulationId = route.params.id
const status = ref(null)
const attackChain = ref([])
const injections = ref([])
const reasoningAction = ref(null)
const showReasoningModal = ref(false)
let pollInterval = null

const statusBadgeClass = ref('badge badge-info')

function onStopShortcut() {
  if (status.value?.status === 'running') {
    stopSimulation()
  }
}

function onCloseModals() {
  showReasoningModal.value = false
}

onMounted(async () => {
  if (!simulationId) {
    router.push('/')
    return
  }

  window.addEventListener('redswarm:stop-simulation', onStopShortcut)
  window.addEventListener('redswarm:close-modals', onCloseModals)

  await fetchStatus()
  await fetchAttackChain()
  
  pollInterval = setInterval(async () => {
    await fetchStatus()
    await fetchAttackChain()
    
    if (['completed', 'failed', 'stopped'].includes(status.value?.status)) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }, 3000)
})

onUnmounted(() => {
  window.removeEventListener('redswarm:stop-simulation', onStopShortcut)
  window.removeEventListener('redswarm:close-modals', onCloseModals)
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})

async function fetchStatus() {
  try {
    const previousStatus = status.value?.status
    status.value = await simulationStore.getSimulationStatus(simulationId)
    updateStatusBadge()
    
    // Notify on status changes
    if (previousStatus !== status.value?.status) {
      if (status.value?.status === 'completed' && previousStatus !== 'completed') {
        notifications.simulationCompleted(simulationId)
      } else if (status.value?.status === 'failed' && previousStatus !== 'failed') {
        notifications.error('Simulation failed - check the logs for details')
      }
    }
  } catch (err) {
    if (err.response?.status === 404) {
      console.error('Simulation not found')
      if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
      }
      if (route.name === 'simulation') {
        router.push('/')
      }
      return
    }
    console.error('Failed to fetch status:', err)
  }
}

async function fetchAttackChain() {
  try {
    const response = await simulationStore.getSimulationReport(simulationId)
    attackChain.value = response.attack_graph?.actions || []
  } catch (err) {
    if (err.response?.status === 404) {
      return
    }
    console.error('Failed to fetch attack chain:', err)
  }
}

async function stopSimulation() {
  try {
    await simulationStore.stopSimulation(simulationId)
    await fetchStatus()
    notifications.simulationStopped()
  } catch (err) {
    console.error('Failed to stop simulation:', err)
    notifications.error('Failed to stop simulation')
  }
}

async function injectDefense(type) {
  try {
    const config = getDefenseConfig(type)
    await simulationStore.injectDefense(simulationId, { type, config })
    injections.value.push({ id: Date.now(), type })
    notifications.defenseInjected(type)
  } catch (err) {
    console.error('Failed to inject defense:', err)
    notifications.error('Failed to inject defense')
  }
}

function getDefenseConfig(type) {
  const configs = {
    firewall: { rules: ['block_port_445'], default_policy: 'deny' },
    edr: { detection_level: 'high' },
    patch: { cves: ['CVE-2024-1234'] },
    block_port: { ports: [445, 3389] },
    rate_limit: { max_requests: 10, time_window: 60 }
  }
  return configs[type] || {}
}

function getAgentStatusClass(agentStatus) {
  const classes = {
    idle: 'badge badge-info',
    thinking: 'badge badge-warning',
    executing: 'badge badge-warning',
    completed: 'badge badge-success',
    failed: 'badge badge-danger'
  }
  return classes[agentStatus] || 'badge badge-info'
}

function updateStatusBadge() {
  const classes = {
    running: 'badge badge-warning',
    completed: 'badge badge-success',
    failed: 'badge badge-danger',
    stopped: 'badge badge-info'
  }
  statusBadgeClass.value = classes[status.value?.status] || 'badge badge-info'
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

async function exportReport() {
  try {
    const report = await simulationStore.getSimulationReport(simulationId)
    const dataStr = JSON.stringify(report, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `redswarm-report-${simulationId}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    notifications.reportExported('json')
  } catch (err) {
    console.error('Failed to export report:', err)
    notifications.error('Failed to export report')
  }
}

function viewReasoning(action) {
  reasoningAction.value = action
  showReasoningModal.value = true
}

function getAgentType(agentId) {
  if (!agentId) return 'Unknown'
  if (agentId.includes('recon')) return 'Reconnaissance'
  if (agentId.includes('exploit')) return 'Exploitation'
  if (agentId.includes('post_exploit')) return 'Post-Exploitation'
  if (agentId.includes('insider')) return 'Insider Threat'
  return 'Unknown'
}
</script>
