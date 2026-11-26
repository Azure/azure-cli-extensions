.. :changelog:

Release History
===============

1.0.0b1
++++++
* Identify Linux kernels from installed package and boot references; ignore module-only directories without skipping genuine missing boot images or changing check/fix/dry-run behavior.
* Reject incomplete or failed guest preparation; verify NVMe/Hyper-V PCI modules per installed Linux kernel and stornvme/vpci across Windows ControlSets.
* Await Windows driver fixes, reject Windows dry-run before mutation, and require confirmed VM deallocation before disk/controller writes.
* Correct fallback udev dollar escaping and multi-letter SCSI device UUID resolution; preserve fstab on unresolved entries.
* Refuse NVMe for OS/data-disk ADE and unknown encryption inventory; return diagnostic encryption inventory.
* Fix RHEL 7 standalone EFI timeout readiness and regeneration when GRUB defaults already contain the required value.
* Initial preview release
* Convert VMs between SCSI and NVMe disk controllers
* Pre-flight validation checks (SKU, OS, generation, ADE)
* OS preparation for Windows (stornvme/vpci drivers) and Linux (initrd, fstab, io_timeout)
* Dry-run mode for Linux VMs
* Fallback udev rules when azure-vm-utils is not installed
* Auto-detect controller type; reuse current VM size if compatible
