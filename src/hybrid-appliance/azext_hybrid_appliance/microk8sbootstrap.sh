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
sudo microk8s start
sudo microk8s config > $KUBECONFIG_PATH
sudo microk8s enable dns
sudo microk8s enable rbac
sudo microk8s enable metrics-server
echo "Microk8s cluster provisioned"

if grep -q "encryption-provider-config" "/var/snap/microk8s/current/args/kube-apiserver"; then
  echo "Encryption already enabled"
else
  echo "Enabling encryption"
  echo --pod-manifest-path=/etc/kubernetes/manifests >> /var/snap/microk8s/current/args/kubelet
  sudo systemctl restart snap.microk8s.daemon-kubelite

  echo "Sleeping for 60 seconds to let all services start running"
  sleep 60

  microk8s kubectl wait --for=condition=ready pod -l component=kms-localvault -n kube-system --timeout=600s
  if [ $? -ne 0 ]; then
    echo "Failed to start the KMS plugin pod"
    exit 1
  fi

  echo --encryption-provider-config=/etc/kubernetes/encryptionconfig.yaml >> /var/snap/microk8s/current/args/kube-apiserver
  sudo systemctl restart snap.microk8s.daemon-kubelite
fi

# This is needed before running the connectedk8s connect command to allow the cluster to come to a completely running state
# Without this, the prechecks fail intermittently
echo "Sleeping for 60 seconds to allow cluster to get completely ready"
sleep 60