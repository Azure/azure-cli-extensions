from subprocess import check_output, PIPE, STDOUT, Popen

def test_connect(cc_name="testCC", rg_name="arpgucc", loc="eastus2euap"):
    connect_command = ["az", "connectedk8s", "connect"]
    connect_command.extend(["-n", cc_name, "-g", rg_name, "-l" , loc])
    p = Popen(connect_command, stderr=STDOUT, stdout=PIPE, shell=True, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()


def test_show(cc_name="testCC", rg_name="arpgucc"):
    show_command = ["az", "connectedk8s", "show"]
    show_command.extend(["-n", cc_name, "-g", rg_name])
    p = Popen(show_command, stderr=STDOUT, stdout=PIPE, shell=True, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()


def test_delete(cc_name="testCC", rg_name="arpgucc"):
    delete_cmd = ["az", "connectedk8s", "delete"]
    delete_cmd.extend(["-n", cc_name, "-g", rg_name, "-y"])
    p = Popen(delete_cmd, stderr=STDOUT, stdout=PIPE, shell=True, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()

def test_pods(kube_config=None, kube_context=None):
    kubectl_prior = ["kubectl"]
    if kube_config:
        kubectl_prior.extend(["--kubeconfig", kube_config])
    if kube_context:
        kubectl_prior.extend(["--context", kube_context])

    pod_cmd = kubectl_prior + ["get", "pods", "-A"]
    p = Popen(pod_cmd, stderr=STDOUT, stdout=PIPE, shell=True, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        print(line)
    p.stdout.close()
    p.wait()


def main():
    test_connect()
    for _ in range(1, 4):
        test_show()
        test_pods()
    test_delete()

main()
