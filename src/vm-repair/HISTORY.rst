
Release History
===============

0.4.10
++++++
Support for hosting repair vm in existing resource group and fixing existing resource group logic 

0.4.9
++++++
Fix for encrypted vm's auto unlock feature 

0.4.8
++++++
Fix for encrypted vm's and fixing test cases

0.4.7
++++++
Setting subscription account for reset-nic

0.4.6
++++++
Updating the fetch_repair_vm to use the small letters in the query instead of capital letters

0.4.5
++++++
Improve az vm repair reset-nic command to use subnet list available ips command

0.4.4
++++++
Add az vm repair reset-nic command

0.4.3
++++++
Adding a new distro option for creating the recovery VM, adding the detect for gen2 Linux machine and create a gen2 recovery VM

0.4.2
++++++
Linux only: Fixing duplicated UUID issue. Data disk gets attached only after VM got created.

0.4.1
++++++
Fixing bug in preview parameter

0.4.0
++++++
Fixing issue in disk copy, removing floating point in disk name.

0.3.9
++++++
Add support for preview flag and fix Gen2 bug

0.3.8
++++++
Add support for optional public IP 

0.3.6
++++++
Add support for ALAR2 which requires cloud-init script to prepare the recovery VM with a
build environment for Rust.

0.3.5
++++++

Add support for nested VMs
