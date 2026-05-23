# wakatime-activity

<div align="center">

Turn your WakaTime stats into a profile-style activity heatmap.

<br>

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="https://raw.githubusercontent.com/jkdevcode/wakatime-activity/main/waka-heatmap-dark.svg"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="https://raw.githubusercontent.com/jkdevcode/wakatime-activity/main/waka-heatmap.svg"
  />
  <img
    alt="WakaTime activity heatmap"
    src="https://raw.githubusercontent.com/jkdevcode/wakatime-activity/main/waka-heatmap.svg"
  />
</picture>

</div>

---

## Features

- WakaTime yearly activity heatmap
- Automatic dark/light mode in `README.md`
- Profile-style layout with months, weekdays, and legend
- Fixed hour buckets for consistent colors
- GitHub Actions automation
- Local `.env` support for testing
- Lightweight setup with plain Python and SVG output

---

## How It Works

This project fetches your WakaTime daily data from `GET /users/{id}/insights/days?range=last_year` and renders two SVG files:

- `waka-heatmap.svg`
- `waka-heatmap-dark.svg`

The workflow automatically:

- loads your `WAKATIME_API_KEY` from GitHub Secrets
- fetches the last year of WakaTime daily activity
- generates light and dark SVG heatmaps
- commits the updated SVG files back to `main`

---

## Notes

- The generator uses WakaTime `GET /users/{id}/insights/days?range=last_year`.
- Availability of historical data may depend on your WakaTime plan and account data retention.
- The workflow only needs `WAKATIME_API_KEY` because the script defaults to `current` when `WAKATIME_USERNAME` is not provided.
- Generated files are committed directly to `main`; this repo does not use a separate `output` branch.

---

## Setup

1. Fork this repository.
2. Add a repository secret named `WAKATIME_API_KEY`.
3. Optionally set `WAKATIME_USERNAME` locally if you do not want to use `current`.
4. Enable GitHub Actions.
5. Run the `Update WakaTime Heatmap` workflow manually once, or wait for the daily schedule.

---

## Local Usage

Quick start for Windows PowerShell:

```powershell
.\run_local.ps1
```

Manual alternative:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_waka_heatmap.py
```

You can also copy `.env.example` to `.env` and set:

```env
WAKATIME_API_KEY=your_api_key_here
WAKATIME_USERNAME=current
```

---

## Automation

GitHub Actions runs the generator:

- on `workflow_dispatch`
- every 24 hours at `04:00` UTC

The workflow tracks only the generated SVG outputs.
