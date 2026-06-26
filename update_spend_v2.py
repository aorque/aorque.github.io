import json
import re

# Spend data from API
spend_data = {
    "today_cost": 6.2552,
    "today_sessions": 57,
    "days_list": [
        {"date": "2026-06-19", "sessions": 56, "cost": 6.0084},
        {"date": "2026-06-20", "sessions": 54, "cost": 5.2685},
        {"date": "2026-06-21", "sessions": 57, "cost": 5.9053},
        {"date": "2026-06-22", "sessions": 55, "cost": 5.5127},
        {"date": "2026-06-23", "sessions": 55, "cost": 6.4389},
        {"date": "2026-06-24", "sessions": 57, "cost": 5.5362},
        {"date": "2026-06-25", "sessions": 57, "cost": 6.2552},
    ]
}

# Read current HTML
with open('dashboard.html', 'r') as f:
    content = f.read()

# Build spend history HTML
history_html = '\n'.join([
    f'<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);"><span>{day["date"]} · {day["sessions"]} sessions</span><span style="color:var(--orange);font-weight:700;">${day["cost"]:.4f}</span></div>'
    for day in spend_data['days_list']
])

# Replace the messy spend history section with clean version
# Find the card with "2026-06-09" and replace the entire section
pattern = r'<!-- TODAY\'S AGENDA -->.*?<div id="spend-history">.*?</div>\s*<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var\(--border\);">[^<]*<span>2026-06-20[^<]*</span><span[^<]*\$5\.2685</span></div>.*?<div id="spend-history">[^<]*<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var\(--border\);">[^<]*<span>2026-06-25 · 53 sessions[^<]*</span><span style="color:var\(--orange\);font-weight:700;">.*?</span></div>\s*</div>'

replacement = f'''<!-- TODAY'S AGENDA -->
  <div class="card orange">
    <div class="ch"><div class="ci">💸</div><span class="ct">7-DAY HISTORY</span></div>
{history_html}
  </div>'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('dashboard.html', 'w') as f:
    f.write(content)

print("Updated dashboard.html with spend data")
