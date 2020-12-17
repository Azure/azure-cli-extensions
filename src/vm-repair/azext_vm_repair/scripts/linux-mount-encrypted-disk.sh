#!/bin/bash
setlog () {
	export logpath=/var/log/vmrepair
	export logfile=vmrepair.log
	mkdir -p ${logpath}
	echo "`date` Initiating vmrepair mount script" >> ${logpath}/${logfile}
}

trapper () {
	trap 'catch $? $LINENO' ERR
	catch () {
		echo "`date` Trapped error code $1 on line $2" >> ${logpath}/${logfile}
	}
}

duplication_validation () {
	trapper
	#/boot/efi duplication validation
	echo "`date` Validating boot/efi" >> ${logpath}/${logfile}
	efi_cnt=`lsblk | grep -i "/boot/efi" | wc -l`
	if [ "${efi_cnt}" -eq 2 ]
	then
		        umount /boot/efi >> ${logpath}/${logfile}
		fi
}

locatebekvol () {
	trapper
	echo "`date` Locating BEK volume" >> ${logpath}/${logfile}
	export bekdisk=`lsblk -l -o LABEL,NAME| grep BEK | awk '{print $NF}'`
	if [ -z ${bekdisk} ]
	then
		echo "`date` No BEK disk found, cannot continue" >> ${logpath}/${logfile}
		exit
	else
		echo "`date` the BEK Volume is ${bekdisk}" >> ${logpath}/${logfile}
		export bekdisk=/dev/${bekdisk}
	fi
}

mountbekvol () {
	trapper
	echo "`date` Mounting BEK volume" >> ${logpath}/${logfile}
	export bekmountpath=/mnt/azure_bek_disk/
	mkdir -p ${bekmountpath}
	mount ${bekdisk} ${bekmountpath}
	echo "`date` BEK Volume ${bekdisk} mounted on ${bekmountpath}"  >> ${logpath}/${logfile}
}

get_data_disk () {
	trapper
	echo "`date` Getting data disk" >> ${logpath}/${logfile} 2>&1
	export data_disk=`ls -la /dev/disk/azure/scsi1/lun0 | awk -F/ '{print "/dev/"$NF}'`
	if [ -z ${data_disk} ]
	then
		echo "`date` OS disk attached as data disk was not found, cannot continue" >> ${logpath}/${logfile}
		exit
	else
		echo "`date` The data disk is ${data_disk}" >> ${logpath}/${logfile}
	fi
}

create_mountpoints () {
	trapper
	echo "`date` Creating mountpoints" >> ${logpath}/${logfile}
	mkdir /{investigateboot,investigateroot}
}

rename_local_lvm () {
	trapper
	echo "`date` Renaming Local VG" >> ${logpath}/${logfile}
	vgrename -y ${local_vg_list} rescuevg
}

check_local_lvm () {
	trapper
echo "`date` Checking Local LVM" >> ${logpath}/${logfile}
export local_vg_list=`vgs --noheadings -o vg_name| tr -d '   '` >> ${logpath}/${logfile}
local_vg_number=`vgs --noheadings -o vg_name | wc -l` >> ${logpath}/${logfile}
if [ ${local_vg_number} -eq 1 ]
        then
                echo "`date` 1 VG found, renaming it" >> ${logpath}/${logfile}
                rename_local_lvm
        else
                echo "`date` VGs found different than 1, we found ${local_vg_number}" >> ${logpath}/${logfile}
fi
}

data_os_lvm_check () {
	trapper
	echo "`date` Looking for LVM on the data disk" >> ${logpath}/${logfile}
	export lvm_part=`fdisk -l ${data_disk} 2>&1 | grep -i lvm | awk '{print $1}'` >> ${logpath}/${logfile}
	echo ${lvm_part} >> ${logpath}/${logfile}
	if [ -z ${lvm_part} ]
	then
		export root_part=`fdisk -l ${data_disk} 2>&1 | grep ^/ |awk '$4 > 60000000{print $1}'` >> ${logpath}/${logfile}
		echo "`date` LVM not found on the data disk" >> ${logpath}/${logfile}
		echo "`date` The OS partition on the data drive is ${root_part}" >> ${logpath}/${logfile}
	else
		export root_part=${lvm_part} >> ${logpath}/${logfile}
		echo "`date` LVM found on the data disk" >> ${logpath}/${logfile}
		echo "`date` The OS partition on the data drive is ${lvm_part}" >> ${logpath}/${logfile}
	fi
}

