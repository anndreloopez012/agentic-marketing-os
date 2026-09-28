# ==============================================================================
# Agentic Marketing OS - Instalador para Windows (PowerShell)
# Copia las skills a Claude Code y a Codex (CLI, app o extension con tu cuenta de ChatGPT).
#
# Uso (PowerShell, dentro de la carpeta del repositorio):
#   powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Agents claude
#   powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Uninstall
#
# Para la memoria con Obsidian, video y CLIs completos se recomienda WSL + install.sh.
# ==============================================================================

param(
    [ValidateSet("all", "claude", "codex", "gemini")]
    [string[]]$Agents = @("all"),
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Marker = ".agentic-marketing-os"

$Targets = @{
    claude = Join-Path $HOME ".claude\skills"
    codex  = Join-Path $HOME ".agents\skills"
    gemini = Join-Path $HOME ".gemini\config\skills"
}
if ($Agents -contains "all") { $Agents = @("claude", "codex", "gemini") }

function Write-Ok($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [!]  $msg" -ForegroundColor Yellow }

if ($Uninstall) {
    foreach ($root in $Targets.Values) {
        if (-not (Test-Path $root)) { continue }
        $removed = 0
        Get-ChildItem $root -Directory | Where-Object { Test-Path (Join-Path $_.FullName $Marker) } | ForEach-Object {
            Remove-Item $_.FullName -Recurse -Force; $removed++
        }
        Write-Ok "${root}: $removed skills quitadas"
    }
    exit 0
}

Write-Host "`n=== AGENTIC MARKETING OS - Instalador para Windows ===`n" -ForegroundColor Cyan

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Warn "Python no encontrado. Instalalo desde https://www.python.org/downloads/ (marca 'Add to PATH')."
    exit 1
}

$skillDirs = & $python.Source (Join-Path $RepoRoot "scripts\skills_tool.py") list --paths
foreach ($agent in $Agents) {
    $root = $Targets[$agent]
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $installed = 0; $kept = 0
    foreach ($dir in $skillDirs) {
        if (-not $dir) { continue }
        $name = Split-Path $dir -Leaf
        $dest = Join-Path $root $name
        if ((Test-Path $dest) -and -not (Test-Path (Join-Path $dest $Marker))) {
            $kept++; continue
        }
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        Copy-Item $dir $dest -Recurse
        # Las skills anidadas se instalan por separado; no se duplican dentro de la padre.
        Get-ChildItem $dest -Recurse -Filter SKILL.md | Where-Object { $_.DirectoryName -ne $dest } | ForEach-Object {
            Remove-Item $_.DirectoryName -Recurse -Force -ErrorAction SilentlyContinue
        }
        New-Item -ItemType File -Path (Join-Path $dest $Marker) -Force | Out-Null
        $installed++
    }
    $summary = "${agent}: $installed skills en $root"
    if ($kept) { $summary += " ($kept tuyas conservadas)" }
    Write-Ok $summary
}

$envFile = Join-Path $RepoRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $RepoRoot ".env.example") $envFile
    Write-Ok "Creado .env para tus claves de API"
}

Write-Host "`nListo. Reinicia Claude Code o Codex para que detecten las skills." -ForegroundColor Green
Write-Host "Para ChatGPT web o claude.ai: python scripts\skills_tool.py package  y sube los zips de dist\skills.`n"
