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
    rm -rf "$staging_dir" || return 1
    mkdir -p "$staging_dir/original" "$staging_dir/modified" "$staging_dir/diffs" || return 1
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
    setup_dryrun || exit 1
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
KERNEL=="nvme*[0-9]n*[0-9]", ENV{DEVTYPE}=="disk", ATTRS{nsid}=="?*", ATTRS{nsid}!="1", PROGRAM="/bin/sh -ec '\''echo $$((%s{nsid}-2))'\''", SYMLINK+="disk/azure/data/by-lun/%c"
KERNEL=="nvme*[0-9]n*[0-9]p[0-9]*", ENV{DEVTYPE}=="partition", ATTRS{nsid}=="?*", ATTRS{nsid}!="1", PROGRAM="/bin/sh -ec '\''echo $$((%s{nsid}-2))'\''", SYMLINK+="disk/azure/data/by-lun/%c-part%n"

LABEL="azure_nvme_fallback_end"'

_install_fallback_udev_rules() {
    local _target="/etc/udev/rules.d/99-azure-nvme-fallback.rules"

    if [ -f "$_target" ]; then
        echo "[INFO] Fallback udev rule already installed at $_target"
        return
    fi

    if $dry_run; then
        echo "[DRYRUN] Would install fallback udev rule at $_target"
        echo "$_FALLBACK_UDEV_RULE" > "$staging_dir/modified/99-azure-nvme-fallback.rules" || return 1
        return
    fi

    echo "[INFO] Installing fallback NVMe udev rule at $_target"
    mkdir -p /etc/udev/rules.d || return 1
    echo "$_FALLBACK_UDEV_RULE" > "$_target" || return 1
    udevadm control --reload-rules 2>/dev/null || true
    echo "[INFO] Fallback udev rule installed. Provides:"
    echo "[INFO]   - io_timeout=240s for NVMe remote disks"
    echo "[INFO]   - /dev/disk/azure/root symlink"
    echo "[INFO]   - /dev/disk/azure/data/by-lun/N symlinks"
    echo "[INFO]   Note: by-name/by-serial/by-index require azure-vm-utils"
}

# Function to check if NVMe driver is in initrd/initramfs or built into the kernel
nvme_module_builtin() {
    grep -Eq "(^|/)($2)[.]ko$" "/lib/modules/$1/modules.builtin" 2>/dev/null
}

nvme_verify_boot_images() {
    local tool="$1" nvme_builtin="$2" pci_builtin="$3" image listing missing=false
    shift 3
    for image in "$@"; do
        if ! listing=$("$tool" "$image" 2>&1); then
            echo "[ERROR] Cannot inspect boot image $image."
            return 2
        fi
        if ! $nvme_builtin && ! grep -Eq '(^|[/[:space:]])nvme[.]ko([.](xz|gz|zst))?([[:space:]]|$)' <<< "$listing"; then
            echo "[WARNING] NVMe PCI driver missing in $image."
            missing=true
        fi
        if ! $pci_builtin && ! grep -Eq '(^|[/[:space:]])(hv_pci|pci[-_]hyperv)[.]ko([.](xz|gz|zst))?([[:space:]]|$)' <<< "$listing"; then
            echo "[WARNING] Hyper-V PCI driver missing in $image."
            missing=true
        fi
    done
    ! $missing
}

