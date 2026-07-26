/* ============================================================
   charts.js
   Depends on: auth.js, api.js, Chart.js (loaded before this file)
   ============================================================ */

const CATEGORY_COLORS = {
  Food: '#52d16a', Housing: '#d9a441', Transport: '#4aa8ea', Health: '#ef5f6c',
  Entertainment: '#b587f0', Shopping: '#e08a3d', Education: '#4bcf8a', Other: '#9aa3b2'
};

function fmtMoney(n){
  const num = Number(n) || 0;
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

let monthlyChart, categoryChart, breakdownChart;
let currentRange = 'year';

const RANGE_LABELS = {
  week: 'Last 7 Days', month: 'Last Month', half_year: 'Last 6 Months',
  year: 'Last 12 Months', all: 'All Time'
};

/* Wire up the range buttons FIRST, before touching the Chart global at all.
   If the Chart.js CDN script fails to load for any reason, that must not
   prevent these listeners from being attached — otherwise the buttons
   look completely dead with no way to tell why. */
document.querySelectorAll('.range-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentRange = btn.dataset.range;
    document.getElementById('breakdownTitle').textContent = `Category Breakdown — ${RANGE_LABELS[currentRange]}`;
    loadAllCharts();
  });
});

if(typeof Chart === 'undefined'){
  console.error('Chart.js failed to load — check your network/CDN access. Charts will not render.');
} else {
  Chart.defaults.color = '#8891a3';
  Chart.defaults.borderColor = '#232a36';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
}

async function loadMonthlyChart(){
  const ctx = document.getElementById('monthlyChart');
  if(typeof Chart === 'undefined'){
    ctx.parentElement.innerHTML = '<p class="error-text">Charts failed to load. Check your network/CDN access and reload.</p>';
    return;
  }

  const { ok, data } = await api.getMonthlySummary(currentRange);
  if(monthlyChart) monthlyChart.destroy();

  const labels = ok && data ? data.labels : [];
  const totals = ok && data ? data.totals : [];

  monthlyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: totals,
        borderColor: '#34c759',
        backgroundColor: 'rgba(52,199,89,0.08)',
        pointBackgroundColor: '#34c759',
        pointRadius: 4,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { callback: v => '$' + v } },
        x: { grid: { display: false } }
      }
    }
  });
}

async function loadCategoryChart(){
  const ctx = document.getElementById('categoryChart');
  const legend = document.getElementById('categoryLegend');
  if(typeof Chart === 'undefined') return; // already reported by loadMonthlyChart

  const { ok, data } = await api.getCategorySummary(currentRange);
  if(categoryChart) categoryChart.destroy();

  const rows = ok && data ? data : [];
  const labels = rows.map(r => r.category);
  const values = rows.map(r => r.total);
  const colors = labels.map(c => CATEGORY_COLORS[c] || '#9aa3b2');

  categoryChart = new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: { legend: { display: false } }
    }
  });

  legend.innerHTML = rows.map(r => `
    <div class="legend-row">
      <span class="legend-dot" style="background:${CATEGORY_COLORS[r.category] || '#9aa3b2'}"></span>
      <span class="legend-name">${r.category}</span>
      <span class="legend-amount">${fmtMoney(r.total)}</span>
    </div>
  `).join('') || '<p class="empty-state">No data for this range.</p>';
}

async function loadBreakdownChart(){
  const ctx = document.getElementById('breakdownChart');
  if(typeof Chart === 'undefined') return; // already reported by loadMonthlyChart

  const { ok, data } = await api.getCategoryBreakdown(currentRange);
  if(breakdownChart) breakdownChart.destroy();

  const labels = ok && data ? data.labels : [];
  const datasets = ok && data ? data.datasets : [];

  breakdownChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: datasets.map(ds => ({
        label: ds.category,
        data: ds.data,
        backgroundColor: CATEGORY_COLORS[ds.category] || '#9aa3b2'
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 9, boxHeight: 9 } } },
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: { stacked: true, beginAtZero: true, ticks: { callback: v => '$' + v } }
      }
    }
  });
}

function loadAllCharts(){
  loadMonthlyChart();
  loadCategoryChart();
  loadBreakdownChart();
}

loadAllCharts();
