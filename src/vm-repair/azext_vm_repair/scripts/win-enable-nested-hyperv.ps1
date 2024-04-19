Param([Parameter(Mandatory=$false)][string]$gen)

. .\src\windows\common\setup\init.ps1

Log-Info 'Running Script Enable-NestedHyperV'

$scriptStartTime = get-date -f yyyyMMddHHmmss
$scriptPath = split-path -path $MyInvocation.MyCommand.Path -parent
$scriptName = (split-path -path $MyInvocation.MyCommand.Path -leaf).Split('.')[0]

$logFile = "$env:PUBLIC\Desktop\$($scriptName).log"
$scriptStartTime | out-file -FilePath $logFile -Append

$nestedGuestVmName = 'ProblemVM'
$batchFile = "$env:allusersprofile\Microsoft\Windows\Start Menu\Programs\StartUp\RunHyperVManagerAndVMConnect.cmd"
$batchFileContents = @"
start $env:windir\System32\mmc.exe $env:windir\System32\virtmgmt.msc
start $env:windir\System32\vmconnect.exe localhost $nestedGuestVmName
"@

$features = get-windowsfeature -ErrorAction Stop
$hyperv = $features | where Name -eq 'Hyper-V'
$hypervTools = $features | where Name -eq 'Hyper-V-Tools'
$hypervPowerShell = $features | where Name -eq 'Hyper-V-Powershell'
$dhcp = $features | where Name -eq 'DHCP'
$rsatDhcp = $features | where Name -eq 'RSAT-DHCP'

