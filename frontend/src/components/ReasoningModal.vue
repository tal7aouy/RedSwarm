<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="close">
    <div class="bg-white dark:bg-dark-900 rounded-xl max-w-4xl w-full max-h-[80vh] m-4 overflow-hidden" @click.stop>
      <div class="p-6 border-b border-gray-200 dark:border-dark-800">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
            <Brain class="w-5 h-5 mr-2 text-primary-500" />
            Agent Reasoning: {{ action.action_type }}
          </h3>
          <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          <span class="badge badge-info">{{ agentType }}</span>
          <span class="ml-2">{{ new Date(action.timestamp).toLocaleString() }}</span>
        </div>
      </div>
      
      <div class="p-6 overflow-y-auto max-h-[60vh]">
        <div v-if="action.llm_reasoning" class="space-y-4">
          <div>
            <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Claude's Reasoning</h4>
            <div class="bg-gray-50 dark:bg-dark-800 rounded-lg p-4 border border-gray-200 dark:border-dark-700">
              <pre class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">{{ formatReasoning(action.llm_reasoning) }}</pre>
            </div>
          </div>
          
          <div v-if="parsedReasoning">
            <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Parsed Analysis</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-if="parsedReasoning.analysis" class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                <h5 class="font-medium text-blue-900 dark:text-blue-300 mb-2">Analysis</h5>
                <p class="text-sm text-blue-800 dark:text-blue-200">{{ parsedReasoning.analysis }}</p>
              </div>
              
              <div v-if="parsedReasoning.rationale" class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                <h5 class="font-medium text-green-900 dark:text-green-300 mb-2">Rationale</h5>
                <p class="text-sm text-green-800 dark:text-green-200">{{ parsedReasoning.rationale }}</p>
              </div>
              
              <div v-if="parsedReasoning.expected_outcome" class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                <h5 class="font-medium text-purple-900 dark:text-purple-300 mb-2">Expected Outcome</h5>
                <p class="text-sm text-purple-800 dark:text-purple-200">{{ parsedReasoning.expected_outcome }}</p>
              </div>
              
              <div v-if="parsedReasoning.next_steps" class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
                <h5 class="font-medium text-orange-900 dark:text-orange-300 mb-2">Next Steps</h5>
                <p class="text-sm text-orange-800 dark:text-orange-200">{{ parsedReasoning.next_steps }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8">
          <Brain class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500 dark:text-gray-400">No LLM reasoning available for this action</p>
          <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">This action was executed using fallback logic</p>
        </div>
        
        <div class="mt-6 pt-6 border-t border-gray-200 dark:border-dark-800">
          <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Action Result</h4>
          <div class="bg-gray-50 dark:bg-dark-800 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-900 dark:text-white">Status:</span>
              <span :class="action.result?.success ? 'text-green-600' : 'text-red-600'">
                {{ action.result?.success ? 'Success' : 'Failed' }}
              </span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ action.result?.description || 'No description available' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Brain, X } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  action: Object,
  agentType: String
})

const emit = defineEmits(['close'])

const parsedReasoning = computed(() => {
  if (!props.action.llm_reasoning) return null
  
  try {
    const parsed = JSON.parse(props.action.llm_reasoning)
    return parsed
  } catch {
    // Try to extract key information from raw text
    const text = props.action.llm_reasoning
    const result = {}
    
    // Look for common patterns in LLM responses
    if (text.toLowerCase().includes('analysis')) {
      const match = text.match(/analysis[:\s]+([^.\n]+)/i)
      if (match) result.analysis = match[1].trim()
    }
    
    if (text.toLowerCase().includes('rationale') || text.toLowerCase().includes('reasoning')) {
      const match = text.match(/(?:rationale|reasoning)[:\s]+([^.\n]+)/i)
      if (match) result.rationale = match[1].trim()
    }
    
    if (text.toLowerCase().includes('expected') || text.toLowerCase().includes('outcome')) {
      const match = text.match(/(?:expected|outcome)[:\s]+([^.\n]+)/i)
      if (match) result.expected_outcome = match[1].trim()
    }
    
    if (text.toLowerCase().includes('next')) {
      const match = text.match(/next[:\s]+([^.\n]+)/i)
      if (match) result.next_steps = match[1].trim()
    }
    
    return Object.keys(result).length > 0 ? result : null
  }
})

const formatReasoning = (reasoning) => {
  try {
    // Try to parse and format as JSON
    const parsed = JSON.parse(reasoning)
    return JSON.stringify(parsed, null, 2)
  } catch {
    // Return as plain text if not valid JSON
    return reasoning
  }
}

const close = () => {
  emit('close')
}
</script>
