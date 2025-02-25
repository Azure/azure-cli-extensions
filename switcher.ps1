param (
    [string]$switch
)

$folderPath = '.\src\workload-operations'

if ($switch -eq 'microsoft.edge') {
    Get-ChildItem -Path $folderPath -Recurse -File -Filter *.py | ForEach-Object {
        (Get-Content $_.FullName) -creplace 'private\\.edge', 'microsoft.edge' | Set-Content $_.FullName
    }
} elseif ($switch -eq 'private.edge') {
    Get-ChildItem -Path $folderPath -Recurse -File -Filter *.py | ForEach-Object {
        (Get-Content $_.FullName) -creplace 'microsoft\\.edge', 'private.edge' | Set-Content $_.FullName
    }
} else {
    Write-Host "Invalid method. Choose either 'microsoft.edge' or 'private.edge'."
}
