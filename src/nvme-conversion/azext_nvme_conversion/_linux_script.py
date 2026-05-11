# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Embedded Linux bash script for NVMe readiness checks.

The script is sent to VMs via Azure RunCommand and executes remotely.
It never runs locally. See _linux_checks.py for the Python wrapper.
"""


def get_linux_check_script():
    """Return the Linux NVMe readiness check bash script.

    This script is sent to the VM via RunCommand. It checks:
    - azure-vm-utils presence (recommended for NVMe symlinks and io_timeout)
    - NVMe driver in initrd/initramfs (or built into kernel)
    - nvme_core.io_timeout grub parameter
    - /etc/fstab for deprecated device names (/dev/sd*, /dev/disk/azure/scsi*)

    Supports: Ubuntu, Debian, RHEL, CentOS, Rocky, AlmaLinux, SLES, OL, Azure Linux, Mariner
    Flags: -fix (apply fixes), -dryrun (stage changes in /tmp/nvme-conversion-dryrun/)
    """
    return _LINUX_SCRIPT


_LINUX_SCRIPT = r"""#!/bin/bash

# Set default values
fix=false
dry_run=false
distro=""

# Staging directory for dry-run mode
staging_dir=""

setup_dryrun() {
    staging_dir="/tmp/nvme-conversion-dryrun"
    rm -rf "$staging_dir"
    mkdir -p "$staging_dir/original" "$staging_dir/modified" "$staging_dir/diffs"
    echo "$(hostname)" > "$staging_dir/hostname"
    echo "$distro" > "$staging_dir/distro"
    uname -r > "$staging_dir/kernel"
    echo "[INFO] Dry-run mode: staging changes in $staging_dir"
}

# Function to display usage
usage() {
    echo "Usage: $0 [-fix] [-dryrun]"
    exit 1
}

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -fix)
            fix=true
            ;;
        -dryrun)
            dry_run=true
            fix=true
            ;;
        *)
            usage
            ;;
    esac
    shift
done

# Determine the Linux distribution
if [ -f /etc/os-release ]; then
    source /etc/os-release
    distro="$ID"
elif [ -f /etc/debian_version ]; then
    distro="debian"
elif [ -f /etc/SuSE-release ]; then
    distro="suse"
elif [ -f /etc/redhat-release ]; then
    distro="redhat"
elif [ -f /etc/centos-release ]; then
    distro="centos"
elif [ -f /etc/rocky-release ]; then
    distro="rocky"
else
    echo "[ERROR] Unsupported distribution."
    exit 1
fi
echo "[INFO] Operating system detected: $distro"

# Setup dry-run staging if enabled
if $dry_run && $fix; then
    setup_dryrun
fi

# Function to check if azure-vm-utils is installed
check_azure_vm_utils() {
    echo "[INFO] Checking for azure-vm-utils..."

    if command -v azure-nvme-id &>/dev/null; then
        echo "[INFO] azure-vm-utils is installed (azure-nvme-id found)."
        if [ -f /etc/udev/rules.d/80-azure-disk.rules ] || [ -f /lib/udev/rules.d/80-azure-disk.rules ] || [ -f /usr/lib/udev/rules.d/80-azure-disk.rules ]; then
            echo "[INFO] 80-azure-disk.rules is present. NVMe disk symlinks and io_timeout will be managed by udev."
        else
            echo "[WARNING] azure-nvme-id found but 80-azure-disk.rules is missing. Udev symlinks may not work after conversion."
        fi
    else
        echo "[WARNING] azure-vm-utils is not installed."
        echo "[WARNING] After conversion, /dev/disk/azure/ symlinks for NVMe disks may not be available."
        echo "[WARNING] Install azure-vm-utils from https://github.com/Azure/azure-vm-utils for best NVMe experience."
        if $fix; then
            _install_fallback_udev_rules
        else
            echo "[WARNING] Use --fix-os to install a fallback udev rule for basic NVMe symlinks and io_timeout."
        fi
    fi
}

