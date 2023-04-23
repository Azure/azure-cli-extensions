import subprocess, sys, os, argparse

def check_iscsi():
    if os.path.exists('/usr/bin/apt-get'):
        command = f"dpkg -l open-iscsi".split(' ')
    elif os.path.exists('/usr/bin/yum'):
        command = f"rpm -qa | grep iscsi-initiator-utils".split(' ')
    elif os.path.exists('/usr/bin/zypper'):
        command = f"zypper search -I open-iscsi".split(' ')
    else:
        raise OSError("cannot find a usable package manager")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stdout is None or result.stdout=='':
        value = input("\033[93mWarning: iSCSI initiator is not installed or enabled. It is required for successful execution of this connect script. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')
           
def check_mpio():
    if os.path.exists('/usr/bin/apt-get'):
        command = f"dpkg -l multipath-tools".split(' ')
    elif os.path.exists('/usr/bin/yum'):
        command = f"rpm -qa | grep device-mapper-multipath".split(' ')
    elif os.path.exists('/usr/bin/zypper'):
        command = f"zypper search -I multipath-tools".split(' ')
    else:
        raise OSError("cannot find a usable package manager")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stdout is None or result.stdout=='':
        value = input("\033[93mWarning: Multipath I/O is not installed or enabled. It is recommended for multi-session setup. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')

def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = f"sudo iscsiadm -m session".split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return f"{target_portal_hostname}:{target_portal_port},-1 {target_iqn}" in result.stdout
        
def connect_volume(volume_name, target_iqn, target_portal_hostname, target_portal_port, number_of_sessions):    
    print(f'{volume_name} [{target_iqn}]: Connecting to this volume')
    # add target and attempt to register a session
    command = f"sudo iscsiadm -m node --targetname {target_iqn} --portal {target_portal_hostname}:{target_portal_port} -o new".split(' ')
    subprocess.run(command, stdout=subprocess.DEVNULL)
    command = f"sudo iscsiadm -m node --targetname {target_iqn} -p {target_portal_hostname}:{target_portal_port} -l".split(' ')
    subprocess.run(command, stdout=subprocess.DEVNULL)
    number_of_sessions-=1

    # get session id
    command = f"sudo iscsiadm -m session".split(' ')
    sessions = subprocess.run(command, stdout=subprocess.PIPE, text=True).stdout
    for l in sessions.splitlines()[::-1]:
        s = l.split(' ')
        if s[2] == f"{target_portal_hostname}:{target_portal_port},-1" and s[3] == target_iqn:
            session_id = s[1][1:-1]
            break
        
    # register remaining sessions
    command = f"sudo iscsiadm -m session -r {session_id} --op new".split(' ')
    for i in range(number_of_sessions):
        subprocess.run(command, stdout=subprocess.DEVNULL)
            
    # maintain persistent connection
    command = f"sudo iscsiadm -m node --targetname {target_iqn} --portal {target_portal_hostname}:{target_portal_port} --op update -n node.session.nr_sessions -v {number_of_sessions}".split(' ')
    subprocess.run(command)

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
            print(f'{v.volume_name} [{v.target_iqn}]: Skipped as this volume is already connected')
            continue
        connect_volume(v.volume_name, v.target_iqn, v.target_hostname, v.target_port, v.num_session)