if ($hyperv.Installed -and $hypervTools.Installed -and $hypervPowerShell.Installed)
{
    Log-Info 'START: Creating nested guest VM' | out-file -FilePath $logFile -Append
    # Sets "Do not start Server Manager automatically at logon"
    $return = New-ItemProperty -Path HKLM:\Software\Microsoft\ServerManager -Name DoNotOpenServerManagerAtLogon -PropertyType DWORD -Value 1 -force -ErrorAction SilentlyContinue
    $return = New-ItemProperty -Path HKLM:\Software\Microsoft\ServerManager\Oobe -Name DoNotOpenInitialConfigurationTasksAtLogon -PropertyType DWORD -Value 1 -force -ErrorAction SilentlyContinue

    try {

        # Configure NAT so nested guest has external network connectivity
        # See also https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/nested-virtualization#networking-options
        $switch = Get-VMSwitch -Name Internal -SwitchType Internal -ErrorAction SilentlyContinue | select -first 1
        if (!$switch)
        {
            $switch = New-VMSwitch -Name Internal -SwitchType Internal -ErrorAction Stop
            Log-Info 'New VMSwitch Successfully created' | out-file -FilePath $logFile -Append
        }
        $adapter = Get-NetAdapter -Name 'vEthernet (Internal)' -ErrorAction Stop

        $ip = get-netipaddress -IPAddress 192.168.0.1 -ErrorAction SilentlyContinue | select -first 1
        if (!$ip)
        {
            $return = New-NetIPAddress -IPAddress 192.168.0.1 -PrefixLength 24 -InterfaceIndex $adapter.ifIndex -ErrorAction Stop
            Log-Info 'New NetIPAddress Successfully created' | out-file -FilePath $logFile -Append
        }

        $nat = Get-NetNat -Name InternalNAT -ErrorAction SilentlyContinue | select -first 1
        if (!$nat)
        {
            $return = New-NetNat -Name InternalNAT -InternalIPInterfaceAddressPrefix 192.168.0.0/24 -ErrorAction Stop
            Log-Info 'New NetNat Successfully created' | out-file -FilePath $logFile -Append
        }

        # Configure DHCP server service so nested guest can get an IP from DHCP and will use 168.63.129.16 for DNS and 192.168.0.1 as default gateway
        if ($dhcp.Installed -eq $false -or $rsatDhcp.Installed -eq $false)
        {
            $return = Install-WindowsFeature -Name DHCP -IncludeManagementTools -ErrorAction Stop
            Log-Info 'New NetIPAddress Successfully created' | out-file -FilePath $logFile -Append
        }
        $scope = Get-DhcpServerv4Scope -ErrorAction SilentlyContinue | where Name -eq Scope1 | select -first 1
        if (!$scope)
        {
            $return = Add-DhcpServerV4Scope -Name Scope1 -StartRange 192.168.0.100 -EndRange 192.168.0.200 -SubnetMask 255.255.255.0 -ErrorAction Stop
        }
        $return = Set-DhcpServerv4OptionValue -DnsServer 168.63.129.16 -Router 192.168.0.1 -ErrorAction Stop

        # Create the nested guest VM
        if (!$gen -or ($gen -eq 1)) {
            Log-Info 'Creating Gen1 VM with 4GB memory' | Out-File -FilePath $logFile -Append
            $return = New-VM -Name $nestedGuestVmName -MemoryStartupBytes 4GB -NoVHD -BootDevice IDE -Generation 1 -ErrorAction Stop
        }
        else {
            Log-Info "Creating Gen$($gen) VM with 4GB memory" | Out-File -FilePath $logFile -Append
            $return = New-VM -Name $nestedGuestVmName -MemoryStartupBytes 4GB -NoVHD -Generation $gen -ErrorAction Stop
        }
        $return = set-vm -name $nestedGuestVmName -ProcessorCount 2 -CheckpointType Disabled -ErrorAction Stop
        $disk = get-disk -ErrorAction Stop | where {$_.FriendlyName -eq 'Msft Virtual Disk'}
        $return = $disk | set-disk -IsOffline $true -ErrorAction Stop

        if (!$gen -or ($gen -eq 1)) {
            Log-Info "Gen1: Adding hard drive to IDE controller" | Out-File -FilePath $logFile -Append
            $return = $disk | Add-VMHardDiskDrive -VMName $nestedGuestVmName -ErrorAction Stop            
        }
        else {
            Log-Info "Gen$($gen): Adding hard drive to SCSI controller" | Out-File -FilePath $logFile -Append
            $return = $disk | Add-VMHardDiskDrive -VMName $nestedGuestVmName -ControllerType SCSI -ControllerNumber 0 -ErrorAction Stop
            Log-Info "Gen$($gen): Modifying firmware boot order (we do not need to network boot)" | Out-File -FilePath $logFile -Append
            $return = Set-VMFirmware $nestedGuestVmName -FirstBootDevice ((Get-VMFirmware $nestedGuestVmName).BootOrder | Where-Object { $_.BootType -eq "Drive" })[0]
        }

        $return = $switch | Connect-VMNetworkAdapter -VMName $nestedGuestVmName -ErrorAction Stop
        $return = start-vm -Name $nestedGuestVmName -ErrorAction Stop
        $nestedGuestVmState = (get-vm -Name $nestedGuestVmName -ErrorAction Stop).State

        # Create a batch file in the all users startup folder so both Hyper-V Manager and VMConnect run automatically at logon.
        $return = $batchFileContents | out-file -FilePath $batchFile -Force -Encoding Default
        $return = copy-item -path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Administrative Tools\Hyper-V Manager.lnk" -Destination "C:\Users\Public\Desktop"
        # Suppress the prompt for "Do you want to allow your PC to be discoverable by other PCs and devices on this network"
        $return = new-item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Network\NewNetworkWindowOff" -Force
        "END: Creating nested guest VM" | out-file -FilePath $logFile -Append
        $return.ExitCode
        write-host $return.ExitCode
        return $STATUS_SUCCESS
    }
    catch {
        throw $_
        return $STATUS_ERROR
    }

    # Returns the nested guest VM status to the calling script - "Running" if all went well.
    return $nestedGuestVmState
}
else
{
    "START: Installing Hyper-V" | out-file -FilePath $logFile -Append
    try {
        # Install Hyper-V role. The required restart is handled in the calling script, not this script, to make sure that this script cleanly returns the Hyper-V role install status to the calling script.
        $return = install-windowsfeature -name Hyper-V -IncludeManagementTools -ErrorAction Stop
    }
    catch {
        throw $_
        return $STATUS_ERROR
    }
    "END: Installing Hyper-V" | out-file -FilePath $logFile -Append
    $return.ExitCode
    write-host $return.ExitCode
    return $STATUS_SUCCESS
}

$scriptEndTime = get-date -f yyyyMMddHHmmss
$scriptEndTime | out-file -FilePath $logFile -Append