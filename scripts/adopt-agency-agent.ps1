# adopt-agency-agent.ps1 — Windows-native version of adopt-agency-agent.sh
# Downloads an agency-agent, wraps it with Bhishma compliance, and installs it
# as a Tier-0 worker in observer-test.
#
# Usage (from PowerShell in the observer-test directory):
#   .\scripts\adopt-agency-agent.ps1 `
#     -Source "security/security-application-security.md" `
#     -Name "Karna" `
#     -Emoji "⚔️"

param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Name,
    [int]$Tier = 0,
    [string]$Emoji = "🤖",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoBase    = "https://raw.githubusercontent.com/msitarzewski/agency-agents/main"
$ObserverRoot = Split-Path $PSScriptRoot -Parent
$AgentsDir   = Join-Path $ObserverRoot ".claude\agents"
$LogsDir     = Join-Path $ObserverRoot "logs"

$Slug      = $Name.ToLower()
$AgentDir  = Join-Path $AgentsDir $Slug
$LogDir    = Join-Path $LogsDir   $Slug
$RawUrl    = "$RepoBase/$Source"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Adopting agency-agent → $Name ($Slug)" -ForegroundColor White
Write-Host "  Source : agency-agents/$Source"
Write-Host "  Target : $AgentDir"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# ── 1. Fetch raw content ──────────────────────────────────────────────────────
Write-Host "`n[1/5] Fetching: $RawUrl" -ForegroundColor Gray
try {
    $RawContent = (Invoke-WebRequest -Uri $RawUrl -UseBasicParsing).Content
} catch {
    Write-Error "Could not fetch $RawUrl`n$($_.Exception.Message)"
    exit 1
}

# Extract description from frontmatter
$Description = ""
if ($RawContent -match "(?m)^description:\s*(.+)$") {
    $Description = $Matches[1].Trim()
}
if (-not $Description) { $Description = "Adopted from agency-agents: $Source" }

# Extract body (everything after the closing ---)
$Parts = $RawContent -split "(?m)^---\s*$"
$Body  = if ($Parts.Count -ge 3) { $Parts[2..($Parts.Count-1)] -join "---" } else { $RawContent }

$Today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")

# ── 2. Build agent.md ─────────────────────────────────────────────────────────
$AgentMd = @"
---
name: $Slug
icon: $Emoji
tier: $Tier
model: claude-sonnet-4-6
effort: medium
tools: [Read, Write, Edit, Glob, Grep, Bash]
write_scope:
  - ~/agents/observer-test/.claude/agents/$Slug/
  - ~/agents/observer-test/logs/$Slug/
read_scope:
  - ~/agents/observer-test/.claude/agents/_meta/conductor/bhishma.md
  - ~/agents/observer-test/.claude/agents/$Slug/skill.md
upstream: [kartavya, sanjaya]
downstream: []
source: agency-agents/$Source
---

# $Name — $($Description.Substring(0, [Math]::Min(80, $Description.Length)))

## Bhishma Compliance (read on every session start)

If ``_meta/conductor/bhishma.md`` is present, read it before reading your own files.

- **R2** — No self-modification. Do not edit your own ``agent.md`` or ``skill.md``.
- **R5** — Append-only journals. ``logs/$Slug/`` entries are never deleted or modified.
- **R11** — No writes outside your declared ``write_scope``.
- **R19** — All stored timestamps in UTC.
- **R20** — Every task begins with a run_id: ``$Slug-<YYYYMMDD-HHMMSSZ>-<6char-hash>``

``````bash
gen_run_id() {
  local args="`$1"
  local ts=`$(date -u +"%Y%m%d-%H%M%SZ")
  local hash=`$(printf "%s%s" "`$args" "`$ts" | sha256sum | head -c 6)
  echo "$Slug-`${ts}-`${hash}"
}
``````

## Logging (Sanjaya contract)

At task start, append to ``logs/$Slug/<run_id>.log``:
``````
# run_id: <run_id>
# task: <short description>
# started_at: <UTC ISO8601>
``````
At task end, append outcome (success | failure, output paths, ended_at).

---

$Body
"@

# ── 3. Build skill.md ─────────────────────────────────────────────────────────
$SkillMd = @"
# $Name — Skill Manual

> Adopted from agency-agents/$Source on $Today.
> Domain-expertise sections are faithful to the original agency-agents definition.
> Add Rootlabs-specific context at the bottom.

## Source

- **Agency-agents origin**: ``$Source``
- **Wrapper version**: 1.0.0
- **Bhishma compliance**: R2, R5, R11, R19, R20

## Standard Outputs

Every task produces:
- An entry in ``logs/$Slug/<run_id>.log`` (append-only)
- Any deliverables written to the ``write_scope`` paths in frontmatter

## Rootlabs Context

_(Add Rootlabs-specific instructions here — data source paths, POC conventions, etc.)_

## Change log

- $Today — Adopted from agency-agents via adopt-agency-agent.ps1
"@

# ── Dry run preview ───────────────────────────────────────────────────────────
if ($DryRun) {
    Write-Host "`n[DRY RUN] Would create:" -ForegroundColor Yellow
    Write-Host "  $AgentDir\agent.md"
    Write-Host "  $AgentDir\skill.md"
    Write-Host "  $LogDir\"
    Write-Host "`n── agent.md preview (first 30 lines) ──" -ForegroundColor Gray
    $AgentMd -split "`n" | Select-Object -First 30 | ForEach-Object { Write-Host $_ }
    exit 0
}

# ── 4. Write files ────────────────────────────────────────────────────────────
Write-Host "[2/5] Creating agent directory..." -ForegroundColor Gray
New-Item -ItemType Directory -Force $AgentDir | Out-Null

Write-Host "[3/5] Writing agent.md..." -ForegroundColor Gray
Set-Content -Path (Join-Path $AgentDir "agent.md") -Value $AgentMd -Encoding utf8

Write-Host "[4/5] Writing skill.md..." -ForegroundColor Gray
Set-Content -Path (Join-Path $AgentDir "skill.md") -Value $SkillMd -Encoding utf8

Write-Host "[5/5] Creating log directory..." -ForegroundColor Gray
New-Item -ItemType Directory -Force $LogDir | Out-Null

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  Done. $Name is now a Tier-$Tier worker." -ForegroundColor White
Write-Host ""
Write-Host "  Next steps:"
Write-Host "  1. Review: $AgentDir\agent.md"
Write-Host "     - Adjust write_scope, tools, downstream as needed"
Write-Host "  2. Edit: $AgentDir\skill.md"
Write-Host "     - Add Rootlabs-specific context at the bottom"
Write-Host "  3. Add $Slug to Sanjaya's monitoring roster"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
