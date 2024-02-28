# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import json
import sys, argparse

def connect_single_volume(resource_group_name, elastic_san_name, volume_group_name, volume_name, number_of_sessions):
    command = f"az elastic-san volume show -e {elastic_san_name} -g {resource_group_name} -v {volume_group_name} -n {volume_name} --query storageTarget".split(' ')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode!=0:
        raise Exception('\n'.join(result.stderr.split('\n')[1:]))
    storage_target = result.stdout
    storage_target = json.loads(storage_target)
    target_iqn = storage_target["targetIqn"]
    target_portal_hostname = storage_target["targetPortalHostname"]
    target_portal_port = storage_target["targetPortalPort"]

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--resource-group")
    parser.add_argument("-e", "--elastic-san")
    parser.add_argument("-v", "--volume-group")
    parser.add_argument("-n", "--volumes", nargs='+')
    parser.add_argument("-s", "--num-of-sessions")
    args = parser.parse_args(sys.argv[1:])
    # parameters
    resource_group_name = args.resource_group if args.resource_group is not None else "test-elasticsan-rg"
    elastic_san_name = args.elastic_san if args.elastic_san is not None else "testsan"
    volume_group_name = args.volume_group if args.volume_group is not None else "testvolumegroup"
    volume_names = args.volumes if args.volumes is not None else ["testvolume1"]
    number_of_sessions = int(args.num_of_sessions) if args.num_of_sessions is not None else 2 #default 32
    for volume_name in volume_names:
        connect_single_volume(resource_group_name, elastic_san_name, volume_group_name, volume_name, number_of_sessions)
