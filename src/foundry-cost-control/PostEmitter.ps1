# Replaces 2026-09-15-preview with 2026-07-15-preview in azext_foundry_cost_control
# and its subfolders, excluding azext_foundry_cost_control\tests.
# Run from Windows Command Prompt:
# powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\PostEmitter.ps1

$ErrorActionPreference = 'Stop'

$oldValue = [System.Text.Encoding]::ASCII.GetBytes('2026-09-15-preview')
$newValue = [System.Text.Encoding]::ASCII.GetBytes('2026-07-15-preview')
$targetDirectory = Join-Path $PSScriptRoot 'azext_foundry_cost_control'
$excludedDirectory = [System.IO.Path]::GetFullPath(
    (Join-Path $targetDirectory 'tests')
).TrimEnd('\') + '\'
$updatedFileCount = 0
$replacementCount = 0

Get-ChildItem -LiteralPath $targetDirectory -File -Recurse | ForEach-Object {
    $filePath = [System.IO.Path]::GetFullPath($_.FullName)
    if ($filePath.StartsWith($excludedDirectory, [System.StringComparison]::OrdinalIgnoreCase)) {
        return
    }

    $content = [System.IO.File]::ReadAllBytes($filePath)
    $fileReplacementCount = 0

    for ($index = 0; $index -le $content.Length - $oldValue.Length; $index++) {
        $matches = $true
        for ($offset = 0; $offset -lt $oldValue.Length; $offset++) {
            if ($content[$index + $offset] -ne $oldValue[$offset]) {
                $matches = $false
                break
            }
        }

        if ($matches) {
            [System.Array]::Copy($newValue, 0, $content, $index, $newValue.Length)
            $fileReplacementCount++
            $index += $oldValue.Length - 1
        }
    }

    if ($fileReplacementCount -gt 0) {
        [System.IO.File]::WriteAllBytes($filePath, $content)
        $updatedFileCount++
        $replacementCount += $fileReplacementCount
        Write-Host "Updated: $filePath ($fileReplacementCount replacement(s))"
    }
}

Write-Host "Complete: $replacementCount replacement(s) in $updatedFileCount file(s)."
