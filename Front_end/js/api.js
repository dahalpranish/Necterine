/* ============================================================
   api.js — central place for talking to the FastAPI backend.
   Depends on auth.js being loaded first (uses API_BASE, getToken).
   ============================================================ */

/**
 * Wraps fetch(): attaches Authorization header, parses JSON.
 * On a 401, tries /auth/refresh (uses the httponly refresh cookie, via the
 * shared refreshAccessToken() defined in auth.js) once, and if that succeeds,
 * retries the original request with the new token.
 * Only redirects to login.html if refresh also fails.
 * Returns { ok, status, data } — never throws for normal HTTP errors.
 */

async function apiFetch(path, options = {}, _isRetry = false){
  try{
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
        ...(options.headers || {})
      }
    });

    if(res.status === 401){
      if(_isRetry){
        // already retried once with a fresh token and still 401 — give up
        goToLogin();
        return { ok: false, status: 401, data: null };
      }
      const newToken = await refreshAccessToken();
      if(!newToken){
        goToLogin();
        return { ok: false, status: 401, data: null };
      }
      return apiFetch(path, options, true); // retry once with fresh token
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