locate_mount_data_boot () {
	trapper
	echo "`date` Locating the partitions on the data drive" >> ${logpath}/${logfile}
	export data_parts=`fdisk -l ${data_disk} 2>&1 | grep ^/  | awk '{print $1}'` >> ${logpath}/${logfile}
	echo "`date` Your data partitions are: ${data_parts}" >> ${logpath}/${logfile}

	#create mountpoints for all the data parts
	echo "`date` Creating mountpoints for all partitions on the data drive" >> ${logpath}/${logfile}
	for dpart in ${data_parts} ; do echo "`date` Creating mountpoint for ${dpart}" >> ${logpath}/${logfile} ; mkdir -p /tmp${dpart} >> ${logpath}/${logfile} ; done

	#mount all partitions
	echo "`date` Mounting all partitions on the data drive" >> ${logpath}/${logfile}
	for part in ${data_parts} ; do echo "`date` Mounting ${part} on /tmp/${part}" >> ${logpath}/${logfile} ; mount ${part} /tmp${part} >> ${logpath}/${logfile} 2>&1 ; done
	echo "`date`Locating luksheader" >> ${logpath}/${logfile} 
	export luksheaderpath=`find /tmp -name osluksheader` >> ${logpath}/${logfile} 
	echo "`date` The luksheader part is ${luksheaderpath}" >> ${logpath}/${logfile}
	export boot_part=`df -h $luksheaderpath | grep ^/ |awk '{print $1}'` >> ${logpath}/${logfile}
	echo "`date` The boot partition on the data disk is ${boot_part}" >> ${logpath}/${logfile}
}

mount_cmd () {
	trapper
	echo "`date` Determine mount command" >> ${logpath}/${logfile}
	mount_cmd=`mount -o nouuid 2> /dev/null` >> ${logpath}/${logfile} 2>&1
	if [ $? -gt 0 ]
	then
		        export mount_cmd="mount"
		else
			        export mount_cmd="mount -o nouuid"
			fi
}

mount_lvm () {
	trapper
	echo "`date` Mounting LVM structures found on ${root_part}" >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/rootlv /investigateroot >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/varlv /investigateroot/var/ >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/homelv /investigateroot/home >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/optlv /investigateroot/opt >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/usrlv /investigateroot/usr >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/tmplv /investigateroot/tmp >> ${logpath}/${logfile}
	lsblk -f >> ${logpath}/${logfile}
}

unlock_root () {
	trapper
	echo "`date` unlocking root with command: cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${root_part} osencrypt" >> ${logpath}/${logfile} 
	cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${root_part} osencrypt >> ${logpath}/${logfile}
}

verify_root_unlock () {
	trapper
	echo "`date` Verifying osencrypt unlock" >> ${logpath}/${logfile}
	lsblk -f  | grep osencrypt >> ${logpath}/${logfile}
	if [ $? -gt 0 ]
	then
		        echo "`date` device osencrypt was not found" >> ${logpath}/${logfile}
			        exit
			else
				        echo "`date` device osencrypt found" >> ${logpath}/${logfile}
				fi
}

mount_encrypted () {
	trapper
	echo "`date` Mounting root" >> ${logpath}/${logfile}
	if [ -z ${lvm_part} ]
	then
		echo "`date` Mounting /dev/mapper/osencrypt on /investigateroot" >> ${logpath}/${logfile}
		${mount_cmd} /dev/mapper/osencrypt /investigateroot >> ${logpath}/${logfile}
	else
		        sleep 5
			        mount_lvm
			fi
}

mount_boot () {
	trapper
	echo "`date` Unmounting the boot partition ${boot_part} on the data drive from the temp mount" >> ${logpath}/${logfile}
	umount -l ${boot_part} >> ${logpath}/${logfile}
	echo "`date` Mounting the boot partition ${boot_part} on /investigateboot" >> ${logpath}/${logfile}
	${mount_cmd} ${boot_part} /investigateboot/ >> ${logpath}/${logfile}
}

remount_boot () {
	trapper
	echo "`date` Unmounting the boot partition ${boot_part} on the data drive from the temp mount" >> ${logpath}/${logfile}
	umount -l ${boot_part} >> ${logpath}/${logfile}
	echo "`date` Mounting the boot partition ${boot_part} on /investigateroot/boot" >> ${logpath}/${logfile}
	${mount_cmd} ${boot_part} /investigateroot/boot >> ${logpath}/${logfile}
}

setlog
duplication_validation
create_mountpoints
locatebekvol
mountbekvol
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