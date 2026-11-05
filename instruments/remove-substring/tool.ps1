# ============================================================
#  FastManyWhatever — remove-substring (Windows / PowerShell)
#  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
#  Версия: 0.1.0
# ============================================================
#  Usage:
#    .\tool.ps1 -Dir "D:\photos" -Substring "(NEW)" -DryRun
#    .\tool.ps1 -Dir "D:\photos" -Substring "_old" -Files "a.txt","b.txt"

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Dir,
    [Parameter(Mandatory=$true)][string]$Substring,
    [string[]]$Files = @(),
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

function Get-RenamePlan {
    param([System.IO.FileSystemInfo[]]$Items, [string]$Substring)
    $plan = @()
    foreach ($item in $Items) {
        $name = $item.Name
        $isDir = $item.PSIsContainer
        $newName = $name.Replace($Substring, '')
        $check = Test-ValidName -Name $newName
        $plan += [PSCustomObject]@{
            Old=$name; OldFull=$item.FullName; New=$newName
            IsDir=$isDir; Valid=$check.Valid; Reason=$check.Reason
        }
    }
    return ,$plan
}

function Invoke-RenamePlan {
    param([object[]]$Plan, [string]$Dir, [switch]$DryRun, [string]$LogFile = "")
    $ok=0; $skipped=0; $errors=0; $logLines=@()
    foreach ($op in $Plan) {
        if (-not $op.Valid) { Write-Host "[ERR]  $($op.Old) : $($op.Reason)"; $errors++; continue }
        if ($op.New -eq $op.Old) { Write-Host "[SAME] $($op.Old)"; $skipped++; continue }
        $targetPath = Join-Path $Dir $op.New
        if (Test-Path -LiteralPath $targetPath) {
            Write-Host "[SKIP] $($op.Old) -> $($op.New) (exists)"; $skipped++; continue
        }
        if ($DryRun) { Write-Host "[DRY]  $($op.Old) -> $($op.New)"; $ok++; continue }
        try {
            Rename-Item -LiteralPath $op.OldFull -NewName $op.New -ErrorAction Stop
            Write-Host "[OK]   $($op.Old) -> $($op.New)"
            $logLines += "$($op.OldFull)`t$targetPath"; $ok++
        } catch {
            Write-Host "[ERR]  $($op.Old) : $($_.Exception.Message)"; $errors++
        }
    }
    if ($LogFile -and -not $DryRun -and $logLines.Count -gt 0) {
        $utf8 = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::AppendAllText($LogFile, ($logLines -join "`r`n") + "`r`n", $utf8)
    }
    Write-Host ""
    Write-Host "Summary: ok=$ok skipped=$skipped errors=$errors"
    if ($errors -gt 0) { return 2 } else { return 0 }
}

try {
    $root = Get-Item -LiteralPath $Dir -ErrorAction Stop
    if (-not $root.PSIsContainer) { throw "Not a directory: $Dir" }
} catch {
    Write-Host "error: $($_.Exception.Message)"; exit 1
}

$targets = @()
if ($Files.Count -gt 0) {
    foreach ($f in $Files) {
        $p = Join-Path $root.FullName $f
        $item = Get-Item -LiteralPath $p -ErrorAction SilentlyContinue
        if (-not $item) { Write-Host "[ERROR] not found: $f"; continue }
        $targets += $item
    }
} else {
    $targets = @(Get-ChildItem -LiteralPath $root.FullName)
}
if ($targets.Count -eq 0) { Write-Host "No targets."; exit 1 }

$plan = Get-RenamePlan -Items $targets -Substring $Substring
$exitCode = Invoke-RenamePlan -Plan $plan -Dir $root.FullName -DryRun:$DryRun -LogFile $LogFile
exit $exitCode