<#
Set the local OpenRouter key in the repo-root .env file used by Stage 2 helper scripts.

This script prompts for the key with hidden input, writes OPENROUTER_API_KEY to the
ignored repo-root .env file, and makes it available to the current PowerShell process.
It intentionally never echoes the key.
#>

[CmdletBinding()]
param(
    [switch]$FromClipboard,
    [switch]$KeepClipboard,
    [switch]$Status
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$EnvPath = Join-Path $RepoRoot '.env'
$EnvExamplePath = Join-Path $RepoRoot '.env.example'

function Ensure-RepoEnvFile {
    if (Test-Path $EnvPath) {
        return
    }
    if (Test-Path $EnvExamplePath) {
        Copy-Item $EnvExamplePath $EnvPath
        return
    }
    @"
# Local development only. Do not assume these are available in the official solver subprocess.
OPENROUTER_API_KEY=
OPENAI_API_KEY=
OPENAI_BASE_URL=https://openrouter.ai/api/v1
SAIR_STAGE2_MODEL=openai/gpt-oss-120b
"@ | Set-Content $EnvPath -Encoding utf8
}

function Get-RepoEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not (Test-Path $EnvPath)) {
        return ''
    }
    $content = Get-Content $EnvPath -Raw -Encoding UTF8
    $escapedName = [Regex]::Escape($Name)
    $match = [Regex]::Match($content, "(?m)^$escapedName=(.*)$")
    if (-not $match.Success) {
        return ''
    }
    return $match.Groups[1].Value.Trim()
}

function Set-RepoEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    Ensure-RepoEnvFile
    $content = Get-Content $EnvPath -Raw -Encoding UTF8
    $escapedName = [Regex]::Escape($Name)
    $replacement = "$Name=$Value"
    if ([Regex]::IsMatch($content, "(?m)^$escapedName=.*$")) {
        $content = [Regex]::Replace($content, "(?m)^$escapedName=.*$", $replacement, 1)
    }
    else {
        if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) {
            $content += "`r`n"
        }
        $content += $replacement + "`r`n"
    }
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($EnvPath, $content, $encoding)
}

function Set-OpenRouterKeyValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Plain
    )

    if ([string]::IsNullOrWhiteSpace($Plain)) {
        throw 'No key was provided.'
    }
    $Plain = $Plain.Trim()
    if (-not $Plain.StartsWith('sk-or-v1-')) {
        throw 'Input did not look like an OpenRouter key; expected prefix sk-or-v1-. Existing repo value was left unchanged.'
    }
    if ($Plain.Length -lt 40) {
        throw 'Input was too short to be a full OpenRouter key. Existing repo value was left unchanged.'
    }
    if ($Plain -match '\s') {
        throw 'Input contains whitespace. Copy only the key, with no quotes or surrounding text. Existing repo value was left unchanged.'
    }
    Set-RepoEnvValue -Name 'OPENROUTER_API_KEY' -Value $Plain
    $env:OPENROUTER_API_KEY = $Plain
}

Write-Host 'This stores OPENROUTER_API_KEY in the ignored repo-root .env used by Stage 2 helper scripts.'
Write-Host 'Use a rotated key if the previous value was pasted into chat or logs.'

$existing = Get-RepoEnvValue -Name 'OPENROUTER_API_KEY'
if (-not [string]::IsNullOrWhiteSpace($existing)) {
    Write-Host ('Existing repo key shape: length={0}, starts_sk_or_v1={1}, path={2}' -f $existing.Length, $existing.StartsWith('sk-or-v1-'), $EnvPath)
}
elseif (Test-Path $EnvPath) {
    Write-Host ('Repo env file exists at {0}.' -f $EnvPath)
}
else {
    Write-Host ('Repo env file will be created at {0}.' -f $EnvPath)
}

if ($Status) {
    $processValue = if ($null -eq $env:OPENROUTER_API_KEY) { '' } else { $env:OPENROUTER_API_KEY }
    Write-Host ('Process key shape: length={0}, starts_sk_or_v1={1}' -f $processValue.Length, $processValue.StartsWith('sk-or-v1-'))
    return
}

if ($FromClipboard) {
    Write-Host 'Reading key from the local Windows clipboard. The key will not be echoed.'
    $clipboardText = Get-Clipboard -Raw -ErrorAction Stop
    Set-OpenRouterKeyValue -Plain ([string]$clipboardText)
    if (-not $KeepClipboard) {
        Set-Clipboard -Value ''
        Write-Host 'Clipboard cleared.'
    }
    Write-Host ('OPENROUTER_API_KEY is configured in {0} and this PowerShell process. Stored key length={1}.' -f $EnvPath, $env:OPENROUTER_API_KEY.Length)
    Write-Host 'Repo-owned Stage 2 entrypoints load process env first, then .env, then legacy Windows User env fallback.'
    return
}

$secret = Read-Host 'Paste OpenRouter key (input hidden)' -AsSecureString

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    Set-OpenRouterKeyValue -Plain $plain
}
finally {
    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

Write-Host ('OPENROUTER_API_KEY is configured in {0} and this PowerShell process. Stored key length={1}.' -f $EnvPath, $env:OPENROUTER_API_KEY.Length)
Write-Host 'Repo-owned Stage 2 entrypoints load process env first, then .env, then legacy Windows User env fallback.'