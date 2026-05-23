# Create virtual environment, install deps, prompt for credentials and run script
$venv = ".venv"
if (-not (Test-Path $venv)) {
    python -m venv $venv
}
# Activate venv for this session
. "$venv\Scripts\Activate.ps1"
# Install requirements
pip install -r requirements.txt

# Prompt for WakaTime credentials
$api = Read-Host "WAKATIME_API_KEY (enter your API key)"
$username = Read-Host "WAKATIME_USERNAME (press Enter for 'current')"
if ($username -eq "") { $username = "current" }

# Write .env file
$envContent = "WAKATIME_API_KEY=$api`nWAKATIME_USERNAME=$username"
Set-Content -Path .env -Value $envContent -Encoding UTF8

# Run the script
python generate_waka_heatmap.py
