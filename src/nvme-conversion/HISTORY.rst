.. :changelog:

Release History
===============

1.0.0b1
++++++
* Refuse NVMe for OS/data-disk ADE and unknown encryption inventory; return source-VM eligibility metadata for offline recovery.
* Fix RHEL 7 standalone EFI timeout readiness and regeneration when GRUB defaults already contain the required value.
* Initial preview release
* Convert VMs between SCSI and NVMe disk controllers
* Pre-flight validation checks (SKU, OS, generation, ADE)
* OS preparation for Windows (stornvme driver) and Linux (initrd, fstab, io_timeout)
* Dry-run mode for Linux VMs
* Fallback udev rules when azure-vm-utils is not installed
* Auto-detect controller type; reuse current VM size if compatible
