# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess, sys
if hasattr(__builtins__, 'raw_input'):
      input=raw_input

def check_connection(target_iqn, target_portal_hostname, target_portal_port):
    command = "sudo iscsiadm -m session".split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("utf-8")
    return "No active sessions." not in out and "{}:{},-1 {}".format(target_portal_hostname, target_portal_port, target_iqn) in out
        
def disconnect_volume(volume_name, target_iqn, target_portal_hostname, target_portal_port):    
    print('{} [{}]: Disconnecting volume'.format(volume_name, target_iqn))
    command = "sudo iscsiadm --mode node --target {} --portal {}:{} --logout".format(target_iqn, target_portal_hostname, target_portal_port).split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

class VolumeData:
    volume_name = ''
    target_iqn = ''
    target_hostname = ''
    target_port = ''
    
    def __init__(self, volume_name, target_iqn, target_hostname, target_port):
        self.volume_name = volume_name
        self.target_iqn = target_iqn
        self.target_hostname = target_hostname
        self.target_port = target_port

if __name__ == "__main__":
    value = input('\033[93m[Warning: Running this script will remove access to all the selected volumes, all existing sessions to these volumes will be disconnected. \nDo you wish to continue? [Y/Yes/N/No]:\033[00m')
    while True:
        if value.lower() == 'yes' or value.lower() == 'y':
            break
        elif value.lower() == 'no' or value.lower() == 'n':
            sys.exit(1)
        else:
            value = input('\033[93mDo you wish to continue? [Y/Yes/N/No]:\033[00m')
    
    # create VolumeData array
    volume_data = []
    # Portal team will need to modify the following lines or add/remove lines in the same format - 
    # volume_data.append(VolumeData({TargetIQN}, {TargetHostName}, {TargetPort}))

    for v in volume_data:
        # check connections, if not connected, then skip disconnection
        connected = check_connection(v.target_iqn, v.target_hostname, v.target_port)
        if not connected:
            print("{} [{}]: Skipped as this volume is not connected".format(v.volume_name, v.target_iqn))
            continue
        disconnect_volume(v.volume_name, v.target_iqn, v.target_hostname, v.target_port)
