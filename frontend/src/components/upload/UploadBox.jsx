import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Image, Music, Video, Table } from 'lucide-react'
import { uploadService } from '../../services/uploadService'
import UploadProgress from './UploadProgress'
import toast from 'react-hot-toast'
import '../../styles/upload.css'

const FILE_ICONS = {
  pdf: <FileText size={16} />, docx: <FileText size={16} />,
  png: <Image size={16} />, jpg: <Image size={16} />, jpeg: <Image size={16} />,
  mp3: <Music size={16} />, wav: <Music size={16} />,
  mp4: <Video size={16} />, mov: <Video size={16} />,
  xlsx: <Table size={16} />, csv: <Table size={16} />,
}

export default function UploadBox({ onUploaded }) {
  const [uploads, setUploads] = useState([])

  const onDrop = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles.length) return

    const newUploads = acceptedFiles.map(f => ({ file: f, progress: 0, status: 'uploading', id: null }))
    setUploads(newUploads)

    try {
      const result = await uploadService.uploadFiles(acceptedFiles, (pct) => {
        setUploads(prev => prev.map(u => ({ ...u, progress: pct })))
      })

      setUploads(prev => prev.map((u, i) => ({
        ...u, progress: 100, status: 'processing',
        id: result.uploaded[i]?.id,
      })))

      // Poll each doc
      result.uploaded.forEach((doc) => {
        uploadService.pollStatus(doc.id, (status) => {
          setUploads(prev => prev.map(u =>
            u.id === doc.id ? { ...u, status: status.status } : u
          ))
          if (status.status === 'ready') {
            toast.success(`${doc.original_name} ready`)
            onUploaded?.(doc)
          }
        })
      })
    } catch (e) {
      toast.error('Upload failed')
      setUploads([])
    }
  }, [onUploaded])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'audio/*': ['.mp3', '.wav', '.m4a'],
      'video/*': ['.mp4', '.mov', '.avi'],
      'application/vnd.ms-excel': ['.xlsx', '.xls'],
      'text/csv': ['.csv'],
      'text/plain': ['.txt', '.md'],
    },
  })

  return (
    <div>
      <div {...getRootProps()} className={`upload-box ${isDragActive ? 'drag-over' : ''}`}>
        <input {...getInputProps()} />
        <div className="upload-icon">
          <Upload size={40} color="var(--color-primary)" />
        </div>
        <p className="upload-text">
          <strong>{isDragActive ? 'Drop files here' : 'Drag & drop files here'}</strong>
        </p>
        <p className="upload-text" style={{ marginTop: 4 }}>or click to browse</p>
        <div className="file-type-chips">
          {['PDF', 'Images', 'Audio', 'Video', 'Excel', 'CSV', 'PPTX'].map(t => (
            <span key={t} className="badge badge-primary">{t}</span>
          ))}
        </div>
      </div>

      {uploads.length > 0 && (
        <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {uploads.map((u, i) => <UploadProgress key={i} upload={u} />)}
        </div>
      )}
    </div>
  )
}
