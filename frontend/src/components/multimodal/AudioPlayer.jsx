import { useRef, useState } from 'react'
import { Play, Pause, Volume2 } from 'lucide-react'
export default function AudioPlayer({ src }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const toggle = () => { if (playing) audioRef.current.pause(); else audioRef.current.play(); setPlaying(p => !p) }
  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
      <audio ref={audioRef} src={src} onTimeUpdate={e => setProgress(e.target.currentTime / e.target.duration * 100)} onEnded={() => setPlaying(false)} />
      <button onClick={toggle} style={{ width: 40, height: 40, background: 'var(--color-primary)', border: 'none', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', flexShrink: 0 }}>
        {playing ? <Pause size={16} /> : <Play size={16} />}
      </button>
      <div style={{ flex: 1 }}><div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }} /></div></div>
      <Volume2 size={16} color="var(--color-text-secondary)" />
    </div>
  )
}
