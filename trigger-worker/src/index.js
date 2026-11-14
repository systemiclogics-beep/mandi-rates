export default {
  // Automated Cloudflare Cron: Fires internally at 11:15 AM, 2:05 PM, 3:45 PM IST
  async scheduled(controller, env, ctx) {
    const owner = env.GH_OWNER || 'systemiclogics-beep';
    const repo = env.GH_REPO || 'mandi-rates';
    const workflow = env.GH_WORKFLOW || 'daily_mandi_sync.yml';

    const url = `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GH_PAT}`,
          'User-Agent': 'bharatmandi-cron-trigger',
          'Accept': 'application/vnd.github+json',
        },
        body: JSON.stringify({ ref: 'main' }),
      });

      if (response.status === 204) {
        console.log(`[SUCCESS] Cron successfully dispatched ${workflow} for ${owner}/${repo}`);
      } else {
        const errorText = await response.text();
        console.error(`[ERROR] Failed to dispatch workflow. Status: ${response.status}. Body: ${errorText}`);
      }
    } catch (err) {
      console.error(`[EXCEPTION] Network error during cron dispatch: ${err.message}`);
    }
  },

  // Anonymous Telemetry & Live Farmer Demographics Dashboard
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Universal CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // 1. Silent Anonymous Ping Endpoint: /ping?state=Maharashtra&district=Nashik&crop=Onion&lang=mr
    if (url.pathname === '/ping') {
      const sanitize = (val, maxLen = 40) => {
        if (!val) return '';
        return String(val).replace(/[^a-zA-Z0-9_\s\u0900-\u0D7F-]/g, '').trim().slice(0, maxLen);
      };

      const state = sanitize(url.searchParams.get('state')) || 'Unknown';
      const district = sanitize(url.searchParams.get('district')) || 'General';
      const crop = sanitize(url.searchParams.get('crop')) || 'General';
      const lang = sanitize(url.searchParams.get('lang'), 10) || 'hi';

      const today = new Date().toISOString().slice(0, 10);

      // Log structured JSON for Cloudflare Logpush / Analytics
      console.log(JSON.stringify({
        event: 'farmer_ping',
        date: today,
        state,
        district,
        crop,
        lang,
      }));

      // Store in Cloudflare KV if bound
      if (env.STATS_KV) {
        try {
          const ttl = 86400 * 30; // 30-day retention
          const stateKey = `st:${today}:${state}`;
          const districtKey = `dist:${today}:${state}:${district}`;
          const cropKey = `crop:${today}:${crop}`;
          const totalKey = `total:${today}`;

          const increment = async (key) => {
            const current = await env.STATS_KV.get(key);
            const nextVal = (parseInt(current || '0', 10) + 1).toString();
            await env.STATS_KV.put(key, nextVal, { expirationTtl: ttl });
          };

          await Promise.all([
            increment(stateKey),
            increment(districtKey),
            increment(cropKey),
            increment(totalKey),
          ]);
        } catch (err) {
          console.error('[KV Error]:', err);
        }
      }

      return new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // 2. Private Admin Live Analytics Dashboard: /stats?key=kisan2026
    if (url.pathname === '/stats') {
      const key = url.searchParams.get('key');
      const expectedKey = env.ADMIN_KEY || 'kisan2026';

      if (key !== expectedKey) {
        return new Response('Unauthorized. Please provide valid ?key=...', {
          status: 401,
          headers: { 'Content-Type': 'text/plain' },
        });
      }

      const today = new Date().toISOString().slice(0, 10);
      let totalFarmers = 0;
      const statesMap = {};
      const districtsMap = {};
      const cropsMap = {};

      if (env.STATS_KV) {
        try {
          const list = await env.STATS_KV.list({ prefix: '' });
          for (const item of list.keys) {
            const parts = item.name.split(':');
            const prefix = parts[0];
            const date = parts[1];
            if (date !== today) continue;

            const val = parseInt((await env.STATS_KV.get(item.name)) || '0', 10);
            if (prefix === 'total') {
              totalFarmers = val;
            } else if (prefix === 'st') {
              const st = parts.slice(2).join(':');
              statesMap[st] = (statesMap[st] || 0) + val;
            } else if (prefix === 'dist') {
              const d = parts.slice(2).join(' - ');
              districtsMap[d] = (districtsMap[d] || 0) + val;
            } else if (prefix === 'crop') {
              const c = parts.slice(2).join(':');
              cropsMap[c] = (cropsMap[c] || 0) + val;
            }
          }
        } catch (_) {}
      }

      const escapeHtml = (str) => String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

      const sortEntries = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1]);

      const formatTable = (entries) => {
        if (!entries || entries.length === 0) {
          return '<tr><td colspan="2" class="empty">No activity recorded yet today</td></tr>';
        }
        return entries.map(([name, count]) => `
          <tr>
            <td><strong>${escapeHtml(name)}</strong></td>
            <td class="count">${Number(count).toLocaleString()}</td>
          </tr>
        `).join('');
      };

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BharatMandi Live Analytics</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #F4F6F8; color: #1E293B; margin: 0; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    .header { background: #1B5E20; color: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .header h1 { margin: 0; font-size: 22px; }
    .header p { margin: 6px 0 0 0; opacity: 0.85; font-size: 13px; }
    .card { background: white; border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #E2E8F0; }
    .card h2 { margin: 0 0 12px 0; font-size: 16px; color: #0F172A; display: flex; align-items: center; justify-content: space-between; }
    .badge { background: #E8F5E9; color: #2E7D32; font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 6px; }
    table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #F1F5F9; }
    th { color: #64748B; font-weight: 600; font-size: 11px; text-transform: uppercase; }
    td.count { text-align: right; font-weight: 700; color: #1B5E20; font-variant-numeric: tabular-nums; }
    td.empty { text-align: center; color: #94A3B8; padding: 20px; }
    .footer { text-align: center; font-size: 12px; color: #94A3B8; margin-top: 24px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌾 BharatMandi — Live Farmer Analytics</h1>
      <p>Today's Real-Time Active Audience Breakdown (${escapeHtml(today)}) • Total Sessions: ${Number(totalFarmers).toLocaleString()} • 100% Anonymous & Legal</p>
    </div>

    <div class="card">
      <h2>Top States <span class="badge">State Coverage</span></h2>
      <table>
        <thead><tr><th>State</th><th style="text-align:right">Active Farmers</th></tr></thead>
        <tbody>${formatTable(sortEntries(statesMap))}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>Top Mandi Districts <span class="badge">Local Sponsor Hotspots</span></h2>
      <table>
        <thead><tr><th>District / Cluster</th><th style="text-align:right">Active Farmers</th></tr></thead>
        <tbody>${formatTable(sortEntries(districtsMap))}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>Top Crops in Demand <span class="badge">Buyer Intent</span></h2>
      <table>
        <thead><tr><th>Commodity</th><th style="text-align:right">Searches & Views</th></tr></thead>
        <tbody>${formatTable(sortEntries(cropsMap))}</tbody>
      </table>
    </div>

    <div class="footer">
      Private Sponsor Telemetry • Zero PII / Zero User IDs • Auto-refreshes daily
    </div>
  </div>
</body>
</html>`;

      return new Response(html, {
        status: 200,
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      });
    }

    return new Response('Not Found', { status: 404 });
  },
};
