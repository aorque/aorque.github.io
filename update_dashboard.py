import re

# Spend data
today_cost = 6.2552
today_sessions = 57
days = [
    ("2026-06-19", 56, 6.0084),
    ("2026-06-20", 54, 5.2685),
    ("2026-06-21", 57, 5.9053),
    ("2026-06-22", 55, 5.5127),
    ("2026-06-23", 55, 6.4389),
    ("2026-06-24", 57, 5.5362),
    ("2026-06-25", 57, 6.2552),
]

# Read HTML
with open('dashboard.html', 'r') as f:
    html = f.read()

# Build new history section
history_lines = []
for date, sessions, cost in days:
    line = f'<div style="padding:6px 0;font-size:10px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);"><span>{date} · {sessions} sessions</span><span style="color:var(--orange);font-weight:700;">${cost:.4f}</span></div>'
    history_lines.append(line)

history_html = '\n'.join(history_lines)

# Find the TODAY'S AGENDA section and replace all the hardcoded rows with our data
# This pattern matches from <!-- TODAY'S AGENDA --> to the </div> that closes the card
pattern = r'(<!-- TODAY\'S AGENDA -->\s*<div class="card orange">\s*<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid var\(--border\)">[^<]*<span>2026-06-09.*?)</div>\s*<script>'

replacement = f'''<!-- TODAY'S AGENDA -->
  <div class="card orange">
    <div class="ch"><div class="ci">💸</div><span class="ct">7-DAY HISTORY</span></div>
    {history_html}
  </div>

<script>'''

html = re.sub(pattern, replacement, html, flags=re.DOTALL)

# Write back
with open('dashboard.html', 'w') as f:
    f.write(html)

print("Updated dashboard successfully")
