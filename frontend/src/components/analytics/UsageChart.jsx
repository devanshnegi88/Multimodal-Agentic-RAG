import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function UsageChart({ data = [] }) {
  return (
    <div className="chart-card">
      <div className="chart-card-title">Daily Queries</div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="queryGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-border)', borderRadius: 8 }} />
          <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#queryGrad)" strokeWidth={2} dot={{ fill: '#6366f1', r: 3 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
