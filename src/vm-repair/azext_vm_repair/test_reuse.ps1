# Define the resource group and VMs
$problemRG = "CROWDSTRIKE_RESOURCE";
$repairGroup="repair_crowdstrike_group"
$repairVm="ReuseRescueVM2"
$problemVm="VMSCentralUS"
$subid="88fd8cb2-8248-499e-9a2d-4929a4b0133c"
$repairVmId="/subscriptions/$subid/resourceGroups/$repairGroup/providers/Microsoft.Compute/virtualMachines/$repairVm"

$vms=@("Zone3Trusted", "Zone3", "VMZone1StandardE", "TrustedStandardNoZone", "StandardNoZone")

az vm repair create -g $problemRG -n $problemVm --repair-group-name $repairGroup --repair-vm-name $repairVm --repair-username "haideragha123" --repair-password "Pssword@12345" --yes --verbose
az vm repair run -g $problemRG -n $problemVm --run-id win-crowdstrike-fix-bootloop --run-on-repair --verbose
az vm repair restore -g $problemRG -n $problemVm --repair-vm-id $repairVmId --verbose

foreach ($vm in $vms) {

    az vm repair reuse -g problemRG -n $vm --repair-group-name $repairGroup --repair-vm-name $repairVm --verbose
    az vm repair run -g $repairGroup -n $repairVm --run-id win-crowdstrike-fix-bootloop --verbose
    az vm repair restore -g problemRG -n $vm --repair-vm-id $repairVmId --verbose

}
