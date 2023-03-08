if microk8s status | grep -q "microk8s is running"; then
    echo "Microk8s is running successfully"
else
    microk8s inspect
    exit 1
fi