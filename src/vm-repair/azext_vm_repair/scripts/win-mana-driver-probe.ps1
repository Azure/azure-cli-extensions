# Read-only MANA readiness probe run in the guest by az vm repair through Run Command.
# Takes no input, changes nothing, and prints one machine-readable line:
#   VMREPAIR_MANA_PROBE hardware=<mana|mellanox|none|unknown> driver=<present|missing|unknown>
# hardware: accelerated-networking virtual function present as a PCI device (MANA VEN_1414&DEV_00BA, Mellanox VEN_15B3).
# driver:   on MANA hardware, whether a "Microsoft Azure Network Adapter" network adapter exists. A present MANA
#           device without that adapter means the driver is missing. Elsewhere it cannot be determined this way.

$ErrorActionPreference = 'Stop'
$hardware = 'unknown'
$driver = 'unknown'

try {
    $pciInstanceIds = @(Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like 'PCI\*' } | ForEach-Object { $_.InstanceId })
    if ($pciInstanceIds | Where-Object { $_ -match '^PCI\\VEN_1414&DEV_00BA&' }) {
        $hardware = 'mana'
    }
    elseif ($pciInstanceIds | Where-Object { $_ -match '^PCI\\VEN_15B3&' }) {
        $hardware = 'mellanox'
    }
    else {
        $hardware = 'none'
    }
}
catch {
    $hardware = 'unknown'
}

if ($hardware -eq 'mana') {
    try {
        $manaAdapters = @(Get-NetAdapter | Where-Object { $_.InterfaceDescription -like 'Microsoft Azure Network Adapter*' })
        if ($manaAdapters.Count -gt 0) {
            $driver = 'present'
        }
        else {
            $driver = 'missing'
        }
    }
    catch {
        $driver = 'unknown'
    }
}

Write-Output ('VMREPAIR_MANA_PROBE hardware={0} driver={1}' -f $hardware, $driver)
exit 0
