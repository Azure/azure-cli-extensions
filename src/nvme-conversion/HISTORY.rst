.. :changelog:

Release History
===============

1.0.0b1
++++++
* Initial preview release
* Convert VMs between SCSI and NVMe disk controllers
* Pre-flight validation checks (SKU, OS, generation, ADE)
* OS preparation for Windows (stornvme driver) and Linux (initrd, fstab, io_timeout)
* Dry-run mode for Linux VMs
* Fallback udev rules when azure-vm-utils is not installed
* Auto-detect controller type; reuse current VM size if compatible
