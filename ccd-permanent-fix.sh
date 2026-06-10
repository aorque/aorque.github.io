#!/bin/bash
# ccd-permanent-fix.sh — paste into the Hostinger/VPS terminal ONCE.
#
# New architecture: the VPS is the source of truth.
#   * Dashboard lives at /opt/data/www/aorque.github.io/dashboard.html
#   * Nginx serves it directly:  http://<vps-ip>/dashboard.html  (instant updates)
#   * GitHub Pages stays alive as a mirror (best-effort push; failure can't break the site)
#
# What it does:
#   1. Moves the repo out of /tmp (wiped on reboot!) to /opt/data/www
#   2. Repairs dashboard.html in place (dedupes 7-day history, rebuilds the
#      mangled Today's Usage card, rescues stray JS back inside <script> tags)
#   3. Installs a marker-based updater that can never nest, duplicate, or eat HTML
#   4. Validation guard: structurally broken HTML is never written or pushed
#   5. Installs + configures nginx to serve the dashboard
#   6. Swaps the cron, disables the old mangler, runs everything once
#
# After this, Unit 0 must never edit dashboard.html directly again.

set -e
REPO="/opt/data/www/aorque.github.io"
DASH="$REPO/dashboard.html"
SCRIPTS="/opt/data/scripts"
LOGS="/opt/data/logs"
mkdir -p "$SCRIPTS" "$LOGS" /opt/data/backups /opt/data/www

echo "=== CCD PERMANENT FIX (VPS-hosted) ==="

# ── 0a. STOP THE BLEEDING: kill all old dashboard crons FIRST ─────
(crontab -l 2>/dev/null | grep -v -e update_dashboard -e ccd_update -e dashboard) | crontab - || true
echo "[0a] Old dashboard crons removed."

# ── 0b. Move repo out of /tmp, sync to origin ─────────────────────
if [ ! -d "$REPO/.git" ]; then
  if [ -d /tmp/aorque.github.io/.git ]; then
    mv /tmp/aorque.github.io "$REPO"
  else
    git clone https://github.com/aorque/aorque.github.io.git "$REPO"
  fi
fi
cd "$REPO"
git fetch origin && git reset --hard origin/main
cp "$DASH" "/opt/data/backups/dashboard.pre-fix.$(date +%s).html"
echo "[0b] Repo at $REPO, backup saved."

# ── 0c. Restore last structurally-valid version from git history ──
echo "[0c] Searching git history for last good dashboard.html..."
FOUND=""
for C in $(git rev-list -n 200 origin/main -- dashboard.html); do
  git show "$C:dashboard.html" > /tmp/ccd_candidate.html 2>/dev/null || continue
  if python3 - << 'CHECK'
import sys
h = open('/tmp/ccd_candidate.html', encoding='utf-8').read()
ok = (h.count('<script') == h.count('</script>')
      and h.count('<div') == h.count('</div>')
      and h.rstrip().endswith('</html>')
      and '<!-- SESSION STATS -->' in h
      and '<!-- 7-DAY HISTORY -->' in h
      and len(h) > 50_000)
sys.exit(0 if ok else 1)
CHECK
  then FOUND="$C"; break; fi
done
if [ -z "$FOUND" ]; then
  echo "FATAL: no structurally valid dashboard.html found in last 200 commits."
  echo "Nothing was changed. Send this output to Cowork."
  exit 1
fi
cp /tmp/ccd_candidate.html "$DASH"
echo "[0c] Restored from commit $FOUND ($(git log -1 --format='%ci %s' $FOUND))"

# ── 1. One-time structural repair ─────────────────────────────────
DASH="$DASH" python3 << 'REPAIR'
import re, sys, os

DASH = os.environ["DASH"]
html = open(DASH, encoding="utf-8").read()
orig_len = len(html)

# --- 1a. Rebuild SESSION STATS card with sentinel markers ---
session_stats = '''<!-- SESSION STATS -->
  <div class="card teal">
    <div class="ch"><div class="ci">\U0001F4CA</div><span class="ct">Today's Usage</span></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border:1px solid var(--border)">
      <div style="background:var(--bg2);padding:14px;text-align:center">
        <div style="font-size:24px;font-weight:700;color:var(--teal)"><!--CCD:SESSIONS-->0<!--/CCD:SESSIONS--></div>
        <div style="font-size:8px;color:var(--muted)">SESSIONS</div>
      </div>
      <div style="background:var(--bg2);padding:14px;text-align:center">
        <div style="font-size:24px;font-weight:700;color:var(--orange)"><!--CCD:TOOLCALLS-->0<!--/CCD:TOOLCALLS--></div>
        <div style="font-size:8px;color:var(--muted)">TOOL CALLS</div>
      </div>
      <div style="background:var(--bg2);padding:14px;text-align:center">
        <div style="font-size:24px;font-weight:700;color:var(--green)" id="spend-saved"><!--CCD:SAVED-->$0.00<!--/CCD:SAVED--></div>
        <div style="font-size:8px;color:var(--muted)">EST. SAVED</div>
      </div>
    </div>
  </div>

  '''

