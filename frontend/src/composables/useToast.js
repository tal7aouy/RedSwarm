import { useToast } from 'vue-toastification'

export function useNotifications() {
  const toast = useToast()

  const success = (message, options = {}) => {
    toast.success(message, {
      icon: '✅',
      ...options
    })
  }

  const error = (message, options = {}) => {
    toast.error(message, {
      icon: '❌',
      ...options
    })
  }

  const info = (message, options = {}) => {
    toast.info(message, {
      icon: 'ℹ️',
      ...options
    })
  }

  const warning = (message, options = {}) => {
    toast.warning(message, {
      icon: '⚠️',
      ...options
    })
  }

  const simulationStarted = (simulationId) => {
    success(`Simulation started! ID: ${simulationId.slice(0, 8)}...`, {
      timeout: 3000
    })
  }

  const simulationCompleted = (simulationId) => {
    success(`Simulation completed! View the report now.`, {
      timeout: 5000
    })
  }

  const simulationStopped = () => {
    info('Simulation stopped by user', {
      timeout: 3000
    })
  }

  const defenseInjected = (defenseType) => {
    warning(`Defense deployed: ${defenseType}`, {
      timeout: 4000
    })
  }

  const reportExported = (format) => {
    success(`Report exported as ${format.toUpperCase()}`, {
      timeout: 3000
    })
  }

  const agentStatus = (agentType, status) => {
    info(`${agentType} agent: ${status}`, {
      timeout: 2000
    })
  }

  return {
    success,
    error,
    info,
    warning,
    simulationStarted,
    simulationCompleted,
    simulationStopped,
    defenseInjected,
    reportExported,
    agentStatus
  }
}
