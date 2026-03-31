import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Simulation from '../views/Simulation.vue'
import Scenarios from '../views/Scenarios.vue'
import Reports from '../views/Reports.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/simulation/:id',
      name: 'simulation',
      component: Simulation
    },
    {
      path: '/scenarios',
      name: 'scenarios',
      component: Scenarios
    },
    {
      path: '/reports',
      name: 'reports',
      component: Reports
    }
  ]
})

export default router