# Fallback udev rule for NVMe disks when azure-vm-utils is not available.
# Provides: io_timeout=240s, /dev/disk/azure/root, /dev/disk/azure/data/by-lun/N
# Does NOT provide: by-name, by-serial, by-index (those require azure-nvme-id binary)
# Named 99- so that 80-azure-disk.rules takes precedence if azure-vm-utils is later installed.
_FALLBACK_UDEV_RULE='# Fallback Azure NVMe udev rules (installed by az nvme-conversion)
# Remove this file after installing azure-vm-utils (which provides 80-azure-disk.rules)
ACTION!="add|change", GOTO="azure_nvme_fallback_end"
SUBSYSTEM!="block", GOTO="azure_nvme_fallback_end"
KERNEL!="nvme*", GOTO="azure_nvme_fallback_end"
ENV{ID_MODEL}!="MSFT NVMe Accelerator v1.0", GOTO="azure_nvme_fallback_end"

# Set io_timeout to 240 seconds for remote NVMe disks
ENV{DEVTYPE}=="disk", ATTRS{nsid}=="?*", ATTR{queue/io_timeout}="240000"

# OS disk: namespace ID 1
KERNEL=="nvme*[0-9]n1", ENV{DEVTYPE}=="disk", SYMLINK+="disk/azure/root"
KERNEL=="nvme*[0-9]n1p[0-9]*", ENV{DEVTYPE}=="partition", SYMLINK+="disk/azure/root-part%n"

# Data disks: namespace ID 2+ maps to LUN = nsid - 2
KERNEL=="nvme*[0-9]n*[0-9]", ENV{DEVTYPE}=="disk", ATTRS{nsid}!="1", PROGRAM="/bin/sh -ec '\''echo $(($(cat /sys/class/block/%k/nsid) - 2))'\''", SYMLINK+="disk/azure/data/by-lun/%c"
KERNEL=="nvme*[0-9]n*[0-9]p[0-9]*", ENV{DEVTYPE}=="partition", ATTRS{nsid}!="1", PROGRAM="/bin/sh -ec '\''echo $(($(cat /sys/class/block/$(echo %k | sed s/p[0-9]*$//)/nsid) - 2))'\''", SYMLINK+="disk/azure/data/by-lun/%c-part%n"

LABEL="azure_nvme_fallback_end"'

_install_fallback_udev_rules() {
    local _target="/etc/udev/rules.d/99-azure-nvme-fallback.rules"

    if [ -f "$_target" ]; then
        echo "[INFO] Fallback udev rule already installed at $_target"
        return
    fi

    if $dry_run; then
        echo "[DRYRUN] Would install fallback udev rule at $_target"
        echo "$_FALLBACK_UDEV_RULE" > "$staging_dir/modified/99-azure-nvme-fallback.rules"
        return
    fi

    echo "[INFO] Installing fallback NVMe udev rule at $_target"
    echo "$_FALLBACK_UDEV_RULE" > "$_target"
    udevadm control --reload-rules 2>/dev/null || true
    echo "[INFO] Fallback udev rule installed. Provides:"
    echo "[INFO]   - io_timeout=240s for NVMe remote disks"
    echo "[INFO]   - /dev/disk/azure/root symlink"
    echo "[INFO]   - /dev/disk/azure/data/by-lun/N symlinks"
    echo "[INFO]   Note: by-name/by-serial/by-index require azure-vm-utils"
}

