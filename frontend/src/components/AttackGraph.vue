<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Attack Graph</h3>
      <div class="flex items-center space-x-2">
        <button
          @click="togglePhysics"
          class="btn btn-secondary btn-sm"
          :class="{ 'btn-primary': physicsEnabled }"
        >
          {{ physicsEnabled ? 'Physics On' : 'Physics Off' }}
        </button>
        <button
          @click="centerGraph"
          class="btn btn-secondary btn-sm"
        >
          Center
        </button>
      </div>
    </div>
    
    <div
      ref="networkContainer"
      class="h-96 w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-100 dark:border-dark-700 dark:bg-dark-800"
    ></div>
    
    <div class="mt-4 flex items-center space-x-4 text-sm text-slate-600 dark:text-gray-400">
      <div class="flex items-center space-x-1">
        <div class="w-3 h-3 bg-green-500 rounded-full"></div>
        <span>Success</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-3 h-3 bg-red-500 rounded-full"></div>
        <span>Failed</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
        <span>Target</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-3 h-3 bg-purple-500 rounded-full"></div>
        <span>Agent</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Network } from 'vis-network/standalone'
import 'vis-network/dist/dist/vis-network.css'

const props = defineProps({
  attackChain: Array,
  agents: Object,
  target: String
})

const networkContainer = ref(null)
let network = null
const physicsEnabled = ref(true)

// Graph data
const nodes = ref([])
const edges = ref([])
const nodeIds = new Map()
let animationFrame = null

onMounted(() => {
  initializeGraph()
  updateGraph()
})

onUnmounted(() => {
  if (network) {
    network.destroy()
  }
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
})

watch(() => props.attackChain, () => {
  updateGraph()
}, { deep: true })

watch(() => props.agents, () => {
  updateGraph()
}, { deep: true })

watch(
  () => props.target,
  () => {
    updateGraph()
  }
)

function initializeGraph() {
  if (!networkContainer.value) return

  const options = {
    nodes: {
      shape: 'dot',
      size: 20,
      font: {
        size: 12,
        color: '#ffffff',
        face: 'monospace'
      },
      borderWidth: 2,
      shadow: true
    },
    edges: {
      width: 2,
      color: { color: '#848484', highlight: '#ff0000' },
      smooth: {
        type: 'curvedCW',
        roundness: 0.2
      },
      arrows: {
        to: { enabled: true, scaleFactor: 0.5 }
      },
      shadow: true
    },
    physics: {
      enabled: physicsEnabled.value,
      stabilization: { iterations: 100 },
      barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.3,
        springLength: 120,
        springConstant: 0.04,
        damping: 0.09
      }
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      zoomView: false,
      dragView: true
    }
  }

  network = new Network(networkContainer.value, { nodes: nodes.value, edges: edges.value }, options)
  
  network.on("click", (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.value.find(n => n.id === nodeId)
      if (node && node.action) {
        // Emit event to show reasoning modal
        emit('showReasoning', node.action)
      }
    }
  })
}

const emit = defineEmits(['showReasoning'])

