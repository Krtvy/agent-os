# install.ps1 — One-time setup: copies Hermes skills and wires the cron job
# Run AFTER installing Hermes Agent with:
#   iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
#
# Usage (from this repo root):
#   cd "$HOME\projects\observer-test"
#   .\hermes-skills\install.ps1

$ErrorActionPreference = "Stop"

$HermesHome = "$env:LOCALAPPDATA\hermes"
$SkillsDest = "$HermesHome\skills"
$SkillsSrc  = "$PSScriptRoot"
$BridgeLog  = "$HOME\projects\observer-test\logs\hermes-bridge"

# ── 1. Verify Hermes is installed ────────────────────────────────────────────
Write-Host "`n[1/5] Checking Hermes installation..." -ForegroundColor Cyan
$hermesCmd = Get-Command hermes -ErrorAction SilentlyContinue
if (-not $hermesCmd) {
    Write-Error "hermes command not found. Install Hermes first:`n  iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)"
    exit 1
}
Write-Host "      hermes found at: $($hermesCmd.Source)" -ForegroundColor Green

# ── 2. Ensure skills destination exists ──────────────────────────────────────
Write-Host "`n[2/5] Ensuring ~/.hermes/skills/ exists..." -ForegroundColor Cyan
if (-not (Test-Path $SkillsDest)) {
    New-Item -ItemType Directory -Path $SkillsDest -Force | Out-Null
    Write-Host "      Created $SkillsDest" -ForegroundColor Green
} else {
    Write-Host "      Already exists: $SkillsDest" -ForegroundColor Green
}

# ── 3. Copy skill directories ─────────────────────────────────────────────────
$skills = @("observer-status", "nakula-trigger", "ecosystem-health")

Write-Host "`n[3/5] Copying skills to ~/.hermes/skills/..." -ForegroundColor Cyan
foreach ($skill in $skills) {
    $src  = Join-Path $SkillsSrc $skill
    $dest = Join-Path $SkillsDest $skill
    if (-not (Test-Path $src)) {
        Write-Warning "Skill directory not found: $src — skipping"
        continue
    }
    if (Test-Path $dest) {
        Write-Host "      Updating $skill (already exists)" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $dest
    }
    Copy-Item -Recurse $src $dest
    Write-Host "      Copied: $skill -> $dest" -ForegroundColor Green
}

# ── 4. Create hermes-bridge log directory ────────────────────────────────────
Write-Host "`n[4/5] Creating logs/hermes-bridge/ directory..." -ForegroundColor Cyan
if (-not (Test-Path $BridgeLog)) {
    New-Item -ItemType Directory -Path $BridgeLog -Force | Out-Null
    Write-Host "      Created $BridgeLog" -ForegroundColor Green
} else {
    Write-Host "      Already exists: $BridgeLog" -ForegroundColor Green
}

# ── 5. Register Hermes cron job ───────────────────────────────────────────────
Write-Host "`n[5/5] Registering ecosystem-health cron job in Hermes..." -ForegroundColor Cyan
Write-Host "      Running: hermes cron create ..." -ForegroundColor Gray

# Check if job already exists
$existingJobs = hermes cron list 2>&1
if ($existingJobs -match "ecosystem-health-check") {
    Write-Host "      Cron job 'ecosystem-health-check' already exists — skipping" -ForegroundColor Yellow
} else {
    hermes cron create `
        "Run the ecosystem-health skill to check observer-ecosystem log freshness and write health.json to logs/hermes-bridge/" `
        --skill ecosystem-health
    Write-Host "      Cron job created. Edit schedule with: hermes cron edit ecosystem-health-check" -ForegroundColor Green
    Write-Host "      Default schedule is every 6 hours. To adjust:" -ForegroundColor Gray
    Write-Host "        hermes cron list                    (get the job ID)" -ForegroundColor Gray
    Write-Host "        hermes cron edit <id> --schedule '0 */6 * * *'" -ForegroundColor Gray
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host "`n─────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "Setup complete. What's been installed:" -ForegroundColor White
Write-Host ""
Write-Host "  Skills (slash commands in Hermes):" -ForegroundColor White
Write-Host "    /observer-status   — instant ecosystem health report"
Write-Host "    /nakula-trigger    — manually fire a Nakula job"
Write-Host "    /ecosystem-health  — run the health watchdog now"
Write-Host ""
Write-Host "  Cron: ecosystem-health runs every 6 hours (when gateway is running)"
Write-Host "  Bridge log: $BridgeLog"
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. hermes gateway install   (start cron at login)"
Write-Host "    2. hermes                   (open Hermes chat)"
Write-Host "    3. /observer-status         (verify the skill works)"
Write-Host "─────────────────────────────────────────────────────" -ForegroundColor DarkGray
