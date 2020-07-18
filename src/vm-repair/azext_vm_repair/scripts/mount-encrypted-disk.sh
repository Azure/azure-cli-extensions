#!/bin/bash
setlog ()
{
export logpath=/var/log/vmrepair
export logfile=vmrepair.log
mkdir -p ${logpath}
echo "`date` Initiating vmrepair mount script" >> ${logpath}/${logfile} 2>&1
}

duplication_validation ()
{
#/boot/efi duplication validation
echo "`date` Validating boot/efi" >> ${logpath}/${logfile} 2>&1
efi_cnt=`lsblk | grep -i "/boot/efi" | wc -l`
if [ "${efi_cnt}" -eq 2 ]
then
        umount /boot/efi >> ${logpath}/${logfile} 2>&1
fi
}

get_data_disk ()
{
echo "`date` Getting data disk" >> ${logpath}/${logfile} 2>&1
export data_disk=`ls -la /dev/disk/azure/scsi1/lun0 | awk -F. '{print "/dev"$7}'` >> ${logpath}/${logfile} 2>&1
if [ -z ${data_disk} ]
then
echo "`date` OS disk attached as data disk was not found, cannot continue" >> ${logpath}/${logfile} 2>&1
exit
else
echo "`date` The data disk is ${data_disk}" >> ${logpath}/${logfile} 2>&1
fi
}

create_mountpoints ()
{
echo "`date` Creating mountpoints" >> ${logpath}/${logfile} 2>&1
mkdir /{investigateboot,investigateroot} >> ${logpath}/${logfile} 2>&1
}

rename_local_lvm ()
{
echo "`date` Renaming Local VG" >> ${logpath}/${logfile} 2>&1
vgrename -y ${local_vg_list} rescuevg  >> ${logpath}/${logfile} 2>&1
}

check_local_lvm ()
{
echo "`date` Checking Local LVM" >> ${logpath}/${logfile} 2>&1
export local_vg_list=`vgs --noheadings -o vg_name| tr -d '   '` >> ${logpath}/${logfile} 2>&1
local_vg_number=`vgs --noheadings -o vg_name | wc -l` >> ${logpath}/${logfile} 2>&1
if [ ${local_vg_number} -eq 1 ]
        then
                echo "`date` 1 VG found, renaming it" >> ${logpath}/${logfile} 2>&1
                rename_local_lvm
        else
                echo "`date` VGs found different than 1, we found ${local_vg_number}" >> ${logpath}/${logfile} 2>&1
fi
}

data_os_lvm_check ()
{
echo "`date` Looking for LVM on the data disk" >> ${logpath}/${logfile} 2>&1
export lvm_part=`fdisk -l ${data_disk}| grep -i lvm | awk '{print $1}'` >> ${logpath}/${logfile} 2>&1
echo ${lvm_part} >> ${logpath}/${logfile} 2>&1
if [ -z ${lvm_part} ]
then
export root_part=`fdisk -l ${data_disk} | grep ^/ |awk '$4 > 60000000{print $1}'` >> ${logpath}/${logfile} 2>&1
echo "`date` LVM not found on the data disk" >> ${logpath}/${logfile} 2>&1
echo "`date` The OS partition on the data drive is ${root_part}" >> ${logpath}/${logfile} 2>&1
else
export root_part=${lvm_part} >> ${logpath}/${logfile} 2>&1
echo "`date` LVM found on the data disk" >> ${logpath}/${logfile} 2>&1
echo "`date` The OS partition on the data drive is ${lvm_part}" >> ${logpath}/${logfile} 2>&1
fi
}

