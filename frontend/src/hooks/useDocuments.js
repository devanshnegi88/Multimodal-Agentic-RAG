import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentService } from '../services/documentService'
import toast from 'react-hot-toast'

export function useDocuments(params = {}) {
  const queryClient = useQueryClient()

  const list = useQuery({
    queryKey: ['documents', params],
    queryFn: () => documentService.listDocuments(params),
  })

  const remove = useMutation({
    mutationFn: documentService.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('Document deleted')
    },
    onError: () => toast.error('Failed to delete'),
  })

  return { list, remove }
}
