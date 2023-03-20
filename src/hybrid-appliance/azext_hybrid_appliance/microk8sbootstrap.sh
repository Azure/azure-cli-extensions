# Setting up microk8s cluster
echo "MicroK8s version is $MICROK8S_VERSION"
if [ -z $MICROK8S_VERSION ]; then
  echo "Microk8s version not set"
  exit 1
fi

mkdir -p ~/.azure/hybrid_appliance
sudo snap install microk8s --channel=$MICROK8S_VERSION --classic
sudo microk8s start
sudo microk8s config > $KUBECONFIG_PATH
sudo microk8s enable dns
sudo microk8s enable rbac
sudo microk8s enable metrics-server
echo "Microk8s cluster provisioned"

# This is needed before running the connectedk8s connect command to allow the cluster to come to a completely running state
# Without this, the prechecks fail intermittently
echo "Sleeping for 60 seconds to allow cluster to get completely ready"
sleep 60