locate_mount_data_boot ()
{
echo "`date` Locating the partitions on the data drive" >> ${logpath}/${logfile} 2>&1
export data_parts=`fdisk -l ${data_disk} | grep ^/  | awk '{print $1}'` >> ${logpath}/${logfile} 2>&1
echo "`date` Your data partitions are: ${data_parts}" >> ${logpath}/${logfile} 2>&1

#create mountpoints for all the data parts
echo "`date` Creating mountpoints for all partitions on the data drive" >> ${logpath}/${logfile} 2>&1
for dpart in ${data_parts} ; do echo "`date` Creating mountpoint for ${dpart}" >> ${logpath}/${logfile} 2>&1 ; mkdir -p /tmp${dpart} >> ${logpath}/${logfile} 2>&1 ; done 

#mount all partitions
echo "`date` Mounting all partitions on the data drive" >> ${logpath}/${logfile} 2>&1
for part in ${data_parts} ; do echo "`date` Mounting ${part} on /tmp/${part}" >> ${logpath}/${logfile} 2>&1 ; mount ${part} /tmp${part} >> ${logpath}/${logfile} 2>&1 ; done 
echo "`date`Locating luksheader" >> ${logpath}/${logfile} 2>&1
export luksheaderpath=`find /tmp -name osluksheader` >> ${logpath}/${logfile} 2>&1
echo "`date` The luksheader part is ${luksheaderpath}" >> ${logpath}/${logfile} 2>&1
export boot_part=`df -h $luksheaderpath | grep ^/ |awk '{print $1}'` >> ${logpath}/${logfile} 2>&1
echo "`date` The boot partition on the data disk is ${boot_part}" >> ${logpath}/${logfile} 2>&1
}

mount_cmd ()
{
echo "`date` Determine mount command" >> ${logpath}/${logfile} 2>&1
mount_cmd=`mount -o nouuid 2> /dev/null`
if [ $? -gt 0 ]
then
        export mount_cmd="mount"
else
        export mount_cmd="mount -o nouuid"
fi
}

mount_lvm ()
{
echo "`date` Mounting LVM structures found on ${root_part}" >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/rootlv /investigateroot >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/varlv /investigateroot/var/ >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/homelv /investigateroot/home >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/optlv /investigateroot/opt >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/usrlv /investigateroot/usr >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/rootvg/tmplv /investigateroot/tmp >> ${logpath}/${logfile} 2>&1
lsblk -f >> ${logpath}/${logfile} 2>&1
}

unlock_root ()
{
echo "`date` unlocking root with command: cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${root_part} osencrypt" >> ${logpath}/${logfile} 2>&1 
cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${root_part} osencrypt >> ${logpath}/${logfile} 2>&1
}

verify_root_unlock ()
{
echo "`date` Verifying osencrypt unlock" >> ${logpath}/${logfile} 2>&1
lsblk -f  | grep osencrypt >> ${logpath}/${logfile} 2>&1
if [ $? -gt 0 ]
then
        echo "`date` device osencrypt was not found" >> ${logpath}/${logfile} 2>&1
        exit
else
        echo "`date` device osencrypt found" >> ${logpath}/${logfile} 2>&1
fi
}

mount_encrypted ()
{
echo "`date` Mounting root" >> ${logpath}/${logfile} 2>&1
if [ -z ${lvm_part} ]
then
echo "`date` Mounting /dev/mapper/osencrypt on /investigateroot" >> ${logpath}/${logfile} 2>&1
${mount_cmd} /dev/mapper/osencrypt /investigateroot >> ${logpath}/${logfile} 2>&1
else
        sleep 5
        mount_lvm
fi
}

mount_boot ()
{
echo "`date` Unmounting the boot partition ${boot_part} on the data drive from the temp mount" >> ${logpath}/${logfile} 2>&1
umount -l ${boot_part} >> ${logpath}/${logfile} 2>&1
echo "`date` Mounting the boot partition ${boot_part} on /investigateboot" >> ${logpath}/${logfile} 2>&1
${mount_cmd} ${boot_part} /investigateboot/ >> ${logpath}/${logfile} 2>&1
}

remount_boot ()
{
echo "`date` Unmounting the boot partition ${boot_part} on the data drive from the temp mount" >> ${logpath}/${logfile} 2>&1
umount -l ${boot_part} >> ${logpath}/${logfile} 2>&1
echo "`date` Mounting the boot partition ${boot_part} on /investigateroot/boot" >> ${logpath}/${logfile} 2>&1
${mount_cmd} ${boot_part} /investigateroot/boot >> ${logpath}/${logfile} 2>&1
}

setlog
duplication_validation
create_mountpoints
get_data_disk
check_local_lvm
data_os_lvm_check
mount_cmd
locate_mount_data_boot
mount_boot
unlock_root
verify_root_unlock
mount_encrypted
remount_boot


