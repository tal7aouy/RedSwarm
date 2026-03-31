import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useSimulationStore = defineStore('simulation', () => {
  const simulations = ref([])
  const currentSimulation = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function startSimulation(config) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/simulation/start', config)
      currentSimulation.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to start simulation'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getSimulationStatus(simulationId) {
    try {
      const response = await api.get(`/simulation/${simulationId}/status`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get status'
      throw err
    }
  }

  async function getSimulationReport(simulationId) {
    try {
      const response = await api.get(`/simulation/${simulationId}/report`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get report'
      throw err
    }
  }

  async function stopSimulation(simulationId) {
    try {
      const response = await api.post(`/simulation/${simulationId}/stop`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to stop simulation'
      throw err
    }
  }

  async function listSimulations() {
    loading.value = true
    try {
      const response = await api.get('/simulation/list')
      simulations.value = response.data.simulations
      return response.data.simulations
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to list simulations'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function injectDefense(simulationId, defense) {
    try {
      const response = await api.post(`/god-mode/${simulationId}/inject`, defense)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to inject defense'
      throw err
    }
  }

  return {
    simulations,
    currentSimulation,
    loading,
    error,
    startSimulation,
    getSimulationStatus,
    getSimulationReport,
    stopSimulation,
    listSimulations,
    injectDefense
  }
})
