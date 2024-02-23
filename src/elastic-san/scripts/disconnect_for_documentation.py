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

# check if there are existing connections, if None then exit
def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = "sudo iscsiadm -m session".split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if "error" in err.decode("utf-8").lower():
        raise Exception(err)
    out = out.decode("utf-8")
    return "No active sessions." not in out and "{}:{},-1 {}".format(target_portal_hostname, target_portal_port, target_iqn) in out
        
# disconnect all sessions
def disconnect_volume(volume_name, target_iqn, target_portal_hostname, target_portal_port):    
    print('{} [{}]: Disconnecting volume'.format(volume_name, target_iqn))
    command = "sudo iscsiadm --mode node --target {} --portal {}:{} --logout".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)

if __name__ == "__main__":
    # confirm if want to continue disconnecting all sessions
    value = input('\033[93m[Warning: Running this script will remove access to all the selected volumes, all existing sessions to these volumes will be disconnected. \nDo you wish to continue? [Y/Yes/N/No]:\033[00m')
    while True:
        if value.lower() == 'yes' or value.lower() == 'y':
            break
        elif value.lower() == 'no' or value.lower() == 'n':
            sys.exit(1)
        else:
            value = input('\033[93mDo you wish to continue? [Y/Yes/N/No]:\033[00m')


    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--subscription")
    parser.add_argument("-g", "--resource-group")
    parser.add_argument("-e", "--elastic-san")
    parser.add_argument("-v", "--volume-group")
    parser.add_argument("-n", "--volumes", nargs='+')
    args = parser.parse_args(sys.argv[1:])
    
    # parameters
    subscription = args.subscription
    resource_group_name = args.resource_group
    elastic_san_name = args.elastic_san
    volume_group_name = args.volume_group
    volume_names = args.volumes
    
    if None in [resource_group_name, elastic_san_name, volume_group_name, volume_names]:
        raise Exception('Need to provide resource_group_name, elastic_san_name, volume_group_name, volume_names to connect to the ElasticSAN volume')

    for volume_name in volume_names:
        target_iqn, target_hostname, target_port = get_iqns(subscription, resource_group_name, elastic_san_name, volume_group_name, volume_name)
        # check connections, if not connected, then skip disconnection
        connected = check_connection(target_iqn, target_hostname, target_port)
        if not connected:
            print("{} [{}]: Skipped as this volume is not connected".format(v.volume_name, v.target_iqn))
            continue
        disconnect_volume(volume_name, target_iqn, target_hostname, target_port)
