import subprocess, sys, argparse

def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = f"sudo iscsiadm -m session".split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return f"{target_iqn}" in result.stdout
        
def disconnect_volume(target_iqn, target_portal_hostname, target_portal_port):    
    print(f'Volume name [{target_iqn}]: Disconnecting volume')
    command = f"sudo iscsiadm --mode node --target {target_iqn} --portal {target_portal_hostname}:{target_portal_port} --logout".split(' ')
    subprocess.run(command, stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    value = input('\033[93m[Warning: Running this script will remove access to all the selected volumes, all existing sessions to these volumes will be disconnected. \nDo you wish to continue? [Y/Yes/N/No]:\033[00m')
    while True:
        if value.lower() == 'yes' or value.lower() == 'y':
            break
        elif value.lower() == 'no' or value.lower() == 'n':
            sys.exit(1)
        else:
            value = input('\033[93mDo you wish to continue? [Y/Yes/N/No]:\033[00m')
    
    # get parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--target-iqns", nargs='+')
    parser.add_argument("-n", "--target-portal-hostnames", nargs='+')
    parser.add_argument("-p", "--target-portal-ports", nargs='+')
    args = parser.parse_args(sys.argv[1:])
    target_iqns = args.target_iqns if args.target_iqns is not None else ["iqn.2023-03.net.windows.core.blob.ElasticSan.es-4qtreagkjzj0:testvolume1"]
    target_portal_hostnames = args.target_portal_hostnames if args.target_portal_hostnames is not None else ["es-4qtreagkjzj0.z45.blob.storage.azure.net"]
    target_portal_ports = args.target_portal_ports if args.target_portal_ports is not None else [3260]
    
    for i, target_iqn in enumerate(target_iqns):
        # check connections, if not connected, then skip disconnection
        connected = check_connection(target_iqn, target_portal_hostnames[i], target_portal_ports[i])
        if not connected:
            print(f'Volume name [{target_iqn}]: Skipped as this volume is not connected')
            continue
        disconnect_volume(target_iqn, target_portal_hostnames[i], target_portal_ports[i])
