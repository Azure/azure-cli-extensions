# Define the resource group and VMs
$resourceGroup = "CROWDSTRIKE_RESOURCE";
$repairGroup="repair_crowdstrike_group"
$repairVm="ReuseRescueVM2"
$problemVm="VMSCentralUS"
$subid="88fd8cb2-8248-499e-9a2d-4929a4b0133c"
$repairVmId="/subscriptions/$subid/resourceGroups/$repairGroup/providers/Microsoft.Compute/virtualMachines/$repairVm"

$vms=@("Zone3Trusted", "Zone3", "VMZone1StandardE", "TrustedStandardNoZone", "StandardNoZone")

az vm repair create -g $resourceGroup -n $problemVm --repair-group-name $repairGroup --repair-vm-name $repairVm --repair-username "haideragha123" --repair-password "Pssword@12345" --yes --verbose
az vm repair run -g $resourceGroup -n $problemVm --run-id win-crowdstrike-fix-bootloop --run-on-repair --verbose
az vm repair restore -g $resourceGroup -n $problemVm --repair-vm-id $repairVmId --verbose

foreach ($vm in $vms) {

    az vm repair reuse -g $resourceGroup -n $vm --repair-group-name $repairGroup --repair-vm-name $repairVm --verbose
    az vm repair run -g $repairGroup -n $repairVm --run-id win-crowdstrike-fix-bootloop --verbose
    az vm repair restore -g $resourceGroup -n $problemVm --repair-vm-id $repairVmId --verbose

}
