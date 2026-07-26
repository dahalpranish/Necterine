/* ============================================================
   history.js
   Depends on: auth.js, api.js (loaded before this file)
   ============================================================ */

function fmtMoney(n){
  const num = Number(n) || 0;
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmtTableDate(dateStr){
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function badgeClass(category){
  return 'badge-' + (category || 'other').toLowerCase();
}

const searchInput   = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const dateFilter     = document.getElementById('dateFilter');
const sortFilter     = document.getElementById('sortFilter');
const tbody          = document.getElementById('historyBody');

/* The from/to pickers sit in a fixed spot in the toolbar at all times.
   Picking a custom range silently overrides whatever the dropdown says —
   the dropdown itself never shows or needs a "Custom" option. */
const rangeStart = createDatePicker(document.getElementById('rangeStartHost'), {
  hiddenInputId: 'customStart',
  placeholder: 'From',
  onChange: () => loadHistory()
});
const rangeEnd = createDatePicker(document.getElementById('rangeEndHost'), {
  hiddenInputId: 'customEnd',
  placeholder: 'To',
  onChange: () => loadHistory()
});

/* Choosing a preset from the dropdown clears any custom range so it
   doesn't silently keep overriding the preset the user just picked. */
dateFilter.addEventListener('change', () => {
  rangeStart.setValue(null);
  rangeEnd.setValue(null);
  loadHistory();
});

categoryFilter.addEventListener('change', loadHistory);
sortFilter.addEventListener('change', loadHistory);

/* debounce free-text search so we don't hammer the API on every keystroke */
let searchTimer = null;
searchInput.addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadHistory, 350);
});

async function loadHistory(){
  tbody.innerHTML = '<tr><td colspan="4"><p class="loading-text">Loading...</p></td></tr>';

  const start = rangeStart.getValue();
  const end = rangeEnd.getValue();
  const hasCustomRange = start && end;

  const params = {
    search: searchInput.value.trim(),
    category: categoryFilter.value,
    sort: sortFilter.value,
    // a completed custom range always wins over the dropdown's preset
    date_filter: hasCustomRange ? 'custom' : dateFilter.value
  };
  if(hasCustomRange){
    params.start_date = start;
    params.end_date = end;
  }
  // drop empty params so the querystring stays clean
  Object.keys(params).forEach(k => { if(!params[k]) delete params[k]; });

  const { ok, data } = await api.getExpenses(params);

  if(!ok){
    tbody.innerHTML = '<tr><td colspan="4"><p class="error-text">Could not load history.</p></td></tr>';
    return;
  }
  if(!data || data.length === 0){
    tbody.innerHTML = '<tr><td colspan="4"><p class="empty-state">No expenses match these filters.</p></td></tr>';
    return;
  }

  tbody.innerHTML = data.map(exp => `
    <tr data-id="${exp.id}">
      <td class="date-col">${fmtTableDate(exp.date)}</td>
      <td>${exp.description}</td>
      <td><span class="badge ${badgeClass(exp.category)}">${exp.category}</span></td>
      <td class="amount">
        ${fmtMoney(exp.price)}
        <button class="delete-link" data-id="${exp.id}">Delete</button>
      </td>
    </tr>
  `).join('');
}

tbody.addEventListener('click', async (e) => {
  const btn = e.target.closest('.delete-link');
  if(!btn) return;

  const id = btn.dataset.id;
  const row = btn.closest('tr');
  btn.disabled = true;
  btn.textContent = '...';

  const { ok } = await api.deleteExpense(id);

  if(ok){
    row.remove();
    if(!tbody.querySelector('tr')){
      tbody.innerHTML = '<tr><td colspan="4"><p class="empty-state">No expenses match these filters.</p></td></tr>';
    }
  } else {
    btn.disabled = false;
    btn.textContent = 'Delete';
  }
});

loadHistory();
