# Setting up microk8s cluster
microk8s_extension=4595
curl https://kkanukollusa.blob.core.windows.net/snaps/microk8s_$microk8s_extension.assert > microk8s_$microk8s_extension.assert
curl https://kkanukollusa.blob.core.windows.net/snaps/microk8s_$microk8s_extension.snap > microk8s_$microk8s_extension.snap
sudo snap ack microk8s_$microk8s_extension.assert
sudo snap install microk8s_$microk8s_extension.snap --classic
sudo microk8s start
sudo microk8s status
sudo microk8s config > ~/.kube/config
sudo microk8s enable dns
sudo microk8s enable rbac
echo "Microk8s cluster provisioned"
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
echo --encryption-provider-config=$currDir/encryptionConfig.yaml >> /var/snap/microk8s/$microk8s_extension/args/kube-apiserver
sudo systemctl restart snap.microk8s.daemon-kubelite
sudo microk8s start
sudo microk8s kubectl get secrets --all-namespaces -o json | sudo microk8s kubectl replace -f -