pat = re.compile(r'<!-- SESSION STATS -->.*?(?=<!-- 7-DAY HISTORY -->)', re.S)
if not pat.search(html):
    sys.exit("FATAL: SESSION STATS anchor not found — aborting, file untouched")
html = pat.sub(session_stats, html, count=1)

# --- 1b. Rebuild 7-DAY HISTORY card (kills all nested duplicates) ---
history_card = '''<!-- 7-DAY HISTORY -->
  <div class="card purple">
    <div class="ch"><div class="ci">\U0001F4C5</div><span class="ct">7-Day History</span><span class="cs">last 7 days</span></div>
    <div id="spend-history"><!--CCD:HISTORY--><div style="font-size:11px;color:var(--muted);padding:8px">loading…</div><!--/CCD:HISTORY--></div>
  </div>

  '''
pat = re.compile(r'<!-- 7-DAY HISTORY -->.*?(?=<!-- TEAMWIRE NOTE -->|<div id="page-kanban")', re.S)
if not pat.search(html):
    sys.exit("FATAL: could not find end boundary (TEAMWIRE NOTE / page-kanban) after 7-DAY HISTORY — aborting, file untouched")
html = pat.sub(history_card, html, count=1)

# --- 1c. Mark the big spend number with sentinels (anchored on its id) ---
html = re.sub(
    r'(id="spend-big"[^>]*>)[^<]*(</div>)',
    r'\g<1><!--CCD:SPEND-->$0.00<!--/CCD:SPEND-->\g<2>',
    html, count=1)

# --- 1d. Rescue stray JS rendered as page text ---
m = re.search(r'</html>\s*', html)
if m and m.end() < len(html):
    stray = html[m.end():].strip()
    html = html[:m.end()]
    if 'function' in stray or 'getElementById' in stray:
        stray = stray.replace('</script>', '').replace('<script>', '')
        html = html.replace('</body>', '<script>\n' + stray + '\n</script>\n</body>', 1) \
               if '</body>' in html else html[:html.rfind('</html>')] + '<script>\n' + stray + '\n</script>\n</html>'

# Balance script tags (an opening or closing tag was destroyed somewhere)
opens, closes = html.count('<script'), html.count('</script>')
if opens > closes:
    html = html.replace('</html>', '</script>\n</html>', 1)
elif closes > opens:
    depth = 0
    for mm in re.finditer(r'<script\b|</script>', html):
        if mm.group(0).startswith('<script'):
            depth += 1
        else:
            if depth == 0:
                start = html.rfind('>', 0, mm.start()) + 1
                html = html[:start] + '\n<script>\n' + html[start:]
                break
            depth -= 1

# Final sanity: every check must pass or we abort and leave the file untouched
assert html.count('<script') == html.count('</script>'), "script tags unbalanced after repair"
assert html.count('<div') == html.count('</div>'), \
    f"div mismatch: {html.count('<div')} open vs {html.count('</div>')} close"
assert html.rstrip().endswith('</html>'), "file does not end with </html>"

open(DASH, 'w', encoding='utf-8').write(html)
print(f"[1] Repair done. {orig_len} -> {len(html)} bytes. Structure validated.")
REPAIR

# ── 2. Install the marker-based updater (writes locally, mirrors to GitHub) ──
cat > "$SCRIPTS/ccd_update.py" << 'UPDATER'
#!/usr/bin/env python3
"""CCD updater — the ONLY thing allowed to write dashboard.html.

  * Writes ONLY between <!--CCD:X--> ... <!--/CCD:X--> sentinel pairs.
  * Wholesale-replaces marker content every run -> idempotent, no accumulation.
  * Validates structure before saving. On failure: nothing written, error logged.
  * VPS file (served by nginx) is the source of truth; GitHub Pages push is a
    best-effort mirror — its failure never affects the live site.
"""
import json, re, subprocess, sys, urllib.request, datetime

REPO = "/opt/data/www/aorque.github.io"
DASH = f"{REPO}/dashboard.html"
API  = "http://127.0.0.1:7842"

def log(msg):
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {msg}")

def get(path):
    try:
        with urllib.request.urlopen(f"{API}{path}", timeout=10) as r:
            return json.load(r)
    except Exception as e:
        log(f"API {path} failed: {e}")
        return None

def set_marker(html, name, value):
    pat = re.compile(f"(<!--CCD:{name}-->).*?(<!--/CCD:{name}-->)", re.S)
    if not pat.search(html):
        log(f"marker {name} missing — skipped")
        return html
    return pat.sub(lambda m: m.group(1) + value + m.group(2), html, count=1)

