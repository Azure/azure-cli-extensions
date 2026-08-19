inspect_output=$(microk8s inspect)
if [ $? -ne 0 ]; then
    echo "Failed to run microk8s inspect"
    exit 1
fi
file_path=$(echo $inspect_output | grep -o '/var/.*.tar.gz')
if [ $? -ne 0 ]; then
    echo "Failed to extract file path. The required logs can be found under /var/snap/microk8s/current"
    exit 1
fi
cp $file_path $TROUBLESHOOT_DIRECTORY/inspection_report.tar.gz
