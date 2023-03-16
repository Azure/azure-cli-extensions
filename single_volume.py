import subprocess
import json
resource_group_name = "test-elasticsan-rg"
elastic_san_name = "testsan"
volume_group_name = "testvolumegroup"
volume_name = "testvolume1"
number_of_sessions=3 #default 32
# enable_multi_path=True
command = f"az elastic-san volume show -e {elastic_san_name} -g {resource_group_name} -v {volume_group_name} -n {volume_name} --query storageTarget".split(' ')
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
if result is not None:
    storage_target = result.stdout
storage_target = json.loads(storage_target)
target_iqn = storage_target["targetIqn"]
target_portal_hostname = storage_target["targetPortalHostname"]
target_portal_port = storage_target["targetPortalPort"]

# command = f"sudo iscsiadm -m node --targetname {target_iqn} --portal {target_portal_hostname}:{target_portal_port} -o new".split(' ')
# subprocess.run(command)
# command = f"sudo iscsiadm -m node --targetname {target_iqn} -p {target_portal_hostname}:{target_portal_port} -l".split(' ')
# subprocess.run(command)
command = f"sudo iscsiadm -m session".split(' ')
sessions = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
for l in sessions.splitlines():
    s = l.split(' ')
    if s[2] == f"{target_portal_hostname}:{target_portal_port},-1" and s[3] == target_iqn:
        session_id = s[1][1:-1]
print(session_id)