def num(d, *keys, default=0):
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def history_rows(days):
    """days: list of {date, sessions, cost} — newest last, max 7."""
    rows = []
    mx = max((float(d.get("cost", 0)) for d in days), default=1) or 1
    for d in days[-7:]:
        cost = float(d.get("cost", 0))
        col = "var(--green)" if cost < 7 else "#ff4f6e"
        w = min(100.0, cost / mx * 100)
        rows.append(
            f'<div style="margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
            f'<span style="color:var(--muted)">{d.get("date","?")} — {d.get("sessions","?")} sessions</span>'
            f'<span style="color:{col};font-weight:700">${cost:.2f}</span></div>'
            f'<div style="background:var(--bg3);border-radius:2px;height:8px;overflow:hidden">'
            f'<div style="width:{w:.1f}%;height:100%;background:{col};border-radius:2px"></div></div></div>')
    return "".join(rows)

def validate(html):
    return all([
        html.count("<script") == html.count("</script>"),
        html.count("<div") == html.count("</div>"),
        html.rstrip().endswith("</html>"),
        50_000 < len(html) < 250_000,
        html.count("<!--CCD:HISTORY-->") == 1,
    ])

def mirror_to_github(msg):
    """Best-effort. Never raises."""
    def g(*args):
        return subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    if g("diff", "--quiet", "dashboard.html").returncode == 0:
        return
    g("pull", "--rebase", "--quiet")
    g("add", "dashboard.html")
    g("commit", "-q", "-m", msg)
    p = g("push", "--quiet")
    log("mirror pushed" if p.returncode == 0 else
        f"mirror push failed (site still live on VPS): {p.stderr.decode()[:200]}")

def main():
    html = open(DASH, encoding="utf-8").read()
    before = html

    spend = get("/spend") or {}
    today_cost = float(num(spend, "total_cost_usd", "today_cost", "cost", "total"))
    html = set_marker(html, "SPEND", f"${today_cost:.2f}")
    html = set_marker(html, "SESSIONS", str(num(spend, "sessions", "session_count", default="—")))
    html = set_marker(html, "TOOLCALLS", str(num(spend, "tool_calls", "toolcalls", default="—")))
    saved = num(spend, "saved", "est_saved", default=None)
    if saved is not None:
        html = set_marker(html, "SAVED", f"${float(saved):.2f}")

    hist = get("/spend/history") or get("/history")
    if isinstance(hist, dict):
        hist = hist.get("days") or hist.get("history")
    if isinstance(hist, list) and hist:
        html = set_marker(html, "HISTORY", history_rows(hist))

    if html == before:
        log("no changes")
        return
    if not validate(html):
        log("VALIDATION FAILED — file NOT written, NOT pushed")
        sys.exit(1)

    open(DASH, "w", encoding="utf-8").write(html)  # nginx serves this instantly
    log(f"updated: ${today_cost:.2f}")
    mirror_to_github(f"ccd update ${today_cost:.2f} [{datetime.datetime.now():%H:%M}]")

if __name__ == "__main__":
    main()
UPDATER
chmod +x "$SCRIPTS/ccd_update.py"
echo "[2] Updater installed: $SCRIPTS/ccd_update.py"

# ── 3. Nginx: serve the dashboard straight off the VPS ────────────
if ! command -v nginx >/dev/null 2>&1; then
  apt-get update -qq && apt-get install -y -qq nginx
fi
cat > /etc/nginx/conf.d/ccd.conf << 'NGINX'
server {
    listen 80 default_server;
    server_name _;
    root /opt/data/www/aorque.github.io;
    index dashboard.html;
    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache";
    }
}
NGINX
# disable distro default site if it grabs port 80
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t && (systemctl reload nginx 2>/dev/null || systemctl restart nginx)
echo "[3] Nginx live. Dashboard: http://$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')/dashboard.html"

# ── 4. Swap cron: remove ALL old dashboard crons, add the safe one ─
(crontab -l 2>/dev/null | grep -v -e update_dashboard -e ccd_update; \
 echo "*/15 * * * * /usr/bin/python3 $SCRIPTS/ccd_update.py >> $LOGS/ccd_update.log 2>&1") | crontab -
echo "[4] Cron swapped (every 15 min). Old dashboard crons removed."

# ── 5. Disable the old mangler so nothing can ever run it again ───
[ -f "$SCRIPTS/update_dashboard.sh" ] && mv "$SCRIPTS/update_dashboard.sh" "$SCRIPTS/update_dashboard.sh.DISABLED"

# ── 6. Push repaired file to the GitHub mirror, run updater once ──
cd "$REPO"
git add dashboard.html
git commit -q -m "CCD permanent fix: repair structure, sentinel markers, VPS-hosted + safe updater" || true
git push --quiet && echo "[6] Repaired dashboard mirrored to GitHub Pages." || echo "[6] GitHub push failed (VPS site unaffected)"
python3 "$SCRIPTS/ccd_update.py" || true

echo ""
echo "=== DONE ==="
echo "Live (instant):  http://<your-vps-ip>/dashboard.html"
echo "Mirror (~1 min): https://aorque.github.io/dashboard.html"
echo "Log:             tail -f $LOGS/ccd_update.log"
