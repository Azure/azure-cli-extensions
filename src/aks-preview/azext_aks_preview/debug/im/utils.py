import subprocess


def get_configmap(namespace, name):
    return subprocess.check_output(
        ["kubectl", "get", "cm", "-n", namespace, name, "-o", "json"],
        universal_newlines=True,
    )
