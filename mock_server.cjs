const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Auth
app.post('/api/auth/login', (req, res) => {
  res.json({ access_token: 'mock_access', refresh_token: 'mock_refresh' });
});
app.post('/api/auth/register', (req, res) => {
  res.json({ access_token: 'mock_access', refresh_token: 'mock_refresh' });
});
app.get('/api/auth/me', (req, res) => {
  res.json({ email: 'user@example.com', username: 'Demo User' });
});

// Analytics
app.get('/api/analytics/overview', (req, res) => {
  res.json({ totalDocuments: 42, activeAgents: 8, totalQueries: 1337, accuracy: 0.95 });
});
app.get('/api/analytics/usage', (req, res) => {
  res.json([
    { date: '2023-10-01', queries: 10 },
    { date: '2023-10-02', queries: 25 },
    { date: '2023-10-03', queries: 15 },
    { date: '2023-10-04', queries: 40 },
    { date: '2023-10-05', queries: 35 },
  ]);
});
app.get('/api/analytics/agents', (req, res) => {
  res.json([
    { name: 'Coordinator', calls: 150 },
    { name: 'Planner', calls: 120 },
    { name: 'Retrieval', calls: 200 },
    { name: 'Vision', calls: 45 },
  ]);
});
app.get('/api/analytics/documents', (req, res) => {
  res.json([
    { type: 'PDF', count: 20 },
    { type: 'Image', count: 15 },
    { type: 'Audio', count: 5 },
    { type: 'Excel', count: 2 },
  ]);
});

// Documents
app.get('/api/documents/', (req, res) => {
  res.json({
    items: [
      { id: '1', filename: 'report.pdf', type: 'application/pdf', size: 1024000, status: 'ready', uploadedAt: new Date().toISOString() },
      { id: '2', filename: 'chart.png', type: 'image/png', size: 512000, status: 'ready', uploadedAt: new Date().toISOString() },
    ],
    total: 2,
    page: 1,
    size: 10
  });
});

// Chat
app.get('/api/chat/sessions', (req, res) => {
  res.json({ sessions: [
    { id: 's1', title: 'Q3 Financials', updatedAt: new Date().toISOString() },
    { id: 's2', title: 'Architecture Review', updatedAt: new Date().toISOString() }
  ]});
});
app.get('/api/chat/sessions/:id', (req, res) => {
  res.json({
    id: req.params.id,
    messages: [
      { role: 'user', content: 'What is our revenue?' },
      { role: 'assistant', content: 'Based on the Q3 report, revenue is $1M.' }
    ]
  });
});
app.post('/api/chat/message', (req, res) => {
  res.json({ role: 'assistant', content: 'This is a mocked response from the assistant.', citations: [] });
});

// Catch-all
app.use((req, res) => {
  res.status(404).json({ error: 'Mock not found for ' + req.url });
});

const PORT = 8000;
app.listen(PORT, () => {
  console.log(`Mock server running on http://localhost:${PORT}`);
});