# Function to check if NVMe driver is in initrd/initramfs or built into the kernel
check_nvme_driver() {
    echo "[INFO] Checking if NVMe driver is available for boot..."

    # Check if nvme is compiled directly into the kernel (built-in)
    if grep -qw nvme "/lib/modules/$(uname -r)/modules.builtin" 2>/dev/null; then
        echo "[INFO] NVMe driver is built into the kernel. No initramfs entry needed."
        if $dry_run && $fix; then
            echo "[DRYRUN] NVMe driver is built-in (kernel $(uname -r)). No initramfs or dracut changes needed."
            echo "nvme_builtin=true" > "$staging_dir/modified/nvme-driver-status.txt"
            echo "kernel=$(uname -r)" >> "$staging_dir/modified/nvme-driver-status.txt"
            grep -w nvme "/lib/modules/$(uname -r)/modules.builtin" >> "$staging_dir/modified/nvme-driver-status.txt"
        fi
        return 0
    fi

    echo "[INFO] NVMe is not built-in. Checking initrd/initramfs..."
    case "$distro" in
        ubuntu|debian)
            _initramfs_ok=true
            if ! lsinitramfs /boot/initrd.img-* 2>/dev/null | grep -q nvme; then
                echo "[WARNING] NVMe driver not found in initrd/initramfs."
                _initramfs_ok=false
            fi
            if ! lsinitramfs /boot/initrd.img-* 2>/dev/null | grep -qE 'hv_pci|pci.hyperv'; then
                echo "[WARNING] pci-hyperv/hv_pci driver not found in initrd/initramfs (required for Azure NVMe)."
                _initramfs_ok=false
            fi
            if $_initramfs_ok; then
                echo "[INFO] NVMe driver found in initrd/initramfs."
                if $dry_run && $fix; then
                    echo "[DRYRUN] NVMe and pci-hyperv drivers already in initramfs. No changes needed."
                    echo "nvme_in_initramfs=true" > "$staging_dir/modified/nvme-driver-status.txt"
                    echo "kernel=$(uname -r)" >> "$staging_dir/modified/nvme-driver-status.txt"
                fi
            else
                if modinfo nvme &>/dev/null; then
                    echo "[INFO] NVMe module exists on disk."
                fi
                if $fix; then
                    if $dry_run; then
                        echo "[DRYRUN] Would run: update-initramfs -u -k all"
                        echo "update-initramfs -u -k all" > "$staging_dir/modified/initramfs-commands.txt"
                    else
                        echo "[INFO] Adding NVMe/pci-hyperv drivers to initrd/initramfs..."
                        update-initramfs -u -k all
                        if lsinitramfs /boot/initrd.img-* | grep -q nvme; then
                            echo "[INFO] NVMe driver added successfully."
                        else
                            echo "[ERROR] Failed to add NVMe driver to initrd/initramfs."
                        fi
                    fi
                else
                    echo "[ERROR] NVMe driver not found in initrd/initramfs."
                fi
            fi
            ;;
        redhat|rhel|centos|rocky|almalinux|azurelinux|mariner|suse|sles|ol)
            # Check ALL installed initramfs images, not just the running kernel
            _nvme_missing=false
            for _img in /boot/initramfs-*.img; do
                [ -f "$_img" ] || continue
                [[ "$_img" == *kdump* ]] && continue
                [[ "$_img" == *rescue* ]] && continue
                if ! lsinitrd "$_img" 2>/dev/null | grep -q nvme; then
                    echo "[WARNING] NVMe driver not found in $_img"
                    _nvme_missing=true
                fi
                if ! lsinitrd "$_img" 2>/dev/null | grep -qE 'hv_pci|pci.hyperv'; then
                    echo "[WARNING] pci-hyperv/hv_pci driver not found in $_img (required for Azure NVMe)"
                    _nvme_missing=true
                fi
            done
            if ! $_nvme_missing; then
                echo "[INFO] NVMe and pci-hyperv drivers found in initrd/initramfs."
                if $dry_run && $fix; then
                    echo "[DRYRUN] NVMe and pci-hyperv drivers already in all initramfs images. No changes needed."
                    echo "nvme_in_initramfs=true" > "$staging_dir/modified/nvme-driver-status.txt"
                    echo "kernel=$(uname -r)" >> "$staging_dir/modified/nvme-driver-status.txt"
                fi
            else
                if modinfo nvme &>/dev/null; then
                    echo "[INFO] NVMe module exists on disk but is not in all initramfs images."
                fi
                if $fix; then
                    if $dry_run; then
                        echo "[DRYRUN] Would run: dracut -f --regenerate-all (with nvme nvme-core in /etc/dracut.conf.d/nvme.conf)"
                        echo 'add_drivers+=" nvme nvme-core pci-hyperv "' > "$staging_dir/modified/dracut-nvme.conf"
                        echo "dracut -f --regenerate-all" >> "$staging_dir/modified/initramfs-commands.txt"
                    else
                        echo "[INFO] Adding NVMe driver to initrd/initramfs (all kernels)..."
                        mkdir -p /etc/dracut.conf.d
                        echo 'add_drivers+=" nvme nvme-core pci-hyperv "' | tee /etc/dracut.conf.d/nvme.conf > /dev/null
                        dracut -f --regenerate-all
                        _verify_ok=true
                        for _img in /boot/initramfs-*.img; do
                            [ -f "$_img" ] || continue
                            [[ "$_img" == *kdump* ]] && continue
                            [[ "$_img" == *rescue* ]] && continue
                            if ! lsinitrd "$_img" 2>/dev/null | grep -q nvme; then
                                echo "[ERROR] NVMe driver still missing in $_img after rebuild."
                                _verify_ok=false
                            fi
                            if ! lsinitrd "$_img" 2>/dev/null | grep -qE 'hv_pci|pci.hyperv'; then
                                echo "[ERROR] pci-hyperv/hv_pci driver still missing in $_img after rebuild."
                                _verify_ok=false
                            fi
                        done
                        if $_verify_ok; then
                            echo "[INFO] NVMe driver added successfully."
                        else
                            echo "[ERROR] Failed to add NVMe driver to all initramfs images."
                        fi
                    fi
                else
                    echo "[ERROR] NVMe driver not found in initrd/initramfs."
                fi
            fi
            ;;
        *)
            echo "[ERROR] Unsupported distribution for NVMe driver check."
            return 1
            ;;
    esac
}

