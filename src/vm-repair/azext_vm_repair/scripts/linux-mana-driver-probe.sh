#!/bin/sh
# Read-only MANA readiness probe run in the guest by az vm repair through Run Command.
# Takes no input, changes nothing, and prints one machine-readable line:
#   VMREPAIR_MANA_PROBE hardware=<mana|mellanox|none|unknown> driver=<present|missing|unknown>
# hardware: accelerated-networking virtual function on the PCI bus (MANA 1414:00ba, Mellanox vendor 15b3).
#           "none" only after every PCI entry was read; if any entry cannot be read and no MANA device was
#           found, the result is "unknown", because the unreadable entry could be the MANA device.
# driver:   whether the running kernel can load the MANA Ethernet driver (loaded, built in, or a module file).
#           "missing" only when both the built-in list and the module tree were read without error.

hardware=unknown
pci_root=/sys/bus/pci/devices
if [ -d "$pci_root" ] && [ -r "$pci_root" ] && [ -x "$pci_root" ]; then
    found_mana=0
    found_mellanox=0
    incomplete=0
    for device_path in "$pci_root"/*; do
        # An empty directory leaves the pattern unexpanded.
        [ -e "$device_path" ] || continue
        if ! vendor=$(cat "$device_path/vendor" 2>/dev/null); then
            incomplete=1
            continue
        fi
        if [ "$vendor" = "0x15b3" ]; then
            found_mellanox=1
        elif [ "$vendor" = "0x1414" ]; then
            if ! device=$(cat "$device_path/device" 2>/dev/null); then
                incomplete=1
            elif [ "$device" = "0x00ba" ]; then
                found_mana=1
                break
            fi
        fi
    done
    if [ "$found_mana" -eq 1 ]; then
        hardware=mana
    elif [ "$incomplete" -eq 1 ]; then
        hardware=unknown
    elif [ "$found_mellanox" -eq 1 ]; then
        hardware=mellanox
    else
        hardware=none
    fi
fi

driver=unknown
release=$(uname -r 2>/dev/null)
module_root="/lib/modules/$release"
if [ -d /sys/module/mana ]; then
    driver=present
elif [ -n "$release" ] && [ -d "$module_root" ]; then
    # grep: 0 = listed as built in, 1 = read and not listed, anything else = could not read.
    grep -q '/mana\.ko' "$module_root/modules.builtin" 2>/dev/null
    builtin_status=$?
    # find exits non-zero if any part of the tree could not be traversed.
    module_files=$(find "$module_root" -name 'mana.ko*' 2>/dev/null)
    find_status=$?
    if [ "$builtin_status" -eq 0 ] || [ -n "$module_files" ]; then
        driver=present
    elif [ "$builtin_status" -eq 1 ] && [ "$find_status" -eq 0 ]; then
        driver=missing
    fi
fi

echo "VMREPAIR_MANA_PROBE hardware=$hardware driver=$driver"
exit 0
