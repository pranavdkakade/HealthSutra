const API_BASE = `${import.meta.env.VITE_API_URL || ''}/api/v1`;

export async function sendChatMessage(question, language = 'en', sessionId = null) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question,
      language,
      session_id: sessionId
    })
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE}/documents`);
  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.statusText}`);
  }
  return await response.json();
}

export async function submitFeedback(data) {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return await response.json();
}

export async function fetchSystemHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchEvaluationSummary() {
  const response = await fetch(`${API_BASE}/evaluation`);
  if (!response.ok) {
    throw new Error(`Evaluation fetch failed: ${response.statusText}`);
  }
  return await response.json();
}

export async function fetchAdminAnalytics() {
  const response = await fetch(`${API_BASE}/admin/analytics`);
  if (!response.ok) {
    throw new Error(`Admin analytics fetch failed: ${response.statusText}`);
  }
  return await response.json();
}
