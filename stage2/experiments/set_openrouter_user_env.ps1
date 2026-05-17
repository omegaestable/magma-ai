<#
Set the local OpenRouter key for official Stage 2 runner experiments.

This script prompts for the key with hidden input, stores it as a Windows
User environment variable, and makes it available to the current PowerShell
process. It intentionally never echoes the key.
#>

[CmdletBinding()]
param(
    [switch]$FromClipboard,
    [switch]$KeepClipboard
)

$ErrorActionPreference = 'Stop'

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
        throw 'Input did not look like an OpenRouter key; expected prefix sk-or-v1-. Existing environment value was left unchanged.'
    }
    if ($Plain.Length -lt 40) {
        throw 'Input was too short to be a full OpenRouter key. Existing environment value was left unchanged.'
    }
    if ($Plain -match '\s') {
        throw 'Input contains whitespace. Copy only the key, with no quotes or surrounding text. Existing environment value was left unchanged.'
    }
    [Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', $Plain, 'User')
    $env:OPENROUTER_API_KEY = $Plain
}

Write-Host 'This stores OPENROUTER_API_KEY in the Windows User environment.'
Write-Host 'Use a rotated key if the previous value was pasted into chat or logs.'

$existing = [Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY', 'User')
if (-not [string]::IsNullOrWhiteSpace($existing)) {
    Write-Host ('Existing user key shape: length={0}, starts_sk_or_v1={1}' -f $existing.Length, $existing.StartsWith('sk-or-v1-'))
}

if ($FromClipboard) {
    Write-Host 'Reading key from the local Windows clipboard. The key will not be echoed.'
    $clipboardText = Get-Clipboard -Raw -ErrorAction Stop
    Set-OpenRouterKeyValue -Plain ([string]$clipboardText)
    if (-not $KeepClipboard) {
        Set-Clipboard -Value ''
        Write-Host 'Clipboard cleared.'
    }
    Write-Host ('OPENROUTER_API_KEY is configured for this process and future user terminals. Stored key length={0}.' -f $env:OPENROUTER_API_KEY.Length)
    Write-Host 'Restart VS Code terminals before long runner sessions.'
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

Write-Host ('OPENROUTER_API_KEY is configured for this process and future user terminals. Stored key length={0}.' -f $env:OPENROUTER_API_KEY.Length)
Write-Host 'Restart VS Code terminals before long runner sessions.'
