<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Simulation Reports</h1>
      <p class="mt-2 text-slate-600 dark:text-gray-400">
        View, search, and export completed simulations
      </p>
    </div>

    <div
      class="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 dark:border-dark-800 dark:bg-dark-900 sm:flex-row sm:flex-wrap sm:items-end"
    >
      <div class="min-w-[200px] flex-1">
        <label class="mb-1 block text-xs font-medium text-slate-600 dark:text-gray-400"
          >Search</label
        >
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Target, scenario, ID…"
          class="input text-sm"
        />
      </div>
      <div class="w-full min-w-[140px] sm:w-auto">
        <label class="mb-1 block text-xs font-medium text-slate-600 dark:text-gray-400"
          >Status</label
        >
        <select v-model="statusFilter" class="input text-sm">
          <option value="">All statuses</option>
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="stopped">Stopped</option>
        </select>
      </div>
      <div class="w-full min-w-[160px] sm:w-auto">
        <label class="mb-1 block text-xs font-medium text-slate-600 dark:text-gray-400"
          >Sort by date</label
        >
        <select v-model="sortOrder" class="input text-sm">
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>
      <p class="text-sm text-slate-500 dark:text-gray-500 sm:ml-auto">
        {{ filteredSimulations.length }} of {{ simulations.length }} shown
      </p>
    </div>

    <div class="space-y-4">
      <div
        v-for="simulation in filteredSimulations"
        :key="simulation.id"
        class="card hover:border-primary-600 cursor-pointer transition-colors"
        @click="viewReport(simulation)"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="mb-2 flex items-center space-x-3">
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">
                {{ simulation.target }}
              </h3>
              <span :class="getStatusClass(simulation.status)">
                {{ simulation.status }}
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-gray-400">
              <div class="flex items-center space-x-1">
                <Calendar class="h-4 w-4" />
                <span>{{ formatDate(simulation.created_at) }}</span>
              </div>

              <div v-if="simulation.scenario" class="flex items-center space-x-1">
                <Target class="h-4 w-4" />
                <span>{{ simulation.scenario }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <div class="flex items-center space-x-2">
              <button
                @click.stop="downloadJSON(simulation)"
                class="btn btn-secondary flex items-center space-x-2"
              >
                <Download class="h-4 w-4" />
                <span>JSON</span>
              </button>
              <button
                @click.stop="downloadPDF(simulation)"
                class="btn btn-primary flex items-center space-x-2"
              >
                <FileText class="h-4 w-4" />
                <span>PDF</span>
              </button>
            </div>

            <ChevronRight class="h-5 w-5 text-slate-400 dark:text-gray-500" />
          </div>
        </div>
      </div>

      <div v-if="!simulations.length && !loading" class="card py-12 text-center">
        <FileText class="mx-auto mb-4 h-16 w-16 text-slate-300 dark:text-gray-600" />
        <p class="text-slate-600 dark:text-gray-400">No simulation reports yet</p>
        <button @click="$router.push('/')" class="btn btn-primary mt-4">Start Your First Simulation</button>
      </div>

      <div
        v-else-if="simulations.length && !filteredSimulations.length"
        class="card py-8 text-center text-slate-600 dark:text-gray-400"
      >
        No reports match your filters.
        <button type="button" class="ml-2 text-primary-600 underline dark:text-primary-400" @click="clearFilters">
          Clear filters
        </button>
      </div>

      <div v-if="loading" class="py-8 text-center">
        <Loader class="mx-auto h-8 w-8 animate-spin text-primary-500" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'
import { useNotifications } from '../composables/useToast'
import { FileText, Calendar, Target, Download, ChevronRight, Loader } from 'lucide-vue-next'
import { format } from 'date-fns'

const router = useRouter()
const simulationStore = useSimulationStore()
const notifications = useNotifications()

const simulations = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const sortOrder = ref('desc')

const filteredSimulations = computed(() => {
  let list = [...simulations.value]
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((s) => {
      const id = String(s.id || '').toLowerCase()
      const target = String(s.target || '').toLowerCase()
      const scenario = String(s.scenario || '').toLowerCase()
      return id.includes(q) || target.includes(q) || scenario.includes(q)
    })
  }
  if (statusFilter.value) {
    list = list.filter((s) => s.status === statusFilter.value)
  }
  list.sort((a, b) => {
    const ta = new Date(a.created_at).getTime()
    const tb = new Date(b.created_at).getTime()
    return sortOrder.value === 'desc' ? tb - ta : ta - tb
  })
  return list
})

function clearFilters() {
  searchQuery.value = ''
  statusFilter.value = ''
}

onMounted(async () => {
  await fetchSimulations()
})

