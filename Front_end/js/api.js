/* ============================================================
   api.js — central place for talking to the FastAPI backend.
   Depends on auth.js being loaded first (uses API_BASE, getToken).
   ============================================================ */

/**
 * Wraps fetch(): attaches Authorization header, parses JSON,
 * and auto-redirects to login on a 401.
 * Returns { ok, status, data } — never throws for normal HTTP errors.
 */
async function apiFetch(path, options = {}){
  try{
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
        ...(options.headers || {})
      }
    });

    if(res.status === 401){
      sessionStorage.removeItem('token');
      window.location.href = 'login.html';
      return { ok: false, status: 401, data: null };
    }

    const data = await res.json().catch(() => null);
    return { ok: res.ok, status: res.status, data };
  } catch(err){
    console.error('Network error calling', path, err);
    return { ok: false, status: 0, data: null, networkError: true };
  }
}

const api = {
  // -------- expenses --------
  getTodayExpenses: () => apiFetch('/expenses/today'),
  getExpenses: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/expenses/${qs ? '?' + qs : ''}`);
  },
  addExpense: (payload) => apiFetch('/expenses/', { method: 'POST', body: JSON.stringify(payload) }),
  deleteExpense: (id) => apiFetch(`/expenses/${id}`, { method: 'DELETE' }),

  // -------- analytics --------
  getSummary: () => apiFetch('/analytics/summary'),
  getMonthlySummary: (range) => apiFetch(`/analytics/monthly-summary?range=${range}`),
  getCategorySummary: (range) => apiFetch(`/analytics/category-summary?range=${range}`),
  getCategoryBreakdown: (range) => apiFetch(`/analytics/category-breakdown?range=${range}`)
};
