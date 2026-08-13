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
		exit 1
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
		exit 1
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

# GPT type GUIDs that can never hold the root filesystem.
biosboot_guid=21686148-6449-6e6f-744e-656564454649
efi_guid=c12a7328-f81f-11d2-ba4b-00a0c93ec93b

part_type () {
	# lsblk gained PARTTYPE in util-linux 2.25; RHEL 7 rescue images ship 2.23.
	local pt
	pt=`lsblk -dno PARTTYPE "$1" 2>/dev/null | tr -d ' '`
	if [ -z "${pt}" ]
	then
		pt=`blkid -p -s PART_ENTRY_TYPE -o value "$1" 2>/dev/null`
	fi
	echo "${pt}" | tr 'A-Z' 'a-z'
}

classify_data_parts () {
	trapper
	echo "`date` Classifying the partitions on the data drive" >> ${logpath}/${logfile}
	export boot_candidates=""
	export root_candidates=""
	local part fstype parttype
	for part in `lsblk ${data_disk} -l -n -p -o NAME,TYPE | awk '$2=="part"{print $1}'`
	do
		parttype=`part_type ${part}`
		if [ "${parttype}" = "${biosboot_guid}" ] || [ "${parttype}" = "${efi_guid}" ]
		then
			echo "`date` ${part} skipped, BIOS boot or EFI system partition" >> ${logpath}/${logfile}
			continue
		fi
		fstype=`lsblk -dno FSTYPE ${part} 2>/dev/null | tr -d ' '`
		case "${fstype}" in
			ext2|ext3|ext4|xfs)
				# A readable Linux filesystem cannot be the ADE root, so it is a /boot candidate.
				boot_candidates="${boot_candidates} ${part}" ;;
			""|crypto_LUKS)
				# ADE root: a detached header leaves no signature, an inline header shows crypto_LUKS.
				root_candidates="${root_candidates} ${part}" ;;
			*)
				echo "`date` ${part} skipped, fstype ${fstype}" >> ${logpath}/${logfile} ;;
		esac
	done
	echo "`date` Boot candidates on the data drive: ${boot_candidates}" >> ${logpath}/${logfile}
	echo "`date` Root candidates on the data drive: ${root_candidates}" >> ${logpath}/${logfile}
}

locate_mount_data_boot () {
	trapper
	echo "`date` Looking for the boot partition that carries the LUKS header" >> ${logpath}/${logfile}
	# Probe the candidates one at a time, read only. The previous version mounted every
	# partition read-write just to run `find /tmp -name osluksheader`, which replays the
	# journal of a filesystem that belongs to a VM that already failed to boot.
	export boot_part=""
	export luksheaderpath=""
	probe_mnt=/tmp/vmrepair_headerprobe
	mkdir -p ${probe_mnt}
	for part in ${boot_candidates}
	do
		echo "`date` Probing ${part} for luks/osluksheader" >> ${logpath}/${logfile}
		mount -o ro,noload ${part} ${probe_mnt} 2>/dev/null \
			|| mount -o ro,norecovery ${part} ${probe_mnt} 2>/dev/null \
			|| mount -o ro ${part} ${probe_mnt} 2>/dev/null \
			|| continue
		if [ -f ${probe_mnt}/luks/osluksheader ]
		then
			export boot_part=${part}
			export luksheaderpath=/investigateboot/luks/osluksheader
			umount ${probe_mnt} >> ${logpath}/${logfile} 2>&1
			break
		fi
		umount ${probe_mnt} >> ${logpath}/${logfile} 2>&1
	done
	rmdir ${probe_mnt} 2>/dev/null
	if [ -z "${boot_part}" ]
	then
		echo "`date` No partition on the data disk carries luks/osluksheader, cannot continue" >> ${logpath}/${logfile}
		exit 1
	fi
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
	#adding below lines to make sure that volume groups are activated before trying to mount.
	vgs >>  ${logpath}/${logfile}
	vgchange -ay rootvg >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/rootlv /investigateroot >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/varlv /investigateroot/var/ >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/homelv /investigateroot/home >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/usrlv /investigateroot/usr >> ${logpath}/${logfile}
	${mount_cmd} /dev/rootvg/tmplv /investigateroot/tmp >> ${logpath}/${logfile}
	lsblk -f >> ${logpath}/${logfile}
}