function updateGraph() {
  if (!network) return

  // Clear existing data
  nodes.value = []
  edges.value = []
  nodeIds.clear()

  const targetLabel = (props.target && String(props.target).trim()) || 'Unknown target'

  // Add target node
  const targetId = 'target'
  nodes.value.push({
    id: targetId,
    label: `Target\n${targetLabel}`,
    color: { background: '#3b82f6', border: '#1e40af' },
    shape: 'database',
    size: 30,
    font: { size: 14, color: '#ffffff' }
  })
  nodeIds.set(targetId, targetId)

  // Add agent nodes (status API uses type; report uses agent_type — support both)
  if (props.agents && Object.keys(props.agents).length) {
    Object.entries(props.agents).forEach(([agentId, agent], index) => {
      const nodeId = `agent_${agentId}`
      const n = Object.keys(props.agents).length
      const angle = (index * 2 * Math.PI) / n
      const x = Math.cos(angle) * 200
      const y = Math.sin(angle) * 200

      const role = agent.agent_type || agent.type || 'agent'
      const persona = agent.persona != null ? String(agent.persona) : 'generic'

      nodes.value.push({
        id: nodeId,
        label: `${role}\n${persona}`,
        color: { background: '#a855f7', border: '#7c3aed' },
        shape: 'box',
        size: 25,
        x: x,
        y: y,
        font: { size: 12, color: '#ffffff' },
        agent: agent
      })
      nodeIds.set(agentId, nodeId)
    })
  }

  // Add action nodes and edges
  if (props.attackChain) {
    const agentPositions = {}
    let lastActionId = targetId

    props.attackChain.forEach((action, index) => {
      const actionId = `action_${action.id != null ? action.id : index}`
      const agentId = action.agent_id || 'unknown'
      
      // Get or create agent position
      if (!agentPositions[agentId]) {
        const angle = Math.random() * 2 * Math.PI
        agentPositions[agentId] = {
          x: Math.cos(angle) * 300,
          y: Math.sin(angle) * 300
        }
      }

      const pos = agentPositions[agentId]
      const offsetX = (Math.random() - 0.5) * 50
      const offsetY = (Math.random() - 0.5) * 50

      const actionLabel = action.action_type || 'Action'

      nodes.value.push({
        id: actionId,
        label: actionLabel,
        color: { 
          background: action.success ? '#10b981' : '#ef4444',
          border: action.success ? '#059669' : '#dc2626'
        },
        shape: 'ellipse',
        size: 20,
        x: pos.x + offsetX,
        y: pos.y + offsetY,
        font: { size: 10, color: '#ffffff' },
        action: action,
        title: `${actionLabel}\n${action.result?.description || 'No description'}\nMITRE: ${action.mitre_technique ?? '—'}`
      })

      // Add edge from agent to action
      const agentNodeId = nodeIds.get(agentId)
      if (agentNodeId) {
        edges.value.push({
          from: agentNodeId,
          to: actionId,
          color: { color: action.success ? '#10b981' : '#ef4444' },
          width: action.success ? 3 : 1,
          dashes: !action.success,
          title: `${agentId} → ${actionLabel}`
        })
      }

      // Add edge from last action to this action (chain)
      if (lastActionId && lastActionId !== targetId) {
        edges.value.push({
          from: lastActionId,
          to: actionId,
          color: { color: '#848484' },
          width: 1,
          arrows: { to: { enabled: true, scaleFactor: 0.3 } }
        })
      }

      lastActionId = actionId
    })

    // Add edge from last action to target
    if (lastActionId && lastActionId !== targetId) {
      edges.value.push({
        from: lastActionId,
        to: targetId,
        color: { color: '#fbbf24' },
        width: 2,
        dashes: true,
        title: 'Attack chain targeting'
      })
    }
  }

  // Update network with new data
  nextTick(() => {
    if (network) {
      network.setData({ nodes: nodes.value, edges: edges.value })
      if (!physicsEnabled.value) {
        network.fit({
          animation: {
            duration: 1000,
            easingFunction: 'easeInOutQuad'
          }
        })
      }
    }
  })
}

function togglePhysics() {
  physicsEnabled.value = !physicsEnabled.value
  if (network) {
    network.setOptions({
      physics: { enabled: physicsEnabled.value }
    })
  }
}

function centerGraph() {
  if (network) {
    network.fit({
      animation: {
        duration: 1000,
        easingFunction: 'easeInOutQuad'
      }
    })
  }
}
</script>

<style scoped>
.card {
  @apply rounded-xl border border-slate-200 bg-white p-6 dark:border-dark-800 dark:bg-dark-900;
}

.btn {
  @apply rounded-lg px-3 py-1 text-sm font-medium transition-all duration-200;
}

.btn-primary {
  @apply bg-primary-600 text-white hover:bg-primary-700;
}

.btn-secondary {
  @apply bg-slate-200 text-slate-800 hover:bg-slate-300 dark:bg-dark-700 dark:text-gray-300 dark:hover:bg-dark-600;
}

.btn-sm {
  @apply px-2 py-1 text-xs;
}
</style>
