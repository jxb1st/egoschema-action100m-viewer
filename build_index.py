#!/usr/bin/env python3
"""Generate the dark-themed index.html (panel page) for the viewer site.

Mimics the visual language of https://jxb1st.github.io/datasets/ but the cards
are individual EgoSchema clips instead of separate datasets.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent
PROJ = Path("/gpfs/projects/embodied3d/jianxu/vlm_pruning/streaming_benchmark")
STAGE3 = PROJ / "outputs" / "stage3_annotations"

clip_ids = sorted([p.stem for p in STAGE3.glob("*.json")])

cards = []
total_nodes = 0
total_annotated = 0
all_costs = []   # per-clip cost field is actually a CUMULATIVE snapshot
                 # (CostTracker is shared across clips in --all mode), so the
                 # true total is max(values), not sum.
total_duration = 0.0
for cid in clip_ids:
    d = json.loads((STAGE3 / f"{cid}.json").read_text())
    n_total = len(d["tree"])
    n_ann = sum(1 for n in d["tree"] if n.get("annotation"))
    root = next(n for n in d["tree"] if n["parent_id"] is None)
    summary_brief = ""
    action_brief = ""
    if root.get("annotation"):
        summary_brief = root["annotation"].get("summary", {}).get("brief", "")
        action_brief = root["annotation"].get("action", {}).get("brief", "")
    duration = float(d["video_duration_sec"])
    all_costs.append(d.get("metadata", {}).get("stage3_total_api_cost_usd", 0.0))
    total_nodes += n_total
    total_annotated += n_ann
    total_duration += duration
    cards.append({
        "q_uid": cid,
        "short": cid[:8],
        "duration": duration,
        "n_total": n_total,
        "n_ann": n_ann,
        "summary_brief": summary_brief,
        "action_brief": action_brief,
    })

total_cost = max(all_costs) if all_costs else 0.0


def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def card_html(c: dict) -> str:
    summary = html_escape(c["summary_brief"]) or "<em style='color:var(--muted)'>(no annotation)</em>"
    action = html_escape(c["action_brief"]) or ""
    return f"""    <a class="card" href="viewers/{c['q_uid']}.html">
      <div class="card-head">
        <span class="card-icon">{html_escape(c['short'][:4]).upper()}</span>
        <h2 title="{c['q_uid']}">{c['short']}…</h2>
      </div>
      <p>{summary}</p>
      <div class="card-stats">
        <span><strong>{c['duration']:.0f}s</strong></span>
        <span><strong>{c['n_total']}</strong> nodes</span>
        <span><strong>{c['n_ann']}</strong> annotated</span>
      </div>
      <div class="card-tags">
        <span class="tag">action: {action}</span>
      </div>
      <span class="card-cta">Open viewer</span>
    </a>"""


cards_html = "\n".join(card_html(c) for c in cards)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EgoSchema × Action100M Viewer</title>
<style>
:root {{
  --bg: #0f1419;
  --panel: #1a2129;
  --border: #2d3640;
  --text: #e6e9ed;
  --muted: #8a949e;
  --accent: #4dabf7;
  --good: #51cf66;
  --purple: #b197fc;
  --highlight: #ffd43b;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}}
.wrap {{ max-width: 1200px; margin: 0 auto; padding: 48px 24px 80px; }}
header {{ margin-bottom: 36px; }}
.home-link {{
  display: inline-block;
  font-size: 13px;
  color: var(--muted);
  text-decoration: none;
  margin-bottom: 20px;
}}
.home-link:hover {{ color: var(--accent); }}
h1 {{
  margin: 0 0 10px;
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.3px;
}}
.tagline {{
  margin: 0 0 24px;
  color: var(--muted);
  font-size: 15px;
  max-width: 800px;
}}
.summary-stats {{
  display: flex; gap: 24px; flex-wrap: wrap;
  padding: 16px 20px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
}}
.summary-stats div {{ color: var(--muted); }}
.summary-stats strong {{ color: var(--text); font-size: 17px; font-weight: 700; display: block; margin-bottom: 2px; }}
.search {{
  margin: 28px 0 18px;
}}
.search input {{
  width: 100%;
  padding: 10px 14px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
}}
.search input:focus {{ border-color: var(--accent); }}
.aggregate-card {{
  display: block;
  background: linear-gradient(135deg, rgba(177,151,252,0.08), rgba(77,171,247,0.08));
  border: 1px solid rgba(177,151,252,0.3);
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 24px;
  text-decoration: none;
  color: var(--text);
  transition: border-color 0.12s, transform 0.12s;
}}
.aggregate-card:hover {{ border-color: var(--purple); transform: translateY(-1px); }}
.aggregate-card .agg-title {{ font-size: 15px; font-weight: 600; }}
.aggregate-card .agg-sub {{ font-size: 13px; color: var(--muted); margin-top: 2px; }}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}}
.card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  transition: transform 0.12s ease, border-color 0.12s ease;
  text-decoration: none;
  color: inherit;
}}
.card:hover {{
  border-color: var(--accent);
  transform: translateY(-2px);
}}
.card-head {{
  display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
}}
.card-icon {{
  width: 36px; height: 36px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 8px;
  background: rgba(77,171,247,0.1);
  color: var(--accent);
  font-size: 11px; font-weight: 700;
  font-family: ui-monospace, monospace;
  flex-shrink: 0;
}}
.card h2 {{
  margin: 0; font-size: 14px; font-weight: 600;
  font-family: ui-monospace, monospace;
  color: var(--text);
}}
.card p {{
  margin: 0 0 12px; font-size: 13px; color: var(--muted);
  flex: 1;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.card-stats {{
  display: flex; gap: 12px; flex-wrap: wrap;
  font-size: 11px; color: var(--muted);
  margin-bottom: 10px;
}}
.card-stats strong {{ color: var(--text); font-weight: 600; }}
.card-tags {{
  display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;
}}
.tag {{
  display: inline-block; padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px; font-weight: 500;
  background: rgba(81,207,102,0.1);
  color: var(--good);
  border: 1px solid rgba(81,207,102,0.25);
  max-width: 100%;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.card-cta {{
  display: inline-flex; align-items: center; gap: 4px;
  color: var(--accent);
  font-size: 13px; font-weight: 500;
  margin-top: auto;
}}
.card-cta::after {{ content: "→"; transition: transform 0.12s; }}
.card:hover .card-cta::after {{ transform: translateX(3px); }}
.card.hidden {{ display: none; }}
footer {{
  margin-top: 56px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
  display: flex; justify-content: space-between;
  flex-wrap: wrap; gap: 8px;
}}
footer a {{ color: var(--accent); text-decoration: none; }}
footer a:hover {{ text-decoration: underline; }}
.method {{
  margin-top: 32px;
  padding: 18px 22px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
}}
.method h3 {{ margin: 0 0 10px; font-size: 14px; }}
.method p {{ margin: 6px 0; font-size: 13px; color: var(--muted); }}
.method code {{
  font-family: ui-monospace, monospace;
  font-size: 12px;
  background: var(--bg);
  padding: 1px 6px;
  border-radius: 4px;
  color: var(--text);
}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <a href="https://jxb1st.github.io/datasets/" class="home-link">← Back to Dataset Visualizations</a>
    <h1>EgoSchema × Action100M Viewer</h1>
    <p class="tagline">
      Hierarchical dense action annotation pipeline (Chen et al., 2026 — Action100M)
      ported to {len(cards)} EgoSchema 3-minute egocentric clips. Each clip is segmented by
      V-JEPA 2 + Ward agglomerative clustering, captioned by Llama-3.2-Vision +
      Perception-LM, and aggregated by GPT-4o with 3-round Self-Refine. Click any
      card to open an interactive viewer with the source video, hierarchical timeline,
      and per-node annotations.
    </p>
    <div class="summary-stats">
      <div><strong>{len(cards)}</strong>clips</div>
      <div><strong>{int(total_duration)}s</strong>total video</div>
      <div><strong>{total_nodes:,}</strong>tree nodes</div>
      <div><strong>{total_annotated}</strong>GPT-4o annotated</div>
      <div><strong>${total_cost:.2f}</strong>API cost</div>
    </div>
  </header>

  <a class="aggregate-card" href="viewers/_aggregate_action_sunburst.html">
    <div class="agg-title">→ Aggregate verb-composition sunburst</div>
    <div class="agg-sub">verb→object→modifier word-frequency hierarchy across all 50 clips' action.brief annotations</div>
  </a>

  <div class="search">
    <input type="text" id="search" placeholder="Filter by clip id or summary text…">
  </div>

  <section class="grid" id="grid">
{cards_html}
  </section>

  <div class="method">
    <h3>Pipeline overview</h3>
    <p>
      <strong style="color:var(--text)">Stage 1.</strong> V-JEPA 2 ViT-g-384 frame embeddings (window=64, stride=8, res=384²)
      → temporal-contiguous Ward agglomerative clustering → ~600+ tree nodes per clip.
    </p>
    <p>
      <strong style="color:var(--text)">Stage 2.</strong> Leaf nodes captioned by <code>Llama-3.2-11B-Vision</code> on midpoint frame;
      internal nodes captioned by <code>Perception-LM-3B</code> on 32 evenly-spaced frames at 320×320.
    </p>
    <p>
      <strong style="color:var(--text)">Stage 3.</strong> Nodes ≥4s aggregated by <code>gpt-4o-2024-08-06</code>
      using global-tree-context + current-subtree-markdown, with 3-round Self-Refine and JSON-Schema-strict
      structured outputs (<code>{{summary, action}}</code>).
    </p>
    <p>
      Full method documentation:
      <a href="https://github.com/jxb1st/egoschema-action100m-viewer/blob/main/README.md">README</a> ·
      Source code (private):
      <code>streaming_benchmark/src/{{stage1,stage2,stage3}}_*.py</code>
    </p>
  </div>

  <footer>
    <span>Built with plain HTML + Plotly. Each viewer is a single-file page.</span>
    <a href="https://github.com/jxb1st/egoschema-action100m-viewer">github.com/jxb1st/egoschema-action100m-viewer</a>
  </footer>
</div>

<script>
const input = document.getElementById('search');
const cards = document.querySelectorAll('#grid .card');
input.addEventListener('input', () => {{
  const q = input.value.toLowerCase();
  cards.forEach(c => {{
    const text = c.textContent.toLowerCase();
    c.classList.toggle('hidden', q && !text.includes(q));
  }});
}});
</script>
</body>
</html>
"""

(REPO / "index.html").write_text(html)
print(f"Wrote index.html ({len(html)//1024}KB) with {len(cards)} cards")
