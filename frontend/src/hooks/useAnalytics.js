import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '../services/analyticsService'

export function useAnalytics(days = 7) {
  const overview = useQuery({ queryKey: ['analytics', 'overview'], queryFn: analyticsService.getOverview })
  const usage = useQuery({ queryKey: ['analytics', 'usage', days], queryFn: () => analyticsService.getUsage(days) })
  const agents = useQuery({ queryKey: ['analytics', 'agents'], queryFn: analyticsService.getAgentStats })
  return { overview, usage, agents }
}