async function fetchSimulations() {
  loading.value = true
  try {
    await simulationStore.listSimulations()
    simulations.value = simulationStore.simulations
  } catch (err) {
    console.error('Failed to fetch simulations:', err)
  } finally {
    loading.value = false
  }
}

function viewReport(simulation) {
  router.push(`/simulation/${simulation.id}`)
}

async function downloadJSON(simulation) {
  try {
    const report = await simulationStore.getSimulationReport(simulation.id)
    const dataStr = JSON.stringify(report, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)

    const exportFileDefaultName = `redswarm-report-${simulation.id}.json`

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()

    notifications.reportExported('json')
  } catch (err) {
    console.error('Failed to download JSON report:', err)
    notifications.error('Failed to export JSON report')
  }
}

async function downloadPDF(simulation) {
  try {
    const report = await simulationStore.getSimulationReport(simulation.id)

    const htmlContent = generatePDFHTML(report, simulation)

    const printWindow = window.open('', '_blank')
    printWindow.document.write(htmlContent)
    printWindow.document.close()

    setTimeout(() => {
      printWindow.print()
    }, 500)

    notifications.reportExported('pdf')
  } catch (err) {
    console.error('Failed to download PDF report:', err)
    notifications.error('Failed to export PDF report')
  }
}

function generatePDFHTML(report, simulation) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>RedSwarm Report - ${simulation.id}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
        .header { text-align: center; border-bottom: 2px solid #e74c3c; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #e74c3c; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .summary-item { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c; }
        .action { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .action.success { border-left: 4px solid #28a745; }
        .action.failed { border-left: 4px solid #dc3545; }
        .mitre-technique { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        @media print { body { margin: 0; } }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>🔴 RedSwarm Attack Report</h1>
        <p><strong>Simulation ID:</strong> ${report.simulation_id}</p>
        <p><strong>Target:</strong> ${report.target}</p>
        <p><strong>Status:</strong> ${report.status}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
      </div>

      <div class="section">
        <h2>Executive Summary</h2>
        <div class="summary-grid">
          <div class="summary-item">
            <h3>Total Actions</h3>
            <p style="font-size: 2em; color: #e74c3c;">${report.summary.total_actions}</p>
          </div>
          <div class="summary-item">
            <h3>Success Rate</h3>
            <p style="font-size: 2em; color: #28a745;">${Math.round((report.summary.successful_actions / report.summary.total_actions) * 100)}%</p>
          </div>
          <div class="summary-item">
            <h3>Vulnerabilities Found</h3>
            <p style="font-size: 2em; color: #ffc107;">${report.summary.vulnerabilities_found}</p>
          </div>
          <div class="summary-item">
            <h3>MITRE Techniques</h3>
            <p style="font-size: 2em; color: #17a2b8;">${report.mitre_attack_mapping.total_techniques}</p>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>Attack Chain</h2>
        ${report.attack_graph.actions
          .map(
            (action) => `
          <div class="action ${action.success ? 'success' : 'failed'}">
            <strong>${action.action_type}</strong>
            <span class="mitre-technique">${action.mitre_technique}</span>
            <br>
            <small>${action.result?.description || 'No description'}</small>
            <br>
            <small>Time: ${new Date(action.timestamp).toLocaleString()}</small>
          </div>
        `
          )
          .join('')}
      </div>

      <div class="section">
        <h2>MITRE ATT&CK Coverage</h2>
        ${report.mitre_attack_mapping.tactics
          .map(
            (tactic) => `
          <div style="margin-bottom: 20px;">
            <h3>${tactic.tactic_id} - ${tactic.tactic_id.replace('TA', '')}</h3>
            <ul>
              ${tactic.techniques
                .map(
                  (tech) => `
                <li>${tech.technique_id}: ${tech.action_type} (${tech.success ? '✅' : '❌'})</li>
              `
                )
                .join('')}
            </ul>
          </div>
        `
          )
          .join('')}
      </div>

      <div class="section">
        <h2>Agent Performance</h2>
        ${Object.entries(report.agents)
          .map(
            ([id, agent]) => `
          <div style="margin-bottom: 15px;">
            <strong>${agent.agent_type} (${agent.persona})</strong>
            <br>
            Actions: ${agent.actions_count} | Status: ${agent.status}
          </div>
        `
          )
          .join('')}
      </div>
    </body>
    </html>
  `
}

function getStatusClass(status) {
  const classes = {
    running: 'badge badge-warning',
    completed: 'badge badge-success',
    failed: 'badge badge-danger',
    stopped: 'badge badge-info'
  }
  return classes[status] || 'badge badge-info'
}

function formatDate(dateString) {
  return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
}
</script>
