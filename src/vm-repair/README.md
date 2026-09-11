# Azure CLI VM Repair Extension #
This is an extension for repairing VMs. Usually this is used to repair VMs that cannot boot by copying the 
OS Disk to a separate repair VM copy and run [repair scripts](https://github.com/Azure/repair-script-library) against it. 
VM Repair can also run repair scripts against the source VM itself.
You can also create then run your own custom repair scripts, seen in the `--custom-script-file` parameter in the `az vm repair run` command. 

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vm-repair
```

### Sample Commands ###
Create repair VM command
```
az vm repair create -g MyResourceGroup -n myVM --verbose
```
Run a repair script on the new repair VM
```
az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id win-hello-world --run-on-repair --verbose
```
Restore the now fixed copied OS disk from the repair VM to the original VM
```
az vm repair restore -g MyResourceGroup -n myVM --verbose
```

### Platform-migration scenarios ###
Moving a VM to a size that uses an NVMe disk controller requires the guest OS to be able to boot from
that controller. When it cannot, the VM stops booting after the size change: `INACCESSIBLE_BOOT_DEVICE`
(`0x7B`) on Windows, or a dracut emergency shell on Linux. The fault is inside the guest OS disk, so it
is inspected, and repaired where a repair exists, by attaching that disk to a repair VM.

The table below lists only what is available today. Combinations that are not listed are not supported.

| Scenario | OS | Run ID | Status |
|---|---|---|---|
| NVMe boot readiness detection (read-only) | Windows | `win-detect-nvme-readiness` | Available |
| NVMe boot readiness detection (read-only) | Linux | `linux-detect-nvme-readiness` | Available |
| NVMe boot-driver recovery | Windows | — | Not available yet |
| NVMe boot-driver recovery | Linux | — | Not available yet |

Both detectors run against the source VM's OS disk attached to a repair VM, so they require
`--run-on-repair`. Neither one modifies the attached source OS disk. Both write a log and an evidence
bundle on the repair VM itself, under the Public desktop on Windows and under `/tmp` on Linux.

```
az vm repair create -g MyResourceGroup -n MyBrokenVM --verbose
az vm repair run -g MyResourceGroup -n MyBrokenVM --run-id win-detect-nvme-readiness --run-on-repair --verbose
```

When the source VM uses the NVMe disk controller, `az vm repair create` pins the repair VM to SCSI if
the repair VM size supports it, so that repair scripts which select disks by the SCSI model string can
still see the attached OS disk. For any other source VM the platform default for the repair VM size is
used. `--disk-controller-type` overrides the selection in both cases.
