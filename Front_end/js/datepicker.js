/* ============================================================
   datepicker.js — reusable custom calendar widget.
   Native <input type="date"> can't be restyled or restructured
   (it's rendered by the browser itself), so this replaces it
   everywhere a date needs to be picked: Add Expense (dashboard)
   and the custom range in History.

   Navigation model: year grid (5x5, paged 25 at a time) ->
   month grid (12 months for that year) -> day grid (only the
   selected month's real days; blank cells around them, never
   another month's numbers).

   Usage:
     const picker = createDatePicker(hostElement, {
       hiddenInputId: 'expDate',      // id given to the underlying <input type="hidden">
       initialValue: '2026-07-17',    // ISO date or null
       placeholder: 'mm/dd/yyyy',
       onChange: (iso) => { ... }
     });
     picker.getValue() / picker.setValue('2026-07-01' | null)
   ============================================================ */

function createDatePicker(host, options = {}){
  const {
    hiddenInputId,
    placeholder = 'mm/dd/yyyy',
    initialValue = null,
    onChange = () => {}
  } = options;

  const WEEKDAYS = ['Su','Mo','Tu','We','Th','Fr','Sa'];
  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

  function todayParts(){
    const t = new Date();
    return { y: t.getFullYear(), m: t.getMonth(), d: t.getDate() };
  }
  function parseISO(iso){
    const [y, m, d] = iso.split('-').map(Number);
    return { y, m: m - 1, d };
  }
  function toISO(y, m, d){
    return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  }
  function toDisplay(y, m, d){
    return `${String(m + 1).padStart(2, '0')}/${String(d).padStart(2, '0')}/${y}`;
  }

  let selected = initialValue ? parseISO(initialValue) : null;
  let viewDate = selected ? { y: selected.y, m: selected.m } : todayParts();
  let yearRangeStart = viewDate.y - 12;
  let view = 'days'; // 'days' | 'months' | 'years'
  let open = false;

  host.innerHTML = `
    <div class="dp-wrap">
      <button type="button" class="dp-trigger">
        <span class="dp-trigger-text"></span>
        <svg class="dp-cal-icon" viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M3 9H21" stroke="currentColor" stroke-width="1.6"/><path d="M8 3V6M16 3V6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      </button>
      <div class="dp-panel" hidden>
        <div class="dp-header">
          <button type="button" class="dp-nav dp-prev" title="Previous">&#9650;</button>
          <button type="button" class="dp-label"></button>
          <button type="button" class="dp-nav dp-next" title="Next">&#9660;</button>
        </div>
        <div class="dp-body"></div>
        <div class="dp-footer">
          <button type="button" class="dp-clear">Clear</button>
          <button type="button" class="dp-today">Today</button>
        </div>
      </div>
      <input type="hidden" id="${hiddenInputId}" value="${initialValue || ''}">
    </div>
  `;

  const trigger     = host.querySelector('.dp-trigger');
  const trigText    = host.querySelector('.dp-trigger-text');
  const panel       = host.querySelector('.dp-panel');
  const label       = host.querySelector('.dp-label');
  const body        = host.querySelector('.dp-body');
  const prevBtn     = host.querySelector('.dp-prev');
  const nextBtn     = host.querySelector('.dp-next');
  const clearBtn    = host.querySelector('.dp-clear');
  const todayBtn    = host.querySelector('.dp-today');
  const hiddenInput = host.querySelector(`#${CSS.escape(hiddenInputId)}`);

  function renderTrigger(){
    trigText.textContent = selected ? toDisplay(selected.y, selected.m, selected.d) : placeholder;
    trigText.style.color = selected ? 'var(--text)' : '#57606f';
  }

  function openPanel(){
    open = true;
    panel.hidden = false;
    view = 'days';
    if(selected) viewDate = { y: selected.y, m: selected.m };
    renderView();
  }
  function closePanel(){
    open = false;
    panel.hidden = true;
  }

  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    open ? closePanel() : openPanel();
  });
  document.addEventListener('click', (e) => {
    if(open && !host.contains(e.target)) closePanel();
  });

  /* Clicking the header label always starts from year selection first,
     per spec: year -> month -> day. */
  label.addEventListener('click', (e) => {
    e.stopPropagation();
    view = 'years';
    yearRangeStart = viewDate.y - 12;
    renderView();
  });

  prevBtn.addEventListener('click', (e) => { e.stopPropagation(); step(-1); });
  nextBtn.addEventListener('click', (e) => { e.stopPropagation(); step(1); });

  function step(dir){
    if(view === 'days'){
      let m = viewDate.m + dir, y = viewDate.y;
      if(m < 0){ m = 11; y--; }
      if(m > 11){ m = 0; y++; }
      viewDate = { y, m };
    } else if(view === 'months'){
      viewDate = { y: viewDate.y + dir, m: viewDate.m };
    } else if(view === 'years'){
      yearRangeStart += dir * 25;
    }
    renderView();
  }

  clearBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selected = null;
    hiddenInput.value = '';
    renderTrigger();
    onChange(null);
    closePanel();
  });
  todayBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const t = todayParts();
    selected = t;
    viewDate = { y: t.y, m: t.m };
    hiddenInput.value = toISO(t.y, t.m, t.d);
    renderTrigger();
    onChange(hiddenInput.value);
    closePanel();
  });

  function renderView(){
    if(view === 'days') return renderDays();
    if(view === 'months') return renderMonths();
    if(view === 'years') return renderYears();
  }

  /* Day grid: only ever as many rows as this specific month needs
     (usually 5, occasionally 6 for a 31-day month starting late in
     the week) — never padded with the previous/next month's dates. */
  function renderDays(){
    label.textContent = `${MONTHS[viewDate.m]} ${viewDate.y}`;

    const daysInMonth = new Date(viewDate.y, viewDate.m + 1, 0).getDate();
    let startDay = new Date(viewDate.y, viewDate.m, 1).getDay();
    // Always fit in 5 rows (35 cells). If the real weekday offset would
    // push the month into a 6th row (e.g. a 31-day month starting on a
    // Friday/Saturday), drop the offset entirely and start day 1 in the
    // first cell instead — every day stays visible, none get cut off.
    if(startDay + daysInMonth > 35) startDay = 0;
    const rows = 5;
    const t = todayParts();

    let html = `<div class="dp-weekdays">${WEEKDAYS.map(w => `<span>${w}</span>`).join('')}</div>`;
    html += `<div class="dp-days-grid" style="grid-template-rows: repeat(${rows}, 1fr)">`;

    for(let i = 0; i < rows * 7; i++){
      const dayNum = i - startDay + 1;
      if(dayNum < 1 || dayNum > daysInMonth){
        html += `<span class="dp-cell dp-blank"></span>`;
        continue;
      }
      const isSelected = selected && selected.y === viewDate.y && selected.m === viewDate.m && selected.d === dayNum;
      const isToday = t.y === viewDate.y && t.m === viewDate.m && t.d === dayNum;
      html += `<button type="button" class="dp-cell dp-day ${isSelected ? 'selected' : ''} ${isToday && !isSelected ? 'is-today' : ''}" data-day="${dayNum}">${dayNum}</button>`;
    }
    html += `</div>`;
    body.innerHTML = html;

    body.querySelectorAll('.dp-day').forEach(cell => {
      cell.addEventListener('click', (e) => {
        e.stopPropagation();
        const d = parseInt(cell.dataset.day, 10);
        selected = { y: viewDate.y, m: viewDate.m, d };
        hiddenInput.value = toISO(viewDate.y, viewDate.m, d);
        renderTrigger();
        onChange(hiddenInput.value);
        closePanel();
      });
    });
  }

  function renderMonths(){
    label.textContent = `${viewDate.y}`;
    let html = `<div class="dp-months-grid">`;
    MONTHS.forEach((name, idx) => {
      const isSelected = selected && selected.y === viewDate.y && selected.m === idx;
      html += `<button type="button" class="dp-cell dp-month ${isSelected ? 'selected' : ''}" data-month="${idx}">${name.slice(0, 3)}</button>`;
    });
    html += `</div>`;
    body.innerHTML = html;

    body.querySelectorAll('.dp-month').forEach(cell => {
      cell.addEventListener('click', (e) => {
        e.stopPropagation();
        viewDate = { y: viewDate.y, m: parseInt(cell.dataset.month, 10) };
        view = 'days';
        renderView();
      });
    });
  }

  function renderYears(){
    label.textContent = `${yearRangeStart} – ${yearRangeStart + 24}`;
    let html = `<div class="dp-years-grid">`;
    for(let i = 0; i < 25; i++){
      const y = yearRangeStart + i;
      const isSelected = selected && selected.y === y;
      html += `<button type="button" class="dp-cell dp-year ${isSelected ? 'selected' : ''}" data-year="${y}">${y}</button>`;
    }
    html += `</div>`;
    body.innerHTML = html;

    body.querySelectorAll('.dp-year').forEach(cell => {
      cell.addEventListener('click', (e) => {
        e.stopPropagation();
        viewDate = { y: parseInt(cell.dataset.year, 10), m: viewDate.m };
        view = 'months';
        renderView();
      });
    });
  }

  renderTrigger();

  return {
    getValue: () => hiddenInput.value || null,
    setValue: (iso) => {
      selected = iso ? parseISO(iso) : null;
      if(selected) viewDate = { y: selected.y, m: selected.m };
      hiddenInput.value = iso || '';
      renderTrigger();
    }
  };
}