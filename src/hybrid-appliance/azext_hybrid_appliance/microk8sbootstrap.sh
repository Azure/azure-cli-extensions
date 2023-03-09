# Setting up microk8s cluster
echo "MicroK8s version is $MICROK8S_VERSION"
if [ -z $MICROK8S_VERSION ]; then
  echo "Microk8s version not set"
  exit 1
fi

sudo snap install microk8s --channel=$MICROK8S_VERSION --classic
sudo microk8s start
sudo microk8s config > ~/.kube/config
sudo microk8s enable dns
sudo microk8s enable rbac
sudo microk8s enable metrics-server
echo "Microk8s cluster provisioned"

if grep -q "encryption-provider-config" "/var/snap/microk8s/current/args/kube-apiserver"; then
  echo "Encryption already enabled"
else
  echo "Enabling encryption at rest"
  # Enable encryption at rest
  key=$(head -c 32 /dev/urandom | base64)
  currDir=`pwd`
  sudo cat > $currDir/encryptionConfig.yaml <<EOF
  apiVersion: apiserver.config.k8s.io/v1
  kind: EncryptionConfiguration
  resources:
    - resources:
      - secrets
      providers:
      - aescbc:
          keys:
          - name: k8s-crypto
            secret: $key
      - identity: {}
EOF
  echo --encryption-provider-config=$currDir/encryptionConfig.yaml >> /var/snap/microk8s/current/args/kube-apiserver
  sudo systemctl restart snap.microk8s.daemon-kubelite
  sudo microk8s start
  sudo microk8s kubectl get secrets --all-namespaces -o json | sudo microk8s kubectl replace -f -
fi

# This is needed before running the connectedk8s connect command to allow the cluster to come to a completely running state
# Without this, the prechecks fail intermittently
echo "Sleeping for 60 seconds to allow cluster to get completely ready"
sleep 60