# Function to check nvme_core.io_timeout parameter
check_nvme_timeout() {
    echo "[INFO] Checking nvme_core.io_timeout parameter..."

    # Build grub file list dynamically for verification
    _grub_check_files="/etc/default/grub"
    if [ -f /boot/grub2/grub.cfg ]; then
        _grub_check_files="$_grub_check_files /boot/grub2/grub.cfg"
    elif [ -f /boot/grub/grub.cfg ]; then
        _grub_check_files="$_grub_check_files /boot/grub/grub.cfg"
    fi

    if grep -q "nvme_core.io_timeout=240" $_grub_check_files 2>/dev/null; then
        echo "[INFO] nvme_core.io_timeout is set to 240."
        if $dry_run && $fix; then
            echo "[DRYRUN] nvme_core.io_timeout already set to 240. No grub changes needed."
            echo "nvme_core_io_timeout=240" > "$staging_dir/modified/nvme-timeout-status.txt"
            echo "status=already_configured" >> "$staging_dir/modified/nvme-timeout-status.txt"
        fi
    elif command -v grubby &>/dev/null && grubby --info=ALL 2>/dev/null | grep -q "nvme_core.io_timeout=240"; then
        echo "[INFO] nvme_core.io_timeout is set to 240 (BLS entries)."
    else
        echo "[WARNING] nvme_core.io_timeout is not set to 240."
        if $fix; then
            if $dry_run; then
                echo "[DRYRUN] Staging grub changes..."
                # Find the grub config file to stage
                local grub_file=""
                if [ -f /etc/default/grub ]; then
                    grub_file="/etc/default/grub"
                fi
                if [ -n "$grub_file" ]; then
                    cp "$grub_file" "$staging_dir/original/grub"
                    cp "$grub_file" "$staging_dir/modified/grub"
                    case "$distro" in
                        ubuntu)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub"
                            ;;
                        debian)
                            sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub"
                            ;;
                        suse|sles|opensuse*)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub"
                            ;;
                        ol|azurelinux|mariner)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub"
                            ;;
                        *)
                            sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub"
                            ;;
                    esac
                    diff -u "$staging_dir/original/grub" "$staging_dir/modified/grub" > "$staging_dir/diffs/grub.diff" 2>&1 || true
                    echo "[DRYRUN] Grub diff staged in $staging_dir/diffs/grub.diff"
                    cat "$staging_dir/diffs/grub.diff"
                    # Check for BLS (BootLoaderSpec) — RHEL 8+, AlmaLinux 8+, OL 8.10+
                    if grep -q "GRUB_ENABLE_BLSCFG=true" "$grub_file" 2>/dev/null; then
                        echo "[INFO] BLS (BootLoaderSpec) is enabled."
                        if command -v grubby &>/dev/null; then
                            echo "[DRYRUN] Would run: grubby --update-kernel=ALL --args=nvme_core.io_timeout=240"
                            echo "bls_enabled=true" >> "$staging_dir/modified/nvme-timeout-status.txt"
                            echo "grubby_available=true" >> "$staging_dir/modified/nvme-timeout-status.txt"
                        else
                            echo "[WARNING] BLS is enabled but grubby is not installed."
                            echo "bls_enabled=true" >> "$staging_dir/modified/nvme-timeout-status.txt"
                            echo "grubby_available=false" >> "$staging_dir/modified/nvme-timeout-status.txt"
                        fi
                    fi
                else
                    echo "[DRYRUN] No grub config found to stage."
                fi
            else
                echo "[INFO] Setting nvme_core.io_timeout to 240..."
                case "$distro" in
                    ubuntu)
                        sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub
                        GRUB_DISABLE_OS_PROBER=true update-grub
                        ;;
                    debian)
                        sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' /etc/default/grub
                        GRUB_DISABLE_OS_PROBER=true update-grub
                        ;;
                    suse|sles|opensuse*)
                        if [ -f /etc/default/grub ]; then
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub
                            GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg
                        else
                            echo "[ERROR] /etc/default/grub not found."
                            return 1
                        fi
                        ;;
                    redhat|rhel|centos|rocky|almalinux)
                        if [ -f /etc/default/grub ]; then
                            sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' /etc/default/grub
                            GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg
                            # Update BLS entries if applicable (RHEL 8+, AlmaLinux 8+)
                            if grep -q "GRUB_ENABLE_BLSCFG=true" /etc/default/grub 2>/dev/null; then
                                if command -v grubby &>/dev/null; then
                                    grubby --update-kernel=ALL --args="nvme_core.io_timeout=240"
                                    echo "[INFO] Updated BLS entries via grubby."
                                fi
                            fi
                        else
                            echo "[ERROR] /etc/default/grub not found."
                            return 1
                        fi
                        ;;
                    ol|azurelinux|mariner)
                        if [ -f /etc/default/grub ]; then
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub
                            GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg
                            # Update BLS entries if applicable (OL 8.10+)
                            if grep -q "GRUB_ENABLE_BLSCFG=true" /etc/default/grub 2>/dev/null; then
                                if command -v grubby &>/dev/null; then
                                    grubby --update-kernel=ALL --args="nvme_core.io_timeout=240"
                                    echo "[INFO] Updated BLS entries via grubby."
                                fi
                            fi
                        else
                            echo "[ERROR] /etc/default/grub not found."
                            return 1
                        fi
                        ;;
                    *)
                        echo "[ERROR] Unsupported distribution for nvme_core.io_timeout fix."
                        return 1
                        ;;
                esac

                if grep -q "nvme_core.io_timeout=240" $_grub_check_files 2>/dev/null; then
                    echo "[INFO] nvme_core.io_timeout set successfully."
                elif command -v grubby &>/dev/null && grubby --info=ALL 2>/dev/null | grep -q "nvme_core.io_timeout=240"; then
                    echo "[INFO] nvme_core.io_timeout set successfully (BLS entries)."
                else
                    echo "[ERROR] Failed to set nvme_core.io_timeout."
                fi
            fi
        else
            echo "[ERROR] nvme_core.io_timeout is not set to 240."
        fi
    fi
}

