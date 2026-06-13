# PORTFOLIO_CANON — index.html is locked

**For:** Unit 0 (Hermes), AutoBot, ccd_update.py, and any agent with push access to `aorque/aorque.github.io`.
**Status:** ACTIVE rule as of June 13, 2026. Owned by Tony + Cowork.

---

## The one rule

`index.html` is **canonical and frozen**. Do **NOT** regenerate, restyle, theme-swap, "redesign," or revert it.

The live version is the **Portfolio Rebuild (violet/amber)** design — dark base `#0C0A14`, violet `#9A6CE6`, amber `#E58E45`. It is intentional, signed off, and deployed. First deploy: commit `db69132`, June 13 2026.

If you think `index.html` "looks broken," "is the wrong theme," or "needs the Unit 0 brand colors" — **you are wrong. Leave it alone.** The teal/blue light-theme version and all "Revert to Unit 0 colors" commits are retired.

---

## What you MAY touch

- **`dashboard.html` only** — and only between the `<!--CCD:X-->` / `<!--/CCD:X-->` sentinel markers, via `ccd_update.py`. That flow is correct and stays as-is.
- Nothing else in the repo gets auto-edited.

If your job is spend-data / dashboard updates: you already `git pull --rebase` before pushing, so you pick up `index.html` automatically and never conflict with it. Keep doing exactly that. No change needed on your side.

---

## Source of truth

The editable master lives **outside** the repo:

```
Career Type Shit/Portfolio Rebuild/index.html
```

Any real change to the portfolio happens **there first**, then gets re-uploaded to the repo. Do not hand-edit `index.html` on the VPS or in GitHub.

Self-hosted assets that must not be deleted:
- `headshot.jpg` (repo root, 2494×1813 event portrait) — the hero `<img>` and `og:image` both point here.

---

## If index.html gets clobbered (recovery)

1. Restore from `Career Type Shit/Portfolio Rebuild/index.html`, **or**
2. `git checkout db69132 -- index.html` (or any later Cowork "Portfolio …" commit), then push.

A canonical-marker comment lives at the top of `index.html` (`<head>`). If you're an agent reading the file and you see that banner, stop — the file is off-limits.

---

## Why this exists

On June 13 2026 the repo showed churn — a teal "Complete redesign," then "Revert to v1 light theme," "Restore original Unit 0 colors," "Revert to original Unit 0 brand colors" — agents fighting over `index.html`. This file ends that. One owner (Tony + Cowork), one canonical file, one source of truth. Dashboard automation runs untouched alongside it.
