#!/bin/bash

#creating mountpoint directories
mkdir /{investigateboot,investigateroot}

#Getting boot and root partition info

boot_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 1p`
root_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 2p`


#mouning the boot partition

mount -o nouuid  $boot_part /investigateboot

#unlocking the root partition using passphrase

cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName_1_0 --header /investigateboot/luks/osluksheader $root_part investigateosencrypt

#mounting the unlocked root partition

mount -o nouuid /dev/mapper/investigateosencrypt /investigateroot

#nmounting boot and mounting it inside rootpartition.

umount -l /investigateboot
mount -o nouuid $boot_part /investigateroot/boot
