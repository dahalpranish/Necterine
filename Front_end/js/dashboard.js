/* ============================================================
   dashboard.js
   Depends on: auth.js, api.js (loaded before this file)
   ============================================================ */

const CATEGORY_META = {
  Food:          { badge: 'badge-food',          color: '#52d16a' },
  Housing:       { badge: 'badge-housing',       color: '#d9a441' },
  Transport:     { badge: 'badge-transport',     color: '#4aa8ea' },
  Health:        { badge: 'badge-health',        color: '#ef5f6c' },
  Entertainment: { badge: 'badge-entertainment', color: '#b587f0' },
  Shopping:      { badge: 'badge-shopping',      color: '#e08a3d' },
  Education:     { badge: 'badge-education',     color: '#4bcf8a' },
  Other:         { badge: 'badge-other',         color: '#9aa3b2' }
};

function fmtMoney(n){
  const num = Number(n) || 0;
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtShortDate(dateStr){
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/* ---------------- category pill selection ---------------- */
let selectedCategory = 'Food';
document.getElementById('categoryGrid').addEventListener('click', (e) => {
  const pill = e.target.closest('.category-pill');
  if(!pill) return;
  document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('selected'));
  pill.classList.add('selected');
  selectedCategory = pill.dataset.category;
});

/* ---------------- date picker (Add Expense) ---------------- */
function todayISO(){
  return new Date().toISOString().slice(0, 10);
}
const expDatePicker = createDatePicker(document.getElementById('expDateHost'), {
  hiddenInputId: 'expDate',
  initialValue: todayISO()
});

/* ---------------- load stat cards ---------------- */
async function loadSummary(){
  const { ok, data } = await api.getSummary();
  if(!ok || !data) return;

  document.getElementById('statThisMonth').textContent = fmtMoney(data.this_month_total);
  document.getElementById('statLastMonth').textContent = fmtMoney(data.last_month_total);
  document.getElementById('statEntryCount').textContent = data.this_month_count ?? 0;
  document.getElementById('statTopCategory').textContent = data.top_category || '—';

  const diff = data.percent_change_vs_last_month;
  if(typeof diff === 'number'){
    const sub = document.getElementById('statVsLastMonth');
    sub.textContent = `${diff >= 0 ? '+' : ''}${diff.toFixed(1)}% vs last month`;
    sub.className = 'stat-sub ' + (diff <= 0 ? 'up' : '');
  }
}

/* ---------------- load today's expenses only ---------------- */
async function loadRecent(){
  const container = document.getElementById('recentList');
  const { ok, data } = await api.getTodayExpenses();

  if(!ok){
    container.innerHTML = '<p class="error-text">Could not load today\'s expenses.</p>';
    return;
  }
  if(!data || data.length === 0){
    container.innerHTML = '<p class="empty-state">No expenses logged today yet.</p>';
    return;
  }

  container.innerHTML = data.map(exp => {
    const meta = CATEGORY_META[exp.category] || CATEGORY_META.Other;
    return `
      <div class="expense-row">
        <div class="expense-icon" style="background:${meta.color}22; color:${meta.color}">
          ${exp.category.charAt(0)}
        </div>
        <div class="expense-main">
          <div class="expense-desc">${exp.description}</div>
          <div class="expense-meta">${fmtShortDate(exp.date)} · ${exp.category}</div>
        </div>
        <div class="expense-amount">${fmtMoney(exp.price)}</div>
      </div>
    `;
  }).join('');
}

/* ---------------- add expense form ---------------- */
document.getElementById('expenseForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errorEl = document.getElementById('formError');
  errorEl.style.display = 'none';

  const payload = {
    date: document.getElementById('expDate').value,
    description: document.getElementById('expDesc').value.trim(),
    category: selectedCategory,
    price: parseFloat(document.getElementById('expAmount').value)
  };

  if(!payload.date || !payload.description || isNaN(payload.price)){
    errorEl.textContent = 'Please fill out every field.';
    errorEl.style.display = 'block';
    return;
  }

  const btn = document.getElementById('addExpenseBtn');
  btn.disabled = true;
  btn.textContent = 'Adding...';

  const { ok, data } = await api.addExpense(payload);

  btn.disabled = false;
  btn.textContent = 'Add Expense';

  if(!ok){
    errorEl.textContent = (data && data.detail) || 'Something went wrong. Please try again.';
    errorEl.style.display = 'block';
    return;
  }

  document.getElementById('expenseForm').reset();
  expDatePicker.setValue(todayISO());
  document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('selected'));
  document.querySelector('.category-pill[data-category="Food"]').classList.add('selected');
  selectedCategory = 'Food';

  loadSummary();
  loadRecent();
});

loadSummary();
loadRecent();
