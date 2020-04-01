#!/bin/bash
mkdir /{investigateboot,investigateroot}
boot_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 1p`
root_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 2p`
mount -o nouuid  $boot_part /investigateboot
cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName_1_0 --header /investigateboot/luks/osluksheader $root_part investigateosencrypt
mount -o nouuid /dev/mapper/investigateosencrypt /investigateroot
umount -l /investigateboot
mount -o nouuid $boot_part /investigateroot/boot
