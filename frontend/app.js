const BACKEND_BASE = localStorage.getItem('aqi_backend') || 'http://127.0.0.1:8080';

function categoryClass(cat) {
  const c = (cat || '').toLowerCase();
  if (c === 'good') return 'good';
  if (c === 'moderate') return 'moderate';
  if (c === 'poor') return 'poor';
  if (c === 'unhealthy') return 'unhealthy';
  if (c === 'very unhealthy') return 'very-unhealthy';
  return 'hazardous';
}

function renderResult(container, data) {
  if (!data) {
    container.innerHTML = '<p class="muted">No data.</p>';
    return;
  }
  const cat = data.aqi_reg_category || data.aqi_classification_label;
  const badgeClass = categoryClass(cat);
  const advisory = data.advisory || '';
  const rows = [
    `<div><span class="badge ${badgeClass}">${cat}</span> AQI: <b>${data.aqi_regression}</b></div>`,
    data.features ? `<div class="muted">Features used: ${JSON.stringify(data.features)}</div>` : '',
    advisory ? `<div style="margin-top:6px">${advisory}</div>` : ''
  ].filter(Boolean).join('');
  container.innerHTML = rows;
}

document.getElementById('openaq-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const city = document.getElementById('city').value.trim();
  const country = document.getElementById('country').value.trim() || 'IN';
  const lookback = Number(document.getElementById('lookback').value) || 6;
  const out = document.getElementById('openaq-result');
  out.textContent = 'Loading...';
  try {
    const url = new URL('/predict_by_openaq', BACKEND_BASE);
    url.searchParams.set('city', city);
    url.searchParams.set('country', country);
    url.searchParams.set('lookback_hours', String(lookback));
    const resp = await fetch(url.toString());
    if (!resp.ok) throw new Error(`${resp.status} ${await resp.text()}`);
    const data = await resp.json();
    renderResult(out, data);
  } catch (err) {
    out.innerHTML = `<span style="color:#ff8080">Error: ${err}</span>`;
  }
});

document.getElementById('manual-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const si = Number(document.getElementById('si').value || 0);
  const ni = Number(document.getElementById('ni').value || 0);
  const rpi = Number(document.getElementById('rpi').value || 0);
  const out = document.getElementById('manual-result');
  out.textContent = 'Loading...';
  try {
    const resp = await fetch(`${BACKEND_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features: { si, ni, rpi } })
    });
    if (!resp.ok) throw new Error(`${resp.status} ${await resp.text()}`);
    const data = await resp.json();
    data.features = { si, ni, rpi };
    renderResult(out, data);
  } catch (err) {
    out.innerHTML = `<span style="color:#ff8080">Error: ${err}</span>`;
  }
});


