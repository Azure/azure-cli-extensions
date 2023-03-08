# Setting up microk8s cluster

if [[ -z $MICROK8S_VERSION ]]; then
  echo "Microk8s version not found"
  exit 1
fi

sudo snap install microk8s --version=$MICROK8S_VERSION
sudo microk8s start
sudo microk8s status
sudo microk8s config > ~/.kube/config
sudo microk8s enable dns
sudo microk8s enable rbac
sudo microk8s enable metrics-server
echo "Microk8s cluster provisioned"
echo "Enabling encryption at rest"

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
fi

echo --encryption-provider-config=$currDir/encryptionConfig.yaml >> /var/snap/microk8s/$microk8s_extension/args/kube-apiserver
sudo systemctl restart snap.microk8s.daemon-kubelite
sudo microk8s start
sudo microk8s kubectl get secrets --all-namespaces -o json | sudo microk8s kubectl replace -f -