#!/bin/bash

#/boot/efi duplication validation
efi_cnt=`lsblk | grep -i "/boot/efi" | wc -l`
if [ "$efi_cnt" -eq 2 ]
then
        umount /boot/efi
fi

#creating mountpoint directories
mkdir /{investigateboot,investigateroot}

#Getting boot and root partition info
mounted_disks=`df -Ph | awk '{print $1}' | egrep -iv "filesystem|tmpfs|udev" | sed 's/[0-9]//g' | xargs | sed 's/ /|/g'`

root=`fdisk -l | egrep -iv "$mounted_disks" | grep -i sd | grep -iv disk | sed -n 1p | awk '$4 > 60000000{print $1}'`
if [ -z $root ]
then
        boot_part=`fdisk -l | egrep -iv "$mounted_disks" | grep -i sd | grep -iv disk | awk '{print $1}' | sed -n 1p`
        root_part=`fdisk -l | egrep -iv "$mounted_disks" | grep -i sd | grep -iv disk | awk '{print $1}' | sed -n 2p`
else
        root_part="$root"
        boot_part=`fdisk -l | egrep -iv "$mounted_disks" | grep -i sd | grep -iv disk | awk '{print $1}' | sed -n 2p`
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

cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName_1_0 --header /investigateboot/luks/osluksheader $root_part osencrypt

#mounting the unlocked root partition

$mount_cmd /dev/mapper/osencrypt /investigateroot

#nmounting boot and mounting it inside rootpartition.

umount -l /investigateboot
$mount_cmd $boot_part /investigateroot/boot
