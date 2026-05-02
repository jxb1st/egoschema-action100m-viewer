# EgoSchema × Action100M Viewer

Interactive case-by-case browser for an Action100M-style hierarchical dense
action annotation pipeline applied to **50 EgoSchema 3-minute egocentric clips**.

**Live site**: https://jxb1st.github.io/egoschema-action100m-viewer/

## What's in this repo

```
.
├── index.html                  # panel/landing page (50 cards + filter + stats)
├── viewers/
│   ├── <q_uid>.html            # 50 per-clip interactive viewers
│   └── _aggregate_action_sunburst.html  # plotly verb-composition sunburst
├── videos/
│   └── <q_uid>.mp4             # 50 source mp4 clips (~921 MB total)
├── build_index.py              # regenerates index.html from Stage 3 outputs
├── .nojekyll                   # disable Jekyll processing on GitHub Pages
└── README.md
```

Each per-clip viewer is a **single self-contained HTML** with:
- HTML5 `<video>` referencing `../videos/<q_uid>.mp4`
- Plotly horizontal-bar timeline of all ~600 tree nodes (blue = GPT-4o annotated, gray = raw VLM caption only)
- Click-to-seek + click-to-show-annotation interactions
- Red playhead line tracking video time

## Pipeline summary

| Stage | Model | What it does |
|---|---|---|
| 1 | V-JEPA 2 ViT-g-384 + Ward agglomerative clustering | Temporal-contiguous hierarchical segmentation → tree of ~600 nodes |
| 2a (leaves) | Llama-3.2-11B-Vision | Caption single midpoint frame → `raw_caption` (frame) |
| 2b (internals) | Perception-LM-3B | Caption 32 evenly-spaced frames → `raw_caption` (segment) |
| 3 | GPT-4o-2024-08-06 (3-round Self-Refine) | Aggregate captions → `{summary, action}` JSON for nodes ≥4s |
| 4 | matplotlib + Plotly | Visualization (PNG + HTML) |

Total cost across 50 clips: ~$70 (mostly GPT-4o API).

## How to deploy

This repo is sized to fit GitHub Pages' 1 GB recommendation
(~957 MB total: 921 MB videos + 36 MB HTMLs).

### One-time setup
```bash
cd egoschema-action100m-viewer
git init -b main
git add -A
git commit -m "feat: initial EgoSchema × Action100M viewer"
git remote add origin git@github.com:jxb1st/egoschema-action100m-viewer.git
git push -u origin main
```

Then on GitHub:
1. Settings → Pages → Source = "Deploy from a branch", Branch = `main`, folder = `/`
2. Wait ~2 min for the first build
3. Site goes live at `https://jxb1st.github.io/egoschema-action100m-viewer/`

### Linking from the dataset index
Add a card to `https://github.com/jxb1st/jxb1st.github.io` under `datasets/index.html`:

```html
<a class="card" href="https://jxb1st.github.io/egoschema-action100m-viewer/">
  <div class="card-head">
    <span class="card-icon" style="background:rgba(81,207,102,0.1);color:var(--good);">EA</span>
    <h2>EgoSchema × Action100M</h2>
  </div>
  <p>
    Hierarchical dense action annotations on 50 EgoSchema 3-minute egocentric clips.
    V-JEPA 2 segmentation + Llama/PerceptionLM captions + GPT-4o aggregation.
  </p>
  <div class="card-stats">
    <span><strong>50</strong> clips</span>
    <span><strong>~600</strong> nodes/clip</span>
    <span><strong>$70</strong> total cost</span>
  </div>
  <div class="card-tags">
    <span class="tag">video</span>
    <span class="tag purple">egocentric</span>
    <span class="tag green">hierarchical</span>
  </div>
  <span class="card-cta">Open viewer</span>
</a>
```

## How to view locally without deploying

```bash
cd egoschema-action100m-viewer
python -m http.server 8000
# open http://localhost:8000/
```

Direct `file://` won't work — Chrome blocks relative-path video loading from
local files. The HTTP server is required.

## Method documentation

The full Chinese pipeline writeup (algorithms, prompt templates, design
tradeoffs) lives in the source repo at
`streaming_benchmark/claude_tasks/action100m_egoschema/pipeline_overview_zh.md`.

## Source clips

EgoSchema (Mangalam et al., NeurIPS 2023): https://github.com/egoschema/EgoSchema

These 50 clips were sampled with `seed=42` from the full 5031-clip release and
re-encoded for compactness without recompression of pixel data.

## Citation

```bibtex
@inproceedings{action100m,
  title={Action100M: ...},
  author={Chen et al.},
  year={2026}
}
@inproceedings{egoschema,
  title={EgoSchema: A Diagnostic Benchmark for Very Long-form Video Language Understanding},
  author={Mangalam, Karttikeya and Akbari, Hassan and Malik, Jitendra and others},
  booktitle={NeurIPS},
  year={2023}
}
```
