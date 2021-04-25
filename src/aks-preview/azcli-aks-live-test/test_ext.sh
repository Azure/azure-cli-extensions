#!/bin/bash

set -eux
pwd

# activate virtualenv
source azEnv/bin/activate

# remove extension
echo "Remove existing aks-preview extension (if any)"
if az extension remove --name aks-preview || azdev extension remove aks-preview; then
    deactivate
    source azEnv/bin/activate
fi

# install latest extension
echo "Install the latest aks-preview extension and re-activate the virtualenv"
azdev extension add aks-preview
az extension list
azdev extension list | grep "aks-preview" -C 5
deactivate
source azEnv/bin/activate

# Ensure that the command index is updated by calling a specific command in aks-preview, so that all the commands defined in aks-preview are loaded correctly
# Otherwise, cold boot execution of azdev test may use the api version adopted by the acs command group in azure-cli (which may diverge from the api version used in current aks-preview)
retry_count=0
while ! az aks command invoke --help --debug && [[ $retry_count < 3 ]]
do
    retry_count=`expr $retry_count + 1`
    echo $retry_count"th retry to install aks-preview..." 
    azdev extension add aks-preview --debug
    az extension list --debug
    azdev extension list --debug | grep "aks-preview" -C 5
    deactivate
    source azEnv/bin/activate
done

# test ext
if [[ $TEST_MODE == "record" || $TEST_MODE == "all" ]]; then
    echo "Test in record mode!"
    azdev test aks-preview --no-exitfirst --xml-path ext_test.xml --discover -a "-n $PARALLELISM --json-report --json-report-file=ext_report.json --reruns 3 --capture=sys"
fi

if [[ $TEST_MODE == "live" || $TEST_MODE == "all" ]]; then
    echo "Test in live mode!"
    az login --service-principal -u $AZCLI_ALT_CLIENT_ID -p $AZCLI_ALT_CLIENT_SECRET -t $TENANT_ID
    az account set -s $AZCLI_ALT_SUBSCRIPTION_ID
    az account show
    if [[ $TEST_DIFF == true && $BUILD_REASON == "PullRequest" ]]; then
        azdev test aks-preview --live --no-exitfirst --repo=azure-cli-extensions/ --src=HEAD --tgt=origin/$SYSTEM_PULLREQUEST_TARGETBRANCH --cli-ci --xml-path ext_live_test.xml --discover -a "-n $PARALLELISM --json-report --json-report-file=ext_live_report.json --reruns 3 --capture=sys"
    else
        azdev test aks-preview --live --no-exitfirst --xml-path ext_live_test.xml --discover -a "-n $PARALLELISM --json-report --json-report-file=ext_live_report.json --reruns 3 --capture=sys"
    fi
fi
