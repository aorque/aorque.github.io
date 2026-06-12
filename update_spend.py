import json
import re

# New spend data
spend_data = {
    "generated_at": "2026-06-12T20:23:51.743080+00:00",
    "grand_total": 287.5865,
    "today_cost": 15.9264,
    "today_sessions": 180,
    "days": [
        {"date": "2026-06-02", "sessions": 1, "input": 6, "output": 125, "cache_read": 18064, "cost": 0.0753},
        {"date": "2026-06-03", "sessions": 6, "input": 1836, "output": 198763, "cache_read": 67116108, "cost": 45.4227},
        {"date": "2026-06-04", "sessions": 7, "input": 1395, "output": 240644, "cache_read": 48071197, "cost": 44.7528},
        {"date": "2026-06-05", "sessions": 10, "input": 17677, "output": 268456, "cache_read": 74855629, "cost": 46.2749},
        {"date": "2026-06-06", "sessions": 21, "input": 34526, "output": 113268, "cache_read": 20000286, "cost": 12.5992},
        {"date": "2026-06-07", "sessions": 64, "input": 204627, "output": 247172, "cache_read": 23062455, "cost": 6.6497},
        {"date": "2026-06-08", "sessions": 238, "input": 209922, "output": 521879, "cache_read": 51329582, "cost": 21.3507},
        {"date": "2026-06-09", "sessions": 324, "input": 193268, "output": 692836, "cache_read": 74634526, "cost": 28.8849},
        {"date": "2026-06-10", "sessions": 323, "input": 180061, "output": 631923, "cache_read": 85152502, "cost": 31.6838},
        {"date": "2026-06-11", "sessions": 331, "input": 194181, "output": 726115, "cache_read": 91031749, "cost": 33.9659},
        {"date": "2026-06-12", "sessions": 180, "input": 111134, "output": 327217, "cache_read": 43858572, "cost": 15.9266}
    ],
    "sessions_today": [
        {"time": "13:23", "title": "untitled", "input": 3184, "output": 117, "cost": 0.0038, "source": "cron"},
        {"time": "13:22", "title": "untitled", "input": 23, "output": 1584, "cost": 0.0941, "source": "cron"},
        {"time": "13:15", "title": "untitled", "input": 23, "output": 8233, "cost": 0.156, "source": "cron"}
    ]
}

# Read the current file
with open('dashboard.html', 'r') as f:
    content = f.read()

# Find and replace the _spend_data variable
spend_json = json.dumps(spend_data)
pattern = r'var _spend_data = \{.*?\};'
replacement = f'var _spend_data = {spend_json};'

content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also update the first renderSpend call data
first_spend_pattern = r'renderSpend\(\{[^}]*?"today_cost":[^}]*?\}\);'
# Keep just the necessary pattern simpler
content_new = content_new.replace(
    'var SPEND_DATA = {"generated_at"',
    f'var SPEND_DATA = {spend_json}'[:100] + '..."'
)

# Update the SPEND_DATA variable directly to avoid complex regex
pattern2 = r'var SPEND_DATA = \{[^}]*?"generated_at"[^;]*?\};'
# This is safer - replace the entire SPEND_DATA declaration
lines = content_new.split('\n')
new_lines = []
in_spend_var = False
skip_lines = 0

for i, line in enumerate(lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue
    
    if 'var SPEND_DATA = {' in line and '"generated_at"' in line:
        # Found start of SPEND_DATA, skip until we find the closing };
        j = i
        while j < len(lines) and '};' not in lines[j]:
            j += 1
        # Replace with new data
        new_lines.append(f'  var SPEND_DATA = {spend_json};')
        skip_lines = j - i
    else:
        new_lines.append(line)

content_new = '\n'.join(new_lines)

# Write back
with open('dashboard.html', 'w') as f:
    f.write(content_new)

print("Updated dashboard.html")
