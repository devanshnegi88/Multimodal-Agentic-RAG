import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
export default function AccuracyChart({ data = [] }) {
  return (
    <div className="chart-card">
      <div className="chart-card-title">Answer Accuracy Trend</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis domain={[0,100]} tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-border)', borderRadius: 8 }} />
          <Line type="monotone" dataKey="score" stroke="#34d399" strokeWidth={2} dot={{ fill: '#34d399', r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
