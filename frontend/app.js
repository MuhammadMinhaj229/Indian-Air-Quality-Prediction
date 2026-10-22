let BACKEND_BASE = localStorage.getItem('aqi_backend') || 'https://aqi-backend-v5ay.onrender.com';

function categoryBadge(cat) {
  const c = (cat || '').toLowerCase().replace(' ', '-');
  return `<span class="badge badge-${c}">${cat}</span>`;
}

function renderTelemetry(container, data) {
  if (!data) {
    container.style.display = 'block';
    container.innerHTML = '<p style="color:#8b9bb4">No telemetry received.</p>';
    return;
  }

  const aqi = data.aqi_regression || 0;
  const category = data.aqi_reg_category || data.aqi_classification_label || 'Moderate';
  const advisory = data.advisory || '';
  const hvac = data.hvac_throttling_policy || {};
  const source = data.telemetry_source || 'Manual Feature Ingestion';
  const feats = data.features || {};

  container.style.display = 'block';
  container.innerHTML = `
    <div style="font-size:12px; color:#8b9bb4; margin-bottom:12px;">
      Data Ingestion Source: <b style="color:#38bdf8">${source}</b>
    </div>

    <div class="telemetry-display">
      <div class="kpi-tile">
        <div class="kpi-tile-title">Calculated National AQI</div>
        <div class="kpi-tile-value">${aqi}</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-title">CPCB Category</div>
        <div style="margin-top:4px">${categoryBadge(category)}</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-title">Damper Intake Setting</div>
        <div class="kpi-tile-value" style="color:#38bdf8">${hvac.damper_intake_percent || 100}%</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-tile-title">Air Filtration Mode</div>
        <div class="kpi-tile-value" style="font-size:18px; color:#2ea043">${hvac.hepa_filtration || 'STANDARD'}</div>
      </div>
    </div>

    <div style="background:#131b2e; padding:12px 16px; border-radius:8px; font-size:13px; margin-bottom:12px; border:1px solid #1f2b45">
      <b style="color:#ffffff">Public Health Directive:</b>
      <p style="color:#cbd5e1; margin-top:4px">${advisory}</p>
    </div>

    <div class="hvac-card">
      <div class="hvac-title">Smart Building Automation Directive (${hvac.mode || 'ACTIVE'})</div>
      <div>${hvac.action || 'Operate standard outdoor air damper settings.'}</div>
    </div>

    <div style="font-size:11px; color:#64748b; margin-top:10px;">
      Sub-indices used: SO2 (si): ${feats.si || 0} | NO2 (ni): ${feats.ni || 0} | PM10 (rpi): ${feats.rpi || 0}
    </div>
  `;
}

// OpenAQ Query
document.getElementById('openaq-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const city = document.getElementById('city').value.trim();
  const country = document.getElementById('country').value.trim() || 'IN';
  const lookback = Number(document.getElementById('lookback').value) || 6;
  const out = document.getElementById('openaq-result');

  out.style.display = 'block';
  out.innerHTML = '<span style="color:#38bdf8">Connecting to telemetry network and calculating NAQI...</span>';

  try {
    const url = new URL('/predict_by_openaq', BACKEND_BASE);
    url.searchParams.set('city', city);
    url.searchParams.set('country', country);
    url.searchParams.set('lookback_hours', String(lookback));
    const resp = await fetch(url.toString());
    if (!resp.ok) throw new Error(`${resp.status} ${await resp.text()}`);
    const data = await resp.json();
    renderTelemetry(out, data);
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149">Telemetry Query Notice: ${err.message}. Verify backend URL or choose another station.</span>`;
  }
});

// Manual Form Query
document.getElementById('manual-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const si = Number(document.getElementById('si').value || 0);
  const ni = Number(document.getElementById('ni').value || 0);
  const rpi = Number(document.getElementById('rpi').value || 0);
  const out = document.getElementById('manual-result');

  out.style.display = 'block';
  out.innerHTML = '<span style="color:#38bdf8">Inferencing Random Forest Regressor & Classifier...</span>';

  try {
    const resp = await fetch(`${BACKEND_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features: { si, ni, rpi } })
    });
    if (!resp.ok) throw new Error(`${resp.status} ${await resp.text()}`);
    const data = await resp.json();
    data.features = { si, ni, rpi };
    renderTelemetry(out, data);
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149">Prediction Error: ${err.message}. Ensure backend is reachable.</span>`;
  }
});

// Metro Station Chips Click
document.querySelectorAll('.metro-chips .chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.metro-chips .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    const cityName = chip.getAttribute('data-city');
    document.getElementById('city').value = cityName;
    // Trigger submit
    document.getElementById('openaq-form').dispatchEvent(new Event('submit'));
  });
});

// Backend URL configuration
const backendInput = document.getElementById('backend-url');
backendInput.value = localStorage.getItem('aqi_backend') || 'https://aqi-backend-v5ay.onrender.com';

document.getElementById('save-backend').addEventListener('click', () => {
  let val = backendInput.value.trim();
  if (val) {
    if (!val.startsWith('http://') && !val.startsWith('https://')) {
      val = 'https://' + val;
    }
    localStorage.setItem('aqi_backend', val);
    BACKEND_BASE = val;
    alert('Backend updated to: ' + val);
    window.location.reload();
  }
});
