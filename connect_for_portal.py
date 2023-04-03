import subprocess, sys, os

def check_iscsi():
    if os.path.exists('/usr/bin/apt-get'):
        command = f"dpkg -l open-iscsi1".split(' ')
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
        command = f"dpkg -l multipath-tools1".split(' ')
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

def connect_single_volume(target_iqn, target_portal_hostname, target_portal_port, number_of_sessions):
    # try to connect, if failed then skip adding new sessions
    command = f"sudo iscsiadm -m node --targetname {target_iqn} -p {target_portal_hostname}:{target_portal_port} -l".split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode!=0:
        return 
        
    # add target and attempt to register a session
    command = f"sudo iscsiadm -m node --targetname {target_iqn} --portal {target_portal_hostname}:{target_portal_port} -o new".split(' ')
    subprocess.run(command)
    command = f"sudo iscsiadm -m node --targetname {target_iqn} -p {target_portal_hostname}:{target_portal_port} -l".split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
   
    # if a new session has been registered, need to reduce the num of sessions remaining 
    if result.returncode==0:
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
    if session_id:
        command = f"sudo iscsiadm -m session -r {session_id} --op new".split(' ')
        for i in range(number_of_sessions):
            subprocess.run(command)
            
    # maintain persistent  connection
    command = f"sudo iscsiadm -m node --targetname {target_iqn} --portal {target_portal_hostname}:{target_portal_port} --op update -n node.session.nr_sessions -v {number_of_sessions}".split(' ')
    subprocess.run(command)

if __name__ == "__main__":
    # check environment
    # iSCSI initiator
    check_iscsi()
    
    # # MPIO
    check_mpio()
    
    print("keep running")
    
    # # get parameters
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-v", "--volume-names", nargs='+')
    # parser.add_argument("-i", "--target-iqns", nargs='+')
    # parser.add_argument("-h", "--target-portal-hostnames", nargs='+')
    # parser.add_argument("-p", "--target-portal-ports", nargs='+')
    # parser.add_argument("-s", "--num-of-sessions", nargs='+')
    # args = parser.parse_args(sys.argv[1:])
    # target_iqns = args.target_iqns if args.target_iqns is not None else ["iqn.2023-03.net.windows.core.blob.ElasticSan.es-4qtreagkjzj0:testvolume1"]
    # target_portal_hostnames = args.target_portal_hostnames if args.target_portal_hostnames is not None else ["es-4qtreagkjzj0.z45.blob.storage.azure.net"]
    # target_portal_ports = args.target_portal_ports if args.target_portal_ports is not None else [3260]
    # number_of_sessions = int(args.num_of_sessions) if args.num_of_sessions is not None else 32 #default 32
    # number_of_sessions = min(32, number_of_sessions)
    
    # for volume_name in volume_names:
    #     connect_single_volume(target_iqn, target_portal_hostname, target_portal_port, volume_name, number_of_sessions)
