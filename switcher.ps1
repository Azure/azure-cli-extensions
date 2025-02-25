
param (
    [string]$switch
)

# Define the root folder and blacklist folders
# Define the root folder and blacklist folders
$rootFolder = "src\workload-operations\azext_workload_operations\aaz\latest\workload_operations" # Add your root folder path here
$blacklist = @("src\workload-operations\azext_workload_operations\aaz\latest\workload_operations\configuration") # Add your blacklist folder paths here

# Get all files in the folder and subfolders, excluding blacklisted folders
$files = Get-ChildItem -Path $rootFolder -Recurse -File | Where-Object {
    $blacklist -notcontains $_.DirectoryName
}

foreach ($file in $files) {
    # Read the file content
    $content = Get-Content -Path $file.FullName -Raw

    # Replace text based on the switch
    if ($switch -eq "microsoft.edge") {
        $content = $content -replace "(?i)microsoft\.edge", "private.edge"
    } elseif ($switch -eq "private.edge") {
        $content = $content -replace "(?i)private\.edge", "microsoft.edge"
    }

    # Write the updated content back to the file without adding extra newlines
    [System.IO.File]::WriteAllText($file.FullName, $content)
}
