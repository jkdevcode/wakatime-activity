# AGENTS.md

## Repo Shape
- The repo has one executable source file: `generate_waka_heatmap.py`. It fetches WakaTime daily insights and rewrites the root SVG artifacts `waka-heatmap.svg` and `waka-heatmap-dark.svg`.
- `.github/workflows/update-graph.yml` is the automation source of truth: it runs on `workflow_dispatch` and daily at `04:00` UTC, installs dependencies with `pip install svgwrite requests`, runs the script, and commits only the generated SVG files back to `main`.

## Run And Verify
- There is no `requirements.txt` or `pyproject.toml`; local setup matches CI: `pip install requests svgwrite`.
- Required env: `WAKATIME_API_KEY`. Optional env: `WAKATIME_USERNAME` defaults to `current`.
- Repo-native verification is minimal: `python -m py_compile generate_waka_heatmap.py`, then run `python generate_waka_heatmap.py` with the env vars set and inspect both regenerated SVGs.
- The script prints the raw API response and per-day totals to stdout. Noisy logs are expected and are not by themselves a failure.

## Script Constraints
- The script now uses WakaTime `GET /users/{id}/insights/days?range=last_year`, not the old `/summaries` endpoint. If you change the endpoint or range, re-check the grid math and whether the response still includes one entry per day.
- The grid is built as continuous Sunday-through-Saturday columns. `get_data()` pads missing leading and trailing days with zeroes so `draw_svg()` can rely on `index // 7` and `index % 7` for placement.
- Color levels now use fixed hour buckets (`<1`, `1-3`, `4-8`, `9-10`, `11-12`, `13+`) and the SVG includes profile-style month labels, weekday labels, and a Less→More legend. Preserve that layout unless the request explicitly changes it.
- The README uses a `<picture>` element to swap `waka-heatmap.svg` and `waka-heatmap-dark.svg` based on `prefers-color-scheme`; if filenames or paths change, update both the README and workflow.
