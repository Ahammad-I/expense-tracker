const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method: options.method || 'GET',

    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },

    body: options.body || undefined,
  })

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    const err = new Error(data?.error || `HTTP ${res.status}`)
    err.details = data?.details || {}
    err.status = res.status
    throw err
  }

  return data
}

/** GET /api/v1/expenses/?category=&sort=date_desc */
export function fetchExpenses({ category = '', sort = 'date_desc' } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (sort) params.set('sort', sort)
  const qs = params.toString() ? `?${params}` : ''
  return request(`/api/v1/expenses/${qs}`)
}

/** POST /api/v1/expenses/ — idempotent via Idempotency-Key header */
export function createExpense(body, idempotencyKey) {
  return request('/api/v1/expenses/', {
    method: 'POST',
    headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {},
    body: JSON.stringify(body),
  })
}

/** GET /api/v1/expenses/categories/ */
export function fetchCategories() {
  return request('/api/v1/expenses/categories/')
}

/** GET /api/v1/expenses/summary/ */
export function fetchSummary() {
  return request('/api/v1/expenses/summary/')
}