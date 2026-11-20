file_path=$(az connectedk8s troubleshoot -g $RESOURCE_GROUP -n $APPLIANCE_NAME --kube-config $KUBECONFIG_PATH 2>&1 | grep -o "path:.*.")
if [ $? -ne 0 ]; then
    echo "Failed to run troubleshoot to collect the connected cluster logs"
    exit 1
fi

if [ -z "$file_path" ]; then
    echo "Failed to extract file name for connectedk8s troubleshoot. The required logs can be found under ~/.azure"
    exit 1
fi

file_path=${file_path:5} # Remove the "path:" at the beginning
file_path=${file_path%" ."} # Remove the " ." at the end
cp -r $file_path $TROUBLESHOOT_DIRECTORY