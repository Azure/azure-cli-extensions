# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess, sys, os
if hasattr(__builtins__, 'raw_input'):
      input = raw_input

package_manager = ''
if os.path.exists('/usr/bin/apt-get'):
    package_manager = 'apt'
elif os.path.exists('/usr/bin/yum'):
    package_manager = 'yum'
elif os.path.exists('/usr/bin/zypper'):
    package_manager = 'zypper'
else:
    raise OSError("cannot find a usable package manager")

def check_iscsi():
    if package_manager == 'apt':
        command = "dpkg -l open-iscsi".split(' ')
    elif package_manager == 'yum':
        command = "rpm -q iscsi-initiator-utils".split(' ')
    elif package_manager == 'zypper':
        command = "zypper search -i open-iscsi".split(' ')
    else:
        raise OSError("cannot find a usable package manager")
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("utf-8")
    if (package_manager == "apt" and "ii  open-iscsi" not in out) or (package_manager == 'yum' and "iscsi-initiator-utils is not installed" in out) or (package_manager == 'zypper' and "open-iscsi" not in out):
        value = input("\033[93mWarning: iSCSI initiator is not installed or enabled. It is required for successful execution of this connect script. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')
           
def check_mpio():
    if package_manager == 'apt':
        command = "dpkg -l multipath-tools".split(' ')
    elif package_manager == 'yum':
        command = "rpm -q device-mapper-multipath".split(' ')
    elif package_manager == 'zypper':
        command = "zypper search -i multipath-tools".split(' ')
    else:
        raise OSError("cannot find a usable package manager")
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("utf-8")
    if (package_manager == "apt" and "ii  multipath-tools" not in out) or (package_manager == 'yum' and "device-mapper-multipath is not installed" in out) or (package_manager == 'zypper' and "multipath-tools" not in out):
        value = input("\033[93mWarning: Multipath I/O is not installed or enabled. It is recommended for multi-session setup. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')

def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = "sudo iscsiadm -m session".split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("utf-8")
    return "No active sessions." not in out and "{}:{},-1 {}".format(target_portal_hostname, target_portal_port, target_iqn) in out
        
def connect_volume(volume_name, target_iqn, target_portal_hostname, target_portal_port, number_of_sessions):    
    print("{} [{}]: Connecting to this volume".format(volume_name, target_iqn))
    # add target and attempt to register a session
    command = "sudo iscsiadm -m node --targetname {} --portal {}:{} -o new".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    command = "sudo iscsiadm -m node --targetname {} -p {}:{} -l".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    # get session id
    command = "sudo iscsiadm -m session".split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sessions, _ = p.communicate()
    sessions = sessions.decode("utf-8")
    session_id = ""
    for l in sessions.splitlines()[::-1]:
        s = l.split(' ')
        if s[2] == "{}:{},-1".format(target_portal_hostname, target_portal_port) and s[3] == target_iqn:
            session_id = s[1][1:-1]
            break

    # register remaining sessions
    command = "sudo iscsiadm -m session -r {} --op new".format(session_id).split(' ')
    for i in range(number_of_sessions-1):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
            
    # maintain persistent connection
    command = "sudo iscsiadm -m node --targetname {} --portal {}:{} --op update -n node.session.nr_sessions -v {}".format(target_iqn, target_portal_hostname, target_portal_port, number_of_sessions).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    # enable data protection
    command = "sudo iscsiadm -m node --targetname {} --portal {}:{} --op update -n node.conn[0].iscsi.HeaderDigest " \
              "-v CRC32C".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    command = "sudo iscsiadm -m node --targetname {} --portal {}:{} --op update -n node.conn[0].iscsi.DataDigest " \
              "-v CRC32C".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

class VolumeData:
    volume_name = ''
    target_iqn = ''
    target_hostname = ''
    target_port = ''
    num_session = 32
    
    def __init__(self, volume_name, target_iqn, target_hostname, target_port, num_session=32):
        self.volume_name = volume_name
        self.target_iqn = target_iqn
        self.target_hostname = target_hostname
        self.target_port = target_port
        self.num_session = min(32, int(num_session))

if __name__ == "__main__":
    # iSCSI initiator
    check_iscsi()
    
    # MPIO
    check_mpio()
    
    # create VolumeData array
    volume_data = []
    # Portal team will need to modify the following lines or add/remove lines in the same format - 
    # volume_data.append(VolumeData({VolumeName},{TargetIQN}, {TargetHostName}, {TargetPort}, {Number of sessions}))

    for v in volume_data:
        # check connections, if connected, then skip adding new connections
        connected = check_connection(v.target_iqn, v.target_hostname, v.target_port)
        if connected:
            print('{} [{}]: Skipped as this volume is already connected'.format(v.volume_name, v.target_iqn))
            continue
        connect_volume(v.volume_name, v.target_iqn, v.target_hostname, v.target_port, v.num_session)