# Function to check /etc/fstab for deprecated device names
check_fstab() {
    echo "[INFO] Checking /etc/fstab for deprecated device names..."
    # NOTE: /dev/mapper/* (LVM) and PARTUUID= paths survive NVMe conversion
    # because they use UUID-based addressing underneath. Only /dev/sd* and
    # /dev/disk/azure/scsi* paths break when disks move from SCSI to NVMe.
    if grep -Eq '/dev/sd[a-z][0-9]*|/dev/disk/azure/scsi[0-9]*/lun[0-9]*' /etc/fstab; then
        if $fix; then
            echo "[WARNING] /etc/fstab contains deprecated device names."
            if $dry_run; then
                echo "[DRYRUN] Staging fstab changes..."
                cp /etc/fstab "$staging_dir/original/fstab"

                # Build modified fstab in staging directory
                while read -r line; do
                    if [[ "$line" =~ ^[^#] ]]; then
                        device=$(echo "$line" | awk '{print $1}')
                        if [[ "$device" =~ ^/dev/sd[a-z][0-9]*$ ]]; then
                            uuid=$(blkid "$device" | awk -F\" '/UUID=/ {print $2}')
                            if [ -n "$uuid" ]; then
                                newline=$(echo "$line" | sed "s|$device|UUID=$uuid|g")
                                echo "[DRYRUN] Would replace $device with UUID=$uuid"
                                echo "$newline" >> "$staging_dir/modified/fstab"
                            else
                                echo "[DRYRUN] Could not find UUID for $device. Would skip."
                                echo "$line" >> "$staging_dir/modified/fstab"
                            fi
                        elif [[ "$device" =~ ^/dev/disk/azure/scsi[0-9]*/lun[0-9]* ]]; then
                            uuid=$(blkid "$device" | awk -F\" '/UUID=/ {print $2}')
                            if [ -n "$uuid" ]; then
                                newline=$(echo "$line" | sed "s|$device|UUID=$uuid|g")
                                echo "[DRYRUN] Would replace $device with UUID=$uuid"
                                echo "$newline" >> "$staging_dir/modified/fstab"
                            else
                                echo "[DRYRUN] Could not find UUID for $device. Would skip."
                                echo "$line" >> "$staging_dir/modified/fstab"
                            fi
                        else
                            echo "$line" >> "$staging_dir/modified/fstab"
                        fi
                    else
                        echo "$line" >> "$staging_dir/modified/fstab"
                    fi
                done < /etc/fstab

                diff -u "$staging_dir/original/fstab" "$staging_dir/modified/fstab" > "$staging_dir/diffs/fstab.diff" 2>&1 || true
                echo "[DRYRUN] Fstab diff staged in $staging_dir/diffs/fstab.diff"
                cat "$staging_dir/diffs/fstab.diff"
            else
                echo "[INFO] Replacing deprecated device names in /etc/fstab with UUIDs..."

                # Create a backup of the fstab file
                cp /etc/fstab /etc/fstab.bak

                # Ensure fstab.new starts fresh (avoid stale leftovers from interrupted runs)
                rm -f /etc/fstab.new

                # Use sed to replace device names with UUIDs
                while read -r line; do
                    if [[ "$line" =~ ^[^#] ]]; then
                        device=$(echo "$line" | awk '{print $1}')
                        if [[ "$device" =~ ^/dev/sd[a-z][0-9]*$ ]]; then
                            uuid=$(blkid "$device" | awk -F\" '/UUID=/ {print $2}')
                            if [ -n "$uuid" ]; then
                                newline=$(echo "$line" | sed "s|$device|UUID=$uuid|g")
                                echo "[INFO] Replaced $device with UUID=$uuid"
                                echo "$newline" >> /etc/fstab.new
                            else
                                echo "[WARNING] Could not find UUID for $device.  Skipping."
                                echo "$line" >> /etc/fstab.new
                            fi
                        elif [[ "$device" =~ ^/dev/disk/azure/scsi[0-9]*/lun[0-9]* ]]; then
                            uuid=$(blkid "$device" | awk -F\" '/UUID=/ {print $2}')
                            if [ -n "$uuid" ]; then
                                newline=$(echo "$line" | sed "s|$device|UUID=$uuid|g")
                                echo "[INFO] Replaced $device with UUID=$uuid"
                                echo "$newline" >> /etc/fstab.new
                            else
                                echo "[WARNING] Could not find UUID for $device.  Skipping."
                                echo "$line" >> /etc/fstab.new
                            fi
                        else
                            echo "$line" >> /etc/fstab.new
                        fi
                    else
                        echo "$line" >> /etc/fstab.new
                    fi
                done < /etc/fstab

                # Replace the old fstab with the new fstab
                mv /etc/fstab.new /etc/fstab

                echo "[INFO] /etc/fstab updated with UUIDs.  Original fstab backed up to /etc/fstab.bak"
            fi
        else
                echo "[ERROR] /etc/fstab contains device names causing issues switching to NVMe"
        fi
    else
        echo "[INFO] /etc/fstab does not contain deprecated device names."
    fi
}

# Run the checks
check_azure_vm_utils
check_nvme_driver
check_nvme_timeout
check_fstab

# Generate dry-run summary report
if $dry_run && $fix; then
    echo ""
    echo "[DRYRUN] ============================================"
    echo "[DRYRUN] Summary report for $(hostname)"
    echo "[DRYRUN] Distro: $distro | Kernel: $(uname -r)"
    echo "[DRYRUN] Staging directory: $staging_dir"
    echo "[DRYRUN] ============================================"
    echo "[DRYRUN] Files in staging directory:"
    find "$staging_dir" -type f | sort | while read -r f; do
        echo "[DRYRUN]   $f"
    done
    echo "[DRYRUN] ============================================"
    echo "[DRYRUN] No system files were modified."
fi

exit 0
"""
