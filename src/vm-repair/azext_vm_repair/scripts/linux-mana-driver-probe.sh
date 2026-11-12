#!/bin/sh
# Read-only MANA readiness probe run in the guest by az vm repair through Run Command.
# Takes no input, changes nothing, and prints one machine-readable line:
#   VMREPAIR_MANA_PROBE hardware=<mana|mellanox|none|unknown> driver=<present|missing|unknown>
# hardware: accelerated-networking virtual function on the PCI bus (MANA 1414:00ba, Mellanox vendor 15b3).
# driver:   whether the running kernel can load the MANA Ethernet driver (module file or built-in).

hardware=unknown
if [ -d /sys/bus/pci/devices ]; then
    hardware=none
    for device_path in /sys/bus/pci/devices/*; do
        [ -r "$device_path/vendor" ] || continue
        vendor=$(cat "$device_path/vendor" 2>/dev/null)
        device=$(cat "$device_path/device" 2>/dev/null)
        if [ "$vendor" = "0x1414" ] && [ "$device" = "0x00ba" ]; then
            hardware=mana
            break
        fi
        if [ "$vendor" = "0x15b3" ]; then
            hardware=mellanox
        fi
    done
fi

driver=unknown
release=$(uname -r 2>/dev/null)
if [ -d /sys/module/mana ]; then
    driver=present
elif [ -n "$release" ] && [ -d "/lib/modules/$release" ]; then
    if grep -q '/mana\.ko' "/lib/modules/$release/modules.builtin" 2>/dev/null; then
        driver=present
    elif [ -n "$(find "/lib/modules/$release" -name 'mana.ko*' 2>/dev/null | head -n 1)" ]; then
        driver=present
    else
        driver=missing
    fi
fi

echo "VMREPAIR_MANA_PROBE hardware=$hardware driver=$driver"
exit 0
