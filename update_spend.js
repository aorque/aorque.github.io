// Extract from spend data and update HTML
const fs = require('fs');

const spendData = {
  "today_cost": 8.1168,
  "today_sessions": 88,
  "days": [
    {"date": "2026-06-02", "cost": 0.0753, "sessions": 1},
    {"date": "2026-06-03", "cost": 45.4227, "sessions": 6},
    {"date": "2026-06-04", "cost": 44.7528, "sessions": 7},
    {"date": "2026-06-05", "cost": 46.2749, "sessions": 10},
    {"date": "2026-06-06", "cost": 12.5992, "sessions": 21},
    {"date": "2026-06-07", "cost": 6.6497, "sessions": 64},
    {"date": "2026-06-08", "cost": 8.1168, "sessions": 88}
  ],
  "sessions_today": [
    {"time": "13:19", "input": 3184, "output": 97, "cost": 0.0037},
    {"time": "13:17", "input": 18, "output": 769, "cost": 0.1054}
  ]
};

let html = fs.readFileSync('dashboard.html', 'utf-8');

// Format today's cost
const formattedCost = '$' + spendData.today_cost.toFixed(2);
const sessionsCount = spendData.today_sessions;

// Update spend-big element
html = html.replace(/"spend-big"\).textContent = "[^"]*"/, 
  `"spend-big").textContent = "${formattedCost}"`);

// Generate 7-day history HTML
let historyHtml = '';
const maxCost = Math.max(...spendData.days.map(d => d.cost));
spendData.days.forEach(day => {
  const pct = Math.round((day.cost / maxCost) * 100);
  const dayStr = day.date.split('-').slice(1).join('-');
  const color = day.cost < 3 ? 'var(--green)' : day.cost < 6 ? 'var(--orange)' : '#ff4f6e';
  historyHtml += `<div style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;margin-bottom:3px"><span style="color:var(--ink)">2026-${dayStr} — ${day.sessions} sessions</span><span style="color:${color};font-weight:700">$${day.cost.toFixed(2)}</span></div><div style="background:var(--bg3);border-radius:2px;height:8px;overflow:hidden"><div style="width:${pct}%;height:100%;background:${color};border-radius:2px;transition:width 1s ease"></div></div></div>`;
});

// Update spend page data section with new history
html = html.replace(
  /hist\.innerHTML = `<div[^`]*`/s,
  `hist.innerHTML = \`${historyHtml}\``
);

// Update spend-big value in spend page JS section
html = html.replace(
  /if\(bigNum\) \{ bigNum\.textContent = "[^"]*";/,
  `if(bigNum) { bigNum.textContent = "${formattedCost}";`
);

// Update today sessions count
html = html.replace(
  /if\(s\) s\.textContent = '[^']*'/,
  `if(s) s.textContent = '${sessionsCount}'`
);

fs.writeFileSync('dashboard.html', html);
console.log('Dashboard updated with latest spend data');
