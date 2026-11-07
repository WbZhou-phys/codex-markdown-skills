param(
    [Parameter(Mandatory = $true)]
    [string]$Source,
    [string]$OutputDir = "output/pdf",
    [string]$BuildDir = ".md-to-pdf-build",
    [string]$Name,
    [string]$Css,
    [ValidateSet("A4", "A3", "Letter", "Legal")]
    [string]$PageSize = "A4",
    [switch]$Landscape,
    [string]$SeriesLabel = "COURSE NOTES · Markdown collection",
    [string]$SeriesNote = "Exported with md-to-pdf",
    [string]$HeaderLeft = "Markdown notes",
    [string]$HeaderRight = "Course notes",
    [string]$FooterLeft = "",
    [switch]$Offline,
    [string]$Only
)

$ErrorActionPreference = "Stop"
$buildScript = Join-Path $PSScriptRoot "build_html.py"
$printScript = Join-Path $PSScriptRoot "print_pdf.cjs"

function Test-Executable {
    param([string]$Path)
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) {
        return $false
    }
    try {
        & $Path --version *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

$pythonCandidates = @()
if ($env:PYTHON) {
    $pythonCandidates += $env:PYTHON
}
$runtimeRoot = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python"
if (Test-Path -LiteralPath $runtimeRoot) {
    $pythonCandidates += Get-ChildItem -LiteralPath $runtimeRoot -Filter "python.exe" -Recurse |
        Select-Object -ExpandProperty FullName
}
foreach ($commandName in @("python", "python3")) {
    $command = Get-Command $commandName -ErrorAction SilentlyContinue
    if ($command) {
        $pythonCandidates += $command.Source
    }
}
$pythonExe = $pythonCandidates | Where-Object { Test-Executable $_ } | Select-Object -First 1
if (-not $pythonExe) {
    throw "No working Python interpreter was found. Set PYTHON to a Python 3 executable."
}

$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCommand) {
    throw "Node.js was not found in PATH."
}

$buildArgs = @(
    $buildScript,
    $Source,
    "--output-dir", $OutputDir,
    "--build-dir", $BuildDir,
    "--series-label", $SeriesLabel,
    "--series-note", $SeriesNote,
    "--header-left", $HeaderLeft,
    "--header-right", $HeaderRight,
    "--footer-left", $FooterLeft,
    "--page-size", $PageSize
)
if ($Name) { $buildArgs += @("--name", $Name) }
if ($Css) { $buildArgs += @("--css", $Css) }
if ($Landscape) { $buildArgs += "--landscape" }

& $pythonExe @buildArgs
if ($LASTEXITCODE -ne 0) {
    throw "HTML generation failed with exit code $LASTEXITCODE."
}

$manifestPath = Join-Path $BuildDir "manifest.json"
$printArgs = @($printScript, $manifestPath)
if ($Offline) { $printArgs += "--offline" }
if ($Only) { $printArgs += @("--only", $Only) }

& $nodeCommand.Source @printArgs
if ($LASTEXITCODE -ne 0) {
    throw "PDF printing failed with exit code $LASTEXITCODE."
}
