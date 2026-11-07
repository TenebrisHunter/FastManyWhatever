# ============================================================
#  FastManyWhatever — create-by-rule (Windows / PowerShell)
#  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
#  Версия: 0.1.0
# ============================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Dir,
    [Parameter(Mandatory=$true)][int]$From,
    [Parameter(Mandatory=$true)][int]$To,
    [int]$Step = 1,
    [string]$Prefix = "",
    [string]$Suffix = "",
    [string]$Ext = "",
    [ValidateSet('1','01','001','0001')][string]$Pad = "1",
    [ValidateSet('file','folder')][string]$Kind = "file",
    [switch]$DryRun,
    [string]$LogFile = ""
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$script:ForbiddenChars = [char[]]@('\','/',':','*','?','"','<','>','|')
$script:ReservedNames = @(
    'CON','PRN','AUX','NUL',
    'COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9',
    'LPT1','LPT2','LPT3','LPT4','LPT5','LPT6','LPT7','LPT8','LPT9'
)

function Test-ValidName {
    param([string]$Name)
    if ([string]::IsNullOrEmpty($Name)) { return @{ Valid=$false; Reason='empty name' } }
    if ($Name.Length -gt 255) { return @{ Valid=$false; Reason='name too long (>255)' } }
    foreach ($ch in $script:ForbiddenChars) {
        if ($Name.Contains($ch)) { return @{ Valid=$false; Reason="forbidden char: $ch" } }
    }
    if ($Name.EndsWith(' ') -or $Name.EndsWith('.')) {
        return @{ Valid=$false; Reason='trailing space or dot' }
    }
    $stem = $Name
    $dotIdx = $stem.IndexOf('.')
    if ($dotIdx -gt 0) { $stem = $stem.Substring(0, $dotIdx) }
    if ($script:ReservedNames -contains $stem.ToUpperInvariant()) {
        return @{ Valid=$false; Reason="reserved name: $stem" }
    }
    return @{ Valid=$true; Reason='' }
}

if ($From -gt $To) { Write-Host "error: 'From' ($From) > 'To' ($To)"; exit 1 }
if ($Step -lt 1) { Write-Host "error: 'Step' must be >= 1"; exit 1 }
$count = [int][Math]::Floor(($To - $From) / $Step) + 1
if ($count -gt 10000) { Write-Host "error: too many items ($count > 10000)"; exit 1 }
if ($Ext -and -not $Ext.StartsWith('.')) { $Ext = '.' + $Ext }

try {
    $root = Get-Item -LiteralPath $Dir -ErrorAction Stop
    if (-not $root.PSIsContainer) { throw "Not a directory: $Dir" }
} catch {
    Write-Host "error: $($_.Exception.Message)"; exit 1
}

$digits = $Pad.Length
$plan = @()
for ($n = $From; $n -le $To; $n += $Step) {
    $num = if ($digits -gt 1) { $n.ToString().PadLeft($digits, '0') } else { "$n" }
    $name = "$Prefix$num$Suffix"
    if ($Kind -eq 'file') { $name = "$name$Ext" }
    $plan += $name
}

$ok=0; $skipped=0; $errors=0; $logLines=@()
foreach ($name in $plan) {
    $check = Test-ValidName -Name $name
    if (-not $check.Valid) {
        Write-Host "[ERR]  $name : $($check.Reason)"
        $errors++
        continue
    }
    $path = Join-Path $root.FullName $name
    if (Test-Path -LiteralPath $path) {
        Write-Host "[SKIP] $name (exists)"
        $skipped++
        continue
    }
    if ($DryRun) {
        Write-Host "[DRY]  $name"
        $ok++
        continue
    }
    try {
        if ($Kind -eq 'folder') {
            New-Item -ItemType Directory -Path $path -ErrorAction Stop | Out-Null
        } else {
            New-Item -ItemType File -Path $path -ErrorAction Stop | Out-Null
        }
        Write-Host "[OK]   $name"
        $logLines += "$path"
        $ok++
    } catch {
        Write-Host "[ERR]  $name : $($_.Exception.Message)"
        $errors++
    }
}

if ($LogFile -and -not $DryRun -and $logLines.Count -gt 0) {
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::AppendAllText($LogFile, ($logLines -join "`r`n") + "`r`n", $utf8)
}

Write-Host ""
Write-Host "Summary: ok=$ok skipped=$skipped errors=$errors"
if ($errors -gt 0) { exit 2 } else { exit 0 }