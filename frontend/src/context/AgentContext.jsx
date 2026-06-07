import { createContext, useContext, useState, useCallback } from 'react'

const AgentContext = createContext(null)

const INITIAL_AGENTS = {
  coordinator: { status: 'idle', label: 'Coordinator' },
  planner: { status: 'idle', label: 'Planner' },
  retrieval: { status: 'idle', label: 'Retrieval' },
  vision: { status: 'idle', label: 'Vision' },
  web_search: { status: 'idle', label: 'Web Search' },
  memory: { status: 'idle', label: 'Memory' },
  critic: { status: 'idle', label: 'Critic' },
  answer: { status: 'idle', label: 'Answer' },
}

export function AgentProvider({ children }) {
  const [agents, setAgents] = useState(INITIAL_AGENTS)
  const [currentPlan, setCurrentPlan] = useState(null)
  const [agentSteps, setAgentSteps] = useState([])

  const updateAgent = useCallback((agentName, updates) => {
    setAgents((prev) => ({
      ...prev,
      [agentName]: { ...prev[agentName], ...updates },
    }))
  }, [])

  const processAgentUpdate = useCallback((statusData) => {
    const { agent, status, ...rest } = statusData
    if (agent) updateAgent(agent, { status, ...rest })
    if (statusData.plan) setCurrentPlan(statusData.plan)
    setAgentSteps((prev) => [...prev, statusData])
  }, [updateAgent])

  const resetAgents = useCallback(() => {
    setAgents(INITIAL_AGENTS)
    setCurrentPlan(null)
    setAgentSteps([])
  }, [])

  return (
    <AgentContext.Provider value={{ agents, currentPlan, agentSteps, updateAgent, processAgentUpdate, resetAgents }}>
      {children}
    </AgentContext.Provider>
  )
}

export const useAgents = () => {
  const ctx = useContext(AgentContext)
  if (!ctx) throw new Error('useAgents must be used inside AgentProvider')
  return ctx
}