check_nvme_driver() {
    local kernel="${1:-$(uname -r)}" nvme_builtin=false pci_builtin=false tool image status module
    local candidates=() images=()
    echo "[INFO] Checking NVMe and Hyper-V PCI boot drivers for $kernel..."
    nvme_module_builtin "$kernel" nvme && nvme_builtin=true
    nvme_module_builtin "$kernel" 'hv_pci|pci[-_]hyperv' && pci_builtin=true
    if $nvme_builtin && $pci_builtin; then
        echo "[INFO] NVMe and Hyper-V PCI drivers are built into kernel $kernel."
        return 0
    fi
    case "$distro" in
        ubuntu|debian)
            tool=lsinitramfs
            candidates=("/boot/initrd.img-$kernel")
            ;;
        suse|sles)
            tool=lsinitrd
            candidates=("/boot/initrd-$kernel" "/boot/initramfs-$kernel.img")
            ;;
        redhat|rhel|centos|rocky|almalinux|azurelinux|mariner|ol)
            tool=lsinitrd
            candidates=("/boot/initramfs-$kernel.img")
            ;;
        *)
            echo "[ERROR] Unsupported distribution for NVMe driver preparation."
            return 1
            ;;
    esac
    for image in "${candidates[@]}"; do
        [ -f "$image" ] && images+=("$image")
    done
    if [ "${#images[@]}" -eq 0 ]; then
        echo "[ERROR] No usable boot image found for kernel $kernel."
        return 1
    fi
    if nvme_verify_boot_images "$tool" "$nvme_builtin" "$pci_builtin" "${images[@]}"; then
        echo "[INFO] Required boot drivers verified for $kernel."
        return 0
    else
        status=$?
        [ "$status" -eq 1 ] || return 1
    fi
    if ! $fix; then
        echo "[ERROR] Required boot drivers are missing for $kernel."
        return 1
    fi
    if $dry_run; then
        echo "[DRYRUN] Would explicitly include NVMe/Hyper-V PCI drivers and rebuild $kernel."
        if [ "$tool" = lsinitramfs ]; then
            printf '%s\n' 'nvme' 'pci-hyperv' > "$staging_dir/modified/initramfs-modules.txt" || return 1
            printf '%s\n' 'update-initramfs -u -k all' >> "$staging_dir/modified/initramfs-commands.txt" || return 1
        else
            printf '%s\n' 'add_drivers+=" nvme nvme-core pci-hyperv "' > "$staging_dir/modified/dracut-nvme.conf" || return 1
            printf '%s\n' 'dracut -f --regenerate-all' >> "$staging_dir/modified/initramfs-commands.txt" || return 1
        fi
        return 0
    fi
    case "$distro" in
        ubuntu|debian)
            mkdir -p /etc/initramfs-tools || return 1
            touch /etc/initramfs-tools/modules || return 1
            for module in nvme pci-hyperv; do
                if ! grep -qxF "$module" /etc/initramfs-tools/modules; then
                    printf '%s\n' "$module" >> /etc/initramfs-tools/modules || return 1
                fi
            done
            update-initramfs -u -k all || return 1
            ;;
        *)
            mkdir -p /etc/dracut.conf.d || return 1
            printf '%s\n' 'add_drivers+=" nvme nvme-core pci-hyperv "' > /etc/dracut.conf.d/nvme.conf || return 1
            dracut -f --regenerate-all || return 1
            ;;
    esac
    if ! nvme_verify_boot_images "$tool" "$nvme_builtin" "$pci_builtin" "${images[@]}"; then
        echo "[ERROR] Required boot drivers remain unavailable after rebuilding $kernel."
        return 1
    fi
    echo "[INFO] Required boot drivers repaired and verified for $kernel."
}

# Function to check nvme_core.io_timeout parameter
nvme_timeout_entries_ready() {
    awk '
        /^[[:space:]]*linux(efi|16)?[[:space:]]+/ {
            seen = 1
            count = 0
            for (i = 1; i <= NF; i++) {
                if ($i ~ /^nvme_core[.]io_timeout=/) {
                    count++
                    if ($i != "nvme_core.io_timeout=240") bad = 1
                }
            }
            if (count != 1) bad = 1
        }
        END { exit !(seen && !bad) }
    ' "$1"
}

set_rhel7_timeout_defaults() {
    if ! grep -q '^GRUB_CMDLINE_LINUX="' "$1"; then
        echo "[ERROR] Expected quoted GRUB_CMDLINE_LINUX in $1."
        return 1
    fi
    if ! sed -i -E '/^GRUB_CMDLINE_LINUX="/ { s/(^|[[:space:]"])nvme_core[.]io_timeout=[^[:space:]"]+/\1/g; s/^(GRUB_CMDLINE_LINUX=")/\1nvme_core.io_timeout=240 /; }' "$1"; then
        echo "[ERROR] Failed to update timeout defaults in $1."
        return 1
    fi
}

