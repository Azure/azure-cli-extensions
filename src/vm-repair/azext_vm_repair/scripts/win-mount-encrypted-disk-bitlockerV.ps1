param (
    [Parameter(Mandatory=$false)][string]$bitlockerkey
)

Write-Output "Bringing disks online if they are already offline"
Get-Disk | where {$_.OperationalStatus -ne 'Online'} | Set-Disk -IsOffline $false

Write-Output "Finding volume with 'Bek Volume' file system label"
$bekVolume = Get-Volume | Where-Object {$_.FileSystemLabel -eq 'Bek Volume'}
if ($bekVolume)
{
    Write-Output "BEK volume UniqueId: $($bekVolume.UniqueId)"
}
elseif ($bitlockerkey)
{
    Write-Output "No BEK volume found but BitLocker key provided"
}
else {
    Write-Output "No volume found with 'Bek Volume' file system label"
    Exit 1
}

$bekFilePath = $null
$bekPartitionDriveLetter = 'K'
if ($bekVolume) {
    Write-Output "Setting BEK partition drive letter to $bekPartitionDriveLetter"
    $bekVolume | Get-Partition | Set-Partition -NewDriveLetter $bekPartitionDriveLetter
    $bekPartition = $bekVolume | Get-Partition
    if ($bekPartition.DriveLetter -eq $bekPartitionDriveLetter)
    {
        Write-Output "BEK partition drive letter successfully set to $($bekPartition.DriveLetter)"
    }
    else {
        Write-Output "Failed to set BEK partition drive letter to $bekPartitionDriveLetter"
        Exit 1
    }

    Write-Output "Finding *.BEK file on drive $($bekPartition.DriveLetter)"
    $bekFile = Get-ChildItem -Path "$($bekPartition.DriveLetter):\*.BEK" -Hidden
    if ($bekFile)
    {
        $bekFilePath = $bekFile.FullName
        Write-Output "Found $bekFilePath"
    }
    else {
        Write-Output "No *.BEK file found on drive $($bekPartition.DriveLetter)"
        Exit 1
    }
}

Write-Output "Finding encrypted volume"
$encryptedVolume = Get-BitLockerVolume | Where-Object {($_.VolumeStatus -eq 'FullyEncrypted' -or $_.VolumeStatus -eq $null) -and $_.LockStatus -eq 'Locked' }
if ($encryptedVolume)
{

    $driveLetter = $encryptedVolume.MountPoint
    Write-Output "Found encrypted volume with drive letter $driveLetter"
    Write-Output "Unlocking encrypted drive $driveLetter"
    if ($bitlockerkey)
    {
        $result = Unlock-BitLocker -MountPoint $driveLetter -RecoveryPassword $bitlockerkey
    }
    elseif ($bekFilePath)
    {
        $result = Unlock-BitLocker -MountPoint $driveLetter -RecoveryKeyPath $bekFilePath
    }
    else
    {
        Write-Output "No BitLocker key or BEK file provided"
        Exit 1
    }
    if ($result)
    {
        if ($result.LockStatus -eq 'Unlocked')
        {
            Write-Output "Successfully unlocked encrypted drive $driveLetter"
            Exit 0
        }
        else {
            Write-Output "Failed to unlock encrypted drive $driveLetter"
            Exit 1
        }
    }
    else {
        Write-Output "Failed to unlock encrypted drive $driveLetter"
        Exit 1
    }
}
else {
    Write-Output "No encrypted volume found."
    Exit 1
}