import json
import re

# Current spend data
spend_data = {
    "today_cost": 4.0774,
    "today_sessions": 38,
    "days": [
        {"date": "2026-06-15", "sessions": 55, "cost": 6.2791},
        {"date": "2026-06-16", "sessions": 54, "cost": 6.3015},
        {"date": "2026-06-17", "sessions": 55, "cost": 6.5147},
        {"date": "2026-06-18", "sessions": 56, "cost": 6.2003},
        {"date": "2026-06-19", "sessions": 56, "cost": 6.0084},
        {"date": "2026-06-20", "sessions": 54, "cost": 5.2685},
        {"date": "2026-06-21", "sessions": 38, "cost": 4.0774},
    ]
}

with open('dashboard.html', 'r') as f:
    content = f.read()

# Format today's cost as $X.XX
today_cost_str = f"${spend_data['today_cost']:.2f}"

# Update the spend-big element
content = re.sub(
    r'id="spend-big"[^>]*>[^<]*</[^>]*>',
    f'id="spend-big">{today_cost_str}</div>',
    content
)

# Update the spend history/7-day section
history_html = '\n'.join([
    f'    <div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);"><span>{day["date"]} · {day["sessions"]} sessions</span><span style="color:var(--orange);font-weight:700;">${day["cost"]:.4f}</span></div>'
    for day in spend_data['days']
])

# Replace the spend history section
content = re.sub(
    r'(id=["\']spend-history["\'][^>]*>)[\s\S]*?(</div>\s*`)',
    f'\\1\n{history_html}\n    `',
    content
)

# Update today's session count in the SPEND_DATA object
content = re.sub(
    r'"today_sessions":\s*\d+',
    f'"today_sessions": {spend_data["today_sessions"]}',
    content
)

# Update today_cost in SPEND_DATA
content = re.sub(
    r'"today_cost":\s*[\d.]+',
    f'"today_cost": {spend_data["today_cost"]}',
    content
)

# Update the 7-day days array in SPEND_DATA
days_json = json.dumps(spend_data['days'])
content = re.sub(
    r'"days":\s*\[\{[^]]+\}\]',
    f'"days": {days_json}',
    content
)

# Update tk-today element (today's spend)
content = re.sub(
    r'el\.textContent\s*=\s*["\']?\$[\d.]+["\']?',
    f'el.textContent = "{today_cost_str}"',
    content
)

with open('dashboard.html', 'w') as f:
    f.write(content)

print(f"Updated dashboard with: today_cost={today_cost_str}, today_sessions={spend_data['today_sessions']}")
