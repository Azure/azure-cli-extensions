#!/bin/bash

#creating mountpoint directories
mkdir /{investigateboot,investigateroot}

#Getting boot and root partition info

root=`fdisk -l | grep -i sdd | grep -iv disk | sed -n 1p | awk '$4 > 60000000{print $1}'`
if [ -z $root ]
then
        boot_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 1p`
        root_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 2p`
else
        root_part="$root"
        boot_part=`fdisk -l | grep -i sdd | grep -iv disk | awk '{print $1}' | sed -n 2p`
fi

mount_cmd=`mount -o nouuid 2> /dev/null`
if [ $? -gt 0 ]
then
        mount_cmd="mount"
else
        mount_cmd="mount -o nouuid"
fi

#mouning the boot partition

$mount_cmd $boot_part /investigateboot

#unlocking the root partition using passphrase

cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName_1_0 --header /investigateboot/luks/osluksheader $root_part investigateosencrypt

#mounting the unlocked root partition

$mount_cmd /dev/mapper/investigateosencrypt /investigateroot

#nmounting boot and mounting it inside rootpartition.

umount -l /investigateboot
$mount_cmd $boot_part /investigateroot/boot
