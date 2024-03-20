# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess, sys, os, argparse, json, time
# for compatibility between python2 and python3 
if hasattr(__builtins__, 'raw_input'):
      input = raw_input

# determine os and package manager type
package_manager = ''
if os.path.exists('/usr/bin/apt-get'):
    package_manager = 'apt'
elif os.path.exists('/usr/bin/yum'):
    package_manager = 'yum'
elif os.path.exists('/usr/bin/zypper'):
    package_manager = 'zypper'
else:
    raise OSError("cannot find a usable package manager")

# check if iSCSI initiator is installed
def check_iscsi():
    # check for each type of package manager
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
    
    # if not found/installed, select to exit or continue anyway
    if (package_manager == "apt" and "ii  open-iscsi" not in out) or (package_manager == 'yum' and "iscsi-initiator-utils is not installed" in out) or (package_manager == 'zypper' and "open-iscsi" not in out):
        value = input("\033[93mWarning: iSCSI initiator is not installed or enabled. It is required for successful execution of this connect script. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')
           
# check if multipath-tools is installed
def check_mpio():
    # check for each type of package manager
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
    
    # if not found/installed, select to exit or continue anyway
    if (package_manager == "apt" and "ii  multipath-tools" not in out) or (package_manager == 'yum' and "device-mapper-multipath is not installed" in out) or (package_manager == 'zypper' and "multipath-tools" not in out):
        value = input("\033[93mWarning: Multipath I/O is not installed or enabled. It is recommended for multi-session setup. \nDo you wish to terminate the script to install it? \n[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m")
        while True:
            if value.lower() == 'yes' or value.lower() == 'y':
                sys.exit(1)
            elif value.lower() == 'no' or value.lower() == 'n':
                break
            else:
                value = input('\033[93m[Y/Yes to terminate; N/No to proceed with rest of the steps]:\033[00m')

# check if azure cli is installed
def check_azcli():
    # check for each type of package manager
    if package_manager == 'apt':
        command = "dpkg -l azure-cli".split(' ')
    elif package_manager == 'yum':
        command = "rpm -q azure-cli".split(' ')
    elif package_manager == 'zypper':
        command = "zypper search -i azure-cli".split(' ')
    else:
        raise OSError("cannot find a usable package manager")
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("utf-8")
    
    # if not found/installed, exit
    if (package_manager == "apt" and "ii  azure-cli" not in out) or (package_manager == 'yum' and "azure-cli is not installed" in out) or (package_manager == 'zypper' and "azure-cli" not in out):
        print("\033[93mWarning: Azure CLI is not installed or enabled. It is required for successful execution of this connect script. \n You need to install by following `https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux` and run:\n `az extension add -n elastic-san`\n `az login`\033[00m")
        sys.exit(1)
    
# get iqn info from the ElasticSAN
def get_iqns(subscription, resource_group_name, elastic_san_name, volume_group_name, volume_name):
    check_azcli()
    subscription = " --subscription "+subscription if subscription is not None else ""
    command = "az elastic-san volume show -g {} -e {} -v {} -n {} --query storageTarget{}".format(resource_group_name, elastic_san_name, volume_group_name, volume_name, subscription).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # timeout in case the extension is not installed and prompts the user to install
    timeout = 10
    while p.poll() is None and timeout > 0:
     time.sleep(1)
     timeout -= 1
    if timeout<=0:
        raise Exception('Command took longer than 10s')
    out, err = p.communicate()
    if "error" in err.decode("utf-8").lower():
        raise Exception(err)
    out = out.decode("utf-8")
    storage_target = json.loads(out)
    target_iqn = storage_target["targetIqn"]
    target_portal_hostname = storage_target["targetPortalHostname"]
    target_portal_port = storage_target["targetPortalPort"]
    return target_iqn, target_portal_hostname, target_portal_port

# check if there are existing connections, if so exit and not connect again
def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = "sudo iscsiadm -m session".split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if "error" in err.decode("utf-8").lower():
        raise Exception(err)
    out = out.decode("utf-8")
    return "No active sessions." not in out and "{}:{},-1 {}".format(target_portal_hostname, target_portal_port, target_iqn) in out
        
# connect to volume with the specified number of sessions
def connect_volume(volume_name, target_iqn, target_portal_hostname, target_portal_port, number_of_sessions):
    print("{} [{}]: Connecting to this volume".format(volume_name, target_iqn))
    # add target and attempt to register a session
    command = "sudo iscsiadm -m node --targetname {} --portal {}:{} -o new".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)
    command = "sudo iscsiadm -m node --targetname {} -p {}:{} -l".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)

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

if __name__ == "__main__":
    # check if iSCSI initiator is installed
    check_iscsi()
    
    # check if multipath-tools is installed
    check_mpio()
    
    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--subscription")
    parser.add_argument("-g", "--resource-group")
    parser.add_argument("-e", "--elastic-san")
    parser.add_argument("-v", "--volume-group")
    parser.add_argument("-n", "--volumes", nargs='+')
    parser.add_argument("-s", "--num-of-sessions")
    args = parser.parse_args(sys.argv[1:])
    
    # parameters
    subscription = args.subscription
    resource_group_name = args.resource_group
    elastic_san_name = args.elastic_san
    volume_group_name = args.volume_group
    volume_names = args.volumes
    number_of_sessions = min(32, int(args.num_of_sessions)) if args.num_of_sessions is not None else 32 # default is 32, also the maximum allowed number of sessions
    
    if None in [resource_group_name, elastic_san_name, volume_group_name, volume_names]:
        raise Exception('Need to provide resource_group_name, elastic_san_name, volume_group_name, volume_names to connect to the ElasticSAN volume')

    for volume_name in volume_names:
        # check connections, if connected, then skip adding new connections
        target_iqn, target_hostname, target_port = get_iqns(subscription, resource_group_name, elastic_san_name, volume_group_name, volume_name)
        connected = check_connection(target_iqn, target_hostname, target_port)
        if connected:
            print('{} [{}]: Skipped as this volume is already connected'.format(volume_name, target_iqn))
            continue
        # if not already connected, proceed with connection 
        connect_volume(volume_name, target_iqn, target_hostname, target_port, number_of_sessions)
