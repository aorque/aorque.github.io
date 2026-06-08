import json
import re

# Live spend data
data = {
    "today_cost": 2.8815,
    "today_sessions": 16,
    "days": [
        {"date": "2026-06-02", "cost": 0.0753},
        {"date": "2026-06-03", "cost": 45.4227},
        {"date": "2026-06-04", "cost": 44.7528},
        {"date": "2026-06-05", "cost": 46.2749},
        {"date": "2026-06-06", "cost": 12.5992},
        {"date": "2026-06-07", "cost": 2.8814}
    ],
    "sessions_today": [
        {"time": "07:42", "cost": 0.0037},
        {"time": "07:30", "cost": 0.0314},
        {"time": "07:11", "cost": 0.1111},
        {"time": "07:00", "cost": 0.0066},
        {"time": "07:00", "cost": 0.0024},
        {"time": "06:40", "cost": 0.0676},
        {"time": "06:08", "cost": 0.1531},
        {"time": "05:38", "cost": 0.0544},
        {"time": "05:07", "cost": 0.0626},
        {"time": "05:01", "cost": 0.0175},
        {"time": "04:35", "cost": 0.1175},
        {"time": "04:04", "cost": 0.0845},
        {"time": "03:33", "cost": 0.0927},
        {"time": "03:00", "cost": 0.0244},
        {"time": "02:20", "cost": 0.5815},
        {"time": "02:10", "cost": 1.4705}
    ]
}

# Read HTML
with open('dashboard.html', 'r') as f:
    html = f.read()

# Update spend-big element (current spend)
html = re.sub(
    r'(var data = \{[^}]*"today":\s*\{[^}]*"cost":\s*)[\d.]+',
    f'\\1{data["today_cost"]}',
    html
)

# Update history in the hardcoded spend data
history_str = ', '.join([
    f"{{ day: '{d['date']}', cost: {d['cost']}, label: '{data['today_sessions']} sessions' if d['date'] == '2026-06-07' else f\"{d['date'][-2:]} jun\" }}"
    for d in data['days']
])

# Replace the spend data object
old_pattern = r'var data = \{[^}]*today:\s*\{[^}]*\},[^}]*history:\s*\[[^\]]*\]'
new_data = f"""var data = {{
      today: {{ cost: {data["today_cost"]}, sessions: {data["today_sessions"]}, tools: 79835 }},
      history: [
        {{ day: '2026-06-02', cost: 0.0753, label: '1 sessions' }}, {{ day: '2026-06-03', cost: 45.4227, label: '6 sessions' }}, {{ day: '2026-06-04', cost: 44.7528, label: '7 sessions' }}, {{ day: '2026-06-05', cost: 46.2749, label: '10 sessions' }}, {{ day: '2026-06-06', cost: 12.5992, label: '21 sessions' }}, {{ day: '2026-06-07', cost: {data['today_cost']}, label: '{data["today_sessions"]} sessions' }}
      ],
      max_scale: 12
    }}"""

html = re.sub(old_pattern, new_data, html, flags=re.DOTALL)

# Write updated HTML
with open('dashboard.html', 'w') as f:
    f.write(html)

print("Updated")