unlock_root () {
	trapper
	# The root partition is identified by opening it: if the decrypted content is not a
	# filesystem or an LVM PV, that candidate was not the root.
	export root_part=""
	export lvm_part=""
	for part in ${root_candidates}
	do
		echo "`date` unlocking root with command: cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${part} osencrypt" >> ${logpath}/${logfile}
		cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName --header /investigateboot/luks/osluksheader ${part} osencrypt >> ${logpath}/${logfile} 2>&1 || continue
		udevadm settle >/dev/null 2>&1
		inner=`blkid -p -s TYPE -o value /dev/mapper/osencrypt 2>/dev/null`
		if [ -z "${inner}" ]
		then
			inner=`lsblk -dno FSTYPE /dev/mapper/osencrypt 2>/dev/null | tr -d ' '`
		fi
		echo "`date` ${part} opened, decrypted content is '${inner}'" >> ${logpath}/${logfile}
		case "${inner}" in
			LVM2_member)
				export root_part=${part}
				export lvm_part=${part}
				echo "`date` LVM found on the data disk" >> ${logpath}/${logfile}
				echo "`date` The OS partition on the data drive is ${root_part}" >> ${logpath}/${logfile}
				return 0 ;;
			ext2|ext3|ext4|xfs|btrfs)
				export root_part=${part}
				echo "`date` LVM not found on the data disk" >> ${logpath}/${logfile}
				echo "`date` The OS partition on the data drive is ${root_part}" >> ${logpath}/${logfile}
				return 0 ;;
		esac
		echo "`date` ${part} did not decrypt to a usable root, trying the next candidate" >> ${logpath}/${logfile}
		cryptsetup luksClose osencrypt >> ${logpath}/${logfile} 2>&1
	done
	echo "`date` None of the root candidates could be unlocked, cannot continue" >> ${logpath}/${logfile}
	exit 1
}

verify_root_unlock () {
	trapper
	echo "`date` Verifying osencrypt unlock" >> ${logpath}/${logfile}
	lsblk -f  | grep osencrypt >> ${logpath}/${logfile}
	if [ $? -gt 0 ]
	then
		        echo "`date` device osencrypt was not found" >> ${logpath}/${logfile}
			        exit 1
			else
				        echo "`date` device osencrypt found" >> ${logpath}/${logfile}
				fi
}

mount_encrypted () {
	trapper
	echo "`date` Mounting root" >> ${logpath}/${logfile}
	if [ -z "${lvm_part}" ]
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
install_required_packages()
{
	echo "`date` Checking about the required packages and instal the misssing ones" >> ${logpath}/${logfile}
	echo "`date` Checking the distro of the recovery VM .." >> ${logpath}/${logfile}
	output=`which apt`
	if [ $? -eq 0 ]
	then
		echo "`date` This is ubuntu VM" >> ${logpath}/${logfile}
		apt-get install -y cryptsetup lvm2 >> ${logpath}/${logfile}
	else
		output=`which zypper`
		if [ $? -eq 0 ]
		then
			echo "`date` This is a sles VM" >> ${logpath}/${logfile}
			zypper --non-interactive --no-refresh install cryptsetup lvm2
		else
			echo "`date` This a yum based distro"  >> ${logpath}/${logfile}
			yum install -y cryptsetup lvm2
		fi
	fi
}

setlog
install_required_packages
duplication_validation
create_mountpoints
locatebekvol
mountbekvol
get_data_disk
check_local_lvm
classify_data_parts
mount_cmd
locate_mount_data_boot
mount_boot
unlock_root
verify_root_unlock
mount_encrypted
remount_boot