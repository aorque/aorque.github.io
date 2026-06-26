import json
import re

# Fetch current spend data
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
    html = f.read()

# Format spend big value
spend_big = f"${spend_data['today_cost']:.2f}"

# Update spend-big element
pattern = r'(<span class="sn" id="spend-big">)[^<]+(</span>)'
html = re.sub(pattern, rf'\1{spend_big}\2', html)

# If not found, try different pattern
if 'spend-big' not in html or spend_big not in html:
    # Insert it in the Quick Stats section
    pattern = r'(<div class="ct">Quick Stats</div>)'
    insert_html = rf'\1<div class="spend-info" style="margin-top:8px;padding:8px;background:var(--orange-glow);border-radius:6px;text-align:center"><span class="sn" id="spend-big">{spend_big}</span><div class="sl">TODAY SPEND</div></div>'
    html = re.sub(pattern, insert_html, html)

# Build spend history HTML
history_html = '\n'.join([
    f'<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);"><span>{day["date"]} · {day["sessions"]} sessions</span><span style="color:var(--orange);font-weight:700;">${day["cost"]:.4f}</span></div>'
    for day in spend_data['days_list']
])

# Find and replace the spend history section
# Look for the section with 7-DAY HISTORY or similar
pattern = r'<div id="spend-history">.*?</div>\s*(?=<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var\(--border\);")'
if re.search(pattern, html, re.DOTALL):
    replacement = f'<div id="spend-history">\n{history_html}\n</div>'
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
else:
    # Fallback: find the orange card and update it
    pattern = r'(<div class="card orange">\s*<div style="display:flex;[^<]*<[^>]*>2026-06-09.*?</div>)'
    if re.search(pattern, html, re.DOTALL):
        replacement = f'''<div class="card orange">
    <div class="ch"><div class="ci">💸</div><span class="ct">7-DAY HISTORY</span></div>
{history_html}
    </div>'''
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

# Update today's usage stats
# Update sessions count
pattern = r'(<span class="sn" id="spend-sessions">)[^<]+(</span>)'
html = re.sub(pattern, rf'\1{spend_data["today_sessions"]}\2', html)

# Write back
with open('dashboard.html', 'w') as f:
    f.write(html)

print("Updated dashboard.html")
