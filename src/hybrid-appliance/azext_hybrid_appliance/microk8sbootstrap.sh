printError() {
  RED='\033[0;31m'
  NC='\033[0m' # No Color
  printf "${RED}$1${NC}\n"
}

printWarning() {
  YELLOW='\033[0;33m'
  NC='\033[0m' # No Color
  printf "${YELLOW}$1${NC}\n"
}

printSuccess() {
  GREEN='\033[0;92m'
  NC='\033[0m' # No Color
  printf "${GREEN}$1${NC}\n"
}

# Setting up microk8s cluster
if [ -z $MICROK8S_VERSION ]; then
  echo "Microk8s version not set"
  exit 1
fi

mkdir -p ~/.azure/hybrid_appliance
mkdir -p /etc/kubernetes/manifests
cp ~/.azure/cliextensions/hybrid-appliance/azext_hybrid_appliance/encryptionconfig.yaml /etc/kubernetes
cp ~/.azure/hybrid_appliance/kms.yaml /etc/kubernetes/manifests

sudo snap install microk8s --channel=$MICROK8S_VERSION --classic
microk8s start
sleep 15 # The node is not immediately visible in microk8s
microk8s kubectl wait --for=condition=Ready nodes --all --timeout=600s
if [ $? != 0 ]; then
  printError "The nodes of the kubernetes cluster failed to get ready in time."
  exit 1
fi
microk8s config > $KUBECONFIG_PATH
echo "Enabling DNS in the microk8s cluster"
microk8s enable dns >> $LOG_FILE 2>&1
printSuccess "Successfully enabled DNS"
echo "Enabling rbac in the microk8s cluster"
microk8s enable rbac >> $LOG_FILE 2>&1
printSuccess "Successfully enabled rbac"
echo "Enabling metrics server in the microk8s cluster"
microk8s enable metrics-server >> $LOG_FILE 2>&1
printSuccess "Successfully enabled the metrics server"
printSuccess "Microk8s cluster provisioned"

if grep -q "encryption-provider-config" "/var/snap/microk8s/current/args/kube-apiserver"; then
  echo "Encryption already enabled"
else
  echo "Enabling secret encryption in the kubernetes cluster"
  echo --pod-manifest-path=/etc/kubernetes/manifests >> /var/snap/microk8s/current/args/kubelet
  sudo systemctl restart snap.microk8s.daemon-kubelite

  echo "Sleeping for 60 seconds to let all services start running"
  sleep 60

  microk8s kubectl wait --for=condition=ready pod -l component=kms-localvault -n kube-system --timeout=600s
  if [ $? -ne 0 ]; then
    printError "Failed to enable secret encryption"
    exit 1
  fi

  echo --encryption-provider-config=/etc/kubernetes/encryptionconfig.yaml >> /var/snap/microk8s/current/args/kube-apiserver
  sudo systemctl restart snap.microk8s.daemon-kubelite
  printSuccess "Successfully enabled secret encryption"
fi

# This is needed before running the connectedk8s connect command to allow the cluster to come to a completely running state
# Without this, the prechecks fail intermittently
echo "Sleeping for 60 seconds to allow cluster to get completely ready"
sleep 60