check_nvme_timeout() {
    echo "[INFO] Checking nvme_core.io_timeout parameter..."

    local _rhel7_efi_config=""
    case "$distro" in
        redhat|rhel|centos)
            if [ -r /etc/os-release ] &&
               ( . /etc/os-release; [ "${VERSION_ID%%.*}" = 7 ] ) &&
               { [ -e /etc/grub2-efi.cfg ] || [ -L /etc/grub2-efi.cfg ]; }; then
                if ! _rhel7_efi_config=$(readlink -e /etc/grub2-efi.cfg); then
                    echo "[ERROR] Cannot resolve guest EFI configuration /etc/grub2-efi.cfg."
                    return 1
                fi
                case "$_rhel7_efi_config" in
                    /boot/efi/EFI/*/grub.cfg) ;;
                    *) echo "[ERROR] Unsupported guest EFI configuration: $_rhel7_efi_config"; return 1 ;;
                esac
                # Older RHEL EFI uses a full config, not the modern redirect stub.
                if ! grep -Eq '^[[:space:]]*linux(efi|16)?[[:space:]]+' "$_rhel7_efi_config"; then
                    echo "[ERROR] Expected standalone kernel entries in $_rhel7_efi_config; refusing to overwrite."
                    return 1
                fi
            fi
            ;;
    esac

    # Build grub file list dynamically for verification
    _grub_check_files="/etc/default/grub"
    if [ -f /boot/grub2/grub.cfg ]; then
        _grub_check_files="$_grub_check_files /boot/grub2/grub.cfg"
    elif [ -f /boot/grub/grub.cfg ]; then
        _grub_check_files="$_grub_check_files /boot/grub/grub.cfg"
    fi

    if { [ -n "$_rhel7_efi_config" ] && nvme_timeout_entries_ready "$_rhel7_efi_config"; } ||
       { [ -z "$_rhel7_efi_config" ] && grep -q "nvme_core.io_timeout=240" $_grub_check_files 2>/dev/null; }; then
        echo "[INFO] nvme_core.io_timeout is set to 240."
        if $dry_run && $fix; then
            echo "[DRYRUN] nvme_core.io_timeout already set to 240. No grub changes needed."
            echo "nvme_core_io_timeout=240" > "$staging_dir/modified/nvme-timeout-status.txt"
            echo "status=already_configured" >> "$staging_dir/modified/nvme-timeout-status.txt"
        fi
    elif [ -z "$_rhel7_efi_config" ] && command -v grubby &>/dev/null && grubby --info=ALL 2>/dev/null | grep -q "nvme_core.io_timeout=240"; then
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
                    cp "$grub_file" "$staging_dir/original/grub" || return 1
                    cp "$grub_file" "$staging_dir/modified/grub" || return 1
                    case "$distro" in
                        ubuntu)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub" || return 1
                            ;;
                        debian)
                            sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub" || return 1
                            ;;
                        suse|sles|opensuse*)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub" || return 1
                            ;;
                        ol|azurelinux|mariner)
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub" || return 1
                            ;;
                        *)
                            if [ -n "$_rhel7_efi_config" ]; then
                                set_rhel7_timeout_defaults "$staging_dir/modified/grub" || return 1
                                echo "[DRYRUN] Would regenerate $_rhel7_efi_config"
                            else
                                sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' "$staging_dir/modified/grub" || return 1
                            fi
                            ;;
                    esac
                    diff -u "$staging_dir/original/grub" "$staging_dir/modified/grub" > "$staging_dir/diffs/grub.diff" 2>&1 || [ "$?" -eq 1 ] || return 1
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
                    return 1
                fi
            else
                echo "[INFO] Setting nvme_core.io_timeout to 240..."
                case "$distro" in
                    ubuntu)
                        sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub || return 1
                        GRUB_DISABLE_OS_PROBER=true update-grub || return 1
                        ;;
                    debian)
                        sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' /etc/default/grub || return 1
                        GRUB_DISABLE_OS_PROBER=true update-grub || return 1
                        ;;
                    suse|sles|opensuse*)
                        if [ -f /etc/default/grub ]; then
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub || return 1
                            GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg || return 1
                        else
                            echo "[ERROR] /etc/default/grub not found."
                            return 1
                        fi
                        ;;
                    redhat|rhel|centos|rocky|almalinux)
                        if [ -f /etc/default/grub ]; then
                            if [ -n "$_rhel7_efi_config" ]; then
                                set_rhel7_timeout_defaults /etc/default/grub || return 1
                                if ! GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o "$_rhel7_efi_config"; then
                                    echo "[ERROR] Failed to regenerate $_rhel7_efi_config."
                                    return 1
                                fi
                            else
                                sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="nvme_core.io_timeout=240 /g' /etc/default/grub || return 1
                                GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg || return 1
                            fi
                            # Update BLS entries if applicable (RHEL 8+, AlmaLinux 8+)
                            if grep -q "GRUB_ENABLE_BLSCFG=true" /etc/default/grub 2>/dev/null; then
                                if command -v grubby &>/dev/null; then
                                    grubby --update-kernel=ALL --args="nvme_core.io_timeout=240" || return 1
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
                            sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvme_core.io_timeout=240 /g' /etc/default/grub || return 1
                            GRUB_DISABLE_OS_PROBER=true grub2-mkconfig -o /boot/grub2/grub.cfg || return 1
                            # Update BLS entries if applicable (OL 8.10+)
                            if grep -q "GRUB_ENABLE_BLSCFG=true" /etc/default/grub 2>/dev/null; then
                                if command -v grubby &>/dev/null; then
                                    grubby --update-kernel=ALL --args="nvme_core.io_timeout=240" || return 1
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

                if { [ -n "$_rhel7_efi_config" ] && nvme_timeout_entries_ready "$_rhel7_efi_config"; } ||
       { [ -z "$_rhel7_efi_config" ] && grep -q "nvme_core.io_timeout=240" $_grub_check_files 2>/dev/null; }; then
                    echo "[INFO] nvme_core.io_timeout set successfully."
                elif [ -z "$_rhel7_efi_config" ] && command -v grubby &>/dev/null && grubby --info=ALL 2>/dev/null | grep -q "nvme_core.io_timeout=240"; then
                    echo "[INFO] nvme_core.io_timeout set successfully (BLS entries)."
                else
                    echo "[ERROR] Failed to set nvme_core.io_timeout."
                    return 1
                fi
            fi
        else
            echo "[ERROR] nvme_core.io_timeout is not set to 240."
            return 1
        fi
    fi
}

# Function to check /etc/fstab for deprecated device names
nvme_device_uuid() {
    command blkid -s UUID -o value "$1"
}

nvme_fstab_has_devices() {
    awk '$0 !~ /^[[:space:]]*#/ && ($1 ~ /^\/dev\/sd[a-z]+[0-9]*$/ || $1 ~ /^\/dev\/disk\/azure\/scsi[0-9]+\/lun[0-9]+(-part[0-9]+)?$/) { found=1 }
         END { exit !found }' "$1"
}

nvme_migrate_fstab() {
    local line device rest uuid missing=false
    : > "$2" || return 1
    while IFS= read -r line || [ -n "$line" ]; do
        read -r device rest <<< "$line"
        if [[ "$device" =~ ^/dev/sd[a-z]+[0-9]*$ || "$device" =~ ^/dev/disk/azure/scsi[0-9]+/lun[0-9]+(-part[0-9]+)?$ ]]; then
            if uuid=$(nvme_device_uuid "$device") && [[ -n "$uuid" && "$uuid" != *[[:space:]]* ]]; then
                line="${line/"$device"/UUID=$uuid}"
                echo "[INFO] Resolved $device to UUID=$uuid."
            else
                echo "[ERROR] Cannot resolve UUID for $device; leaving the original fstab unchanged."
                missing=true
            fi
        fi
        printf '%s\n' "$line" >> "$2" || return 1
    done < "$1"
    ! $missing
}

check_fstab() {
    echo "[INFO] Checking /etc/fstab for deprecated device names..."
    if [ ! -r /etc/fstab ]; then
        echo "[ERROR] Cannot read /etc/fstab."
        return 1
    fi
    if nvme_fstab_has_devices /etc/fstab; then
        :
    else
        if [ "$?" -ne 1 ]; then
            echo "[ERROR] Cannot inspect /etc/fstab."
            return 1
        fi
        echo "[INFO] /etc/fstab has no deprecated device names."
        return 0
    fi
    if ! $fix; then
        echo "[ERROR] /etc/fstab contains deprecated device names."
        return 1
    fi
    if $dry_run; then
        cp /etc/fstab "$staging_dir/original/fstab" || return 1
        nvme_migrate_fstab /etc/fstab "$staging_dir/modified/fstab" || return 1
        diff -u "$staging_dir/original/fstab" "$staging_dir/modified/fstab" > "$staging_dir/diffs/fstab.diff" 2>&1 || [ "$?" -eq 1 ] || return 1
        cat "$staging_dir/diffs/fstab.diff" || return 1
        return 0
    fi
    cp /etc/fstab /etc/fstab.bak || return 1
    rm -f /etc/fstab.new || return 1
    nvme_migrate_fstab /etc/fstab /etc/fstab.new || return 1
    mv /etc/fstab.new /etc/fstab || return 1
    if nvme_fstab_has_devices /etc/fstab; then
        echo "[ERROR] Deprecated device names remain in /etc/fstab."
        return 1
    fi
    echo "[INFO] /etc/fstab updated with UUIDs; original saved as /etc/fstab.bak."
}

# Run the checks
failed=false
check_azure_vm_utils || failed=true
found_kernel=false
for modules_dir in /lib/modules/*; do
    [ -d "$modules_dir" ] || continue
    found_kernel=true
    check_nvme_driver "${modules_dir##*/}" || failed=true
done
if ! $found_kernel; then echo "[ERROR] No installed kernel module inventory."; failed=true; fi
check_nvme_timeout || failed=true
check_fstab || failed=true
if $failed; then echo "NVME_PREPARATION_RESULT:FAILED"; exit 1; fi

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

if $dry_run; then echo "NVME_PREPARATION_RESULT:DRYRUN"; else echo "NVME_PREPARATION_RESULT:READY"; fi
exit 0
"""
