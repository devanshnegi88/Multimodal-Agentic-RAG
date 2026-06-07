import { useState, useCallback } from 'react'
import { uploadService } from '../services/uploadService'
import toast from 'react-hot-toast'

export function useUpload() {
  const [uploads, setUploads] = useState([])
  const [uploading, setUploading] = useState(false)

  const upload = useCallback(async (files) => {
    setUploading(true)
    try {
      const result = await uploadService.uploadFiles(files, (pct) => {
        setUploads(prev => prev.map(u => ({ ...u, progress: pct })))
      })
      toast.success(`${result.count} file(s) uploaded`)
      return result
    } catch (e) {
      toast.error('Upload failed')
      throw e
    } finally {
      setUploading(false)
    }
  }, [])

  return { uploads, uploading, upload }
}
