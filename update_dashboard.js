// Extract and format current spend data
const spendData = {
  "today_cost": 2.12,
  "today_sessions": 29,
  "days": [
    {"date": "2026-06-08", "sessions": 238, "cost": 21.3507},
    {"date": "2026-06-09", "sessions": 324, "cost": 28.8849},
    {"date": "2026-06-10", "sessions": 323, "cost": 31.6838},
    {"date": "2026-06-11", "sessions": 331, "cost": 33.9659},
    {"date": "2026-06-12", "sessions": 325, "cost": 29.7017},
    {"date": "2026-06-13", "sessions": 298, "cost": 25.5309},
    {"date": "2026-06-14", "sessions": 56, "cost": 5.9532},
    {"date": "2026-06-15", "sessions": 29, "cost": 2.1198}
  ],
  "sessions_today": [
    {"time": "11:42", "output": 96, "cost": 0.0037},
    {"time": "11:12", "output": 3203, "cost": 0.0484},
    {"time": "10:40", "output": 5632, "cost": 0.082},
    {"time": "10:09", "output": 7310, "cost": 0.1414},
    {"time": "09:38", "output": 2610, "cost": 0.0693},
    {"time": "09:33", "output": 682, "cost": 0.0104},
    {"time": "09:07", "output": 2452, "cost": 0.0709},
    {"time": "08:52", "output": 0, "cost": 0},
    {"time": "08:50", "output": 1279, "cost": 0.0504},
    {"time": "08:36", "output": 8739, "cost": 0.1297},
    {"time": "08:05", "output": 2755, "cost": 0.0869},
    {"time": "07:35", "output": 1854, "cost": 0.0604},
    {"time": "07:04", "output": 2711, "cost": 0.0794},
    {"time": "06:33", "output": 2459, "cost": 0.0659},
    {"time": "06:02", "output": 3465, "cost": 0.0833},
    {"time": "05:31", "output": 4843, "cost": 0.0828},
    {"time": "05:00", "output": 7488, "cost": 0.1863},
    {"time": "04:29", "output": 3443, "cost": 0.0545},
    {"time": "03:58", "output": 6626, "cost": 0.1065},
    {"time": "03:32", "output": 661, "cost": 0.0102},
    {"time": "03:27", "output": 2886, "cost": 0.0746},
    {"time": "03:00", "output": 2033, "cost": 0.0311},
    {"time": "02:55", "output": 3094, "cost": 0.0762},
    {"time": "02:24", "output": 4094, "cost": 0.0997},
    {"time": "01:53", "output": 7105, "cost": 0.0995},
    {"time": "01:22", "output": 2417, "cost": 0.0708},
    {"time": "01:01", "output": 6193, "cost": 0.0935},
    {"time": "00:51", "output": 2510, "cost": 0.0736},
    {"time": "00:20", "output": 2392, "cost": 0.0786}
  ]
};

// Format spend big value
const spendBig = "$" + spendData.today_cost.toFixed(2);

// Format 7-day history
let historyHtml = spendData.days.map(d => 
  `<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);"><span>${d.date} · ${d.sessions} sessions</span><span style="color:var(--orange);font-weight:700">$${d.cost.toFixed(4)}</span></div>`
).join('');

// Format today's sessions
let sessionsHtml = spendData.sessions_today.reverse().map(s => 
  `<div style="padding:6px 0;font-size:9px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(0,180,216,.08);"><span>${s.time}</span><span style="display:flex;gap:8px;align-items:center;"><span>↓ ${s.output}</span><span style="color:var(--orange);font-weight:700;min-width:50px;text-align:right">$${s.cost.toFixed(4)}</span></span></div>`
).join('');

console.log(JSON.stringify({
  spend_big: spendBig,
  history: historyHtml,
  sessions: sessionsHtml,
  today_sessions: spendData.today_sessions,
  today_cost: spendData.today_cost
}));
