Describe 'Pre-onboarding Diagnostic Telemetry Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1

        $script:OriginalCorefile = kubectl get configmap coredns -n kube-system -o jsonpath='{.data.Corefile}' 2>&1

        function Invoke-RestoreCoreDNS {
            if (-not $script:OriginalCorefile) { return }
            $patch = @{data = @{Corefile = $script:OriginalCorefile}} | ConvertTo-Json -Compress -Depth 5
            kubectl patch configmap coredns -n kube-system --type merge -p $patch | Out-Null
            kubectl rollout restart deployment/coredns -n kube-system | Out-Null
            kubectl rollout status deployment/coredns -n kube-system --timeout=60s | Out-Null
        }

        function Invoke-CoreDNSBlock {
            param([string[]]$Hosts)
            $hostsBlock = ($Hosts | ForEach-Object { "      192.0.2.1 $_" }) -join "`n"
            $newCorefile = @"
.:53 {
    errors
    ready
    health {
      lameduck 5s
    }
    hosts {
$hostsBlock
      fallthrough
    }
    kubernetes cluster.local in-addr.arpa ip6.arpa {
      pods insecure
      fallthrough in-addr.arpa ip6.arpa
      ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
    import custom/*.override
    template ANY ANY internal.cloudapp.net {
      match "^(?:[^.]+\.){4,}internal\.cloudapp\.net\.$"
      rcode NXDOMAIN
      fallthrough
    }
    template ANY ANY reddog.microsoft.com {
      rcode NXDOMAIN
    }
}
import custom/*.server
"@
            $patch = @{data = @{Corefile = $newCorefile}} | ConvertTo-Json -Compress -Depth 5
            kubectl patch configmap coredns -n kube-system --type merge -p $patch | Out-Null
            kubectl rollout restart deployment/coredns -n kube-system | Out-Null
            kubectl rollout status deployment/coredns -n kube-system --timeout=60s | Out-Null
        }

        function Invoke-ApplyBadCRD {
            param([string]$CRDName)
            $plural = ($CRDName -split '\.')[0]
            $manifest = @"
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: $CRDName
  annotations:
    meta.helm.sh/release-name: some-other-component
    meta.helm.sh/release-namespace: default
spec:
  group: clusterconfig.azure.com
  names:
    kind: FakeResource
    listKind: FakeResourceList
    plural: $plural
    singular: fakeresource
  scope: Cluster
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
"@
            $manifest | kubectl apply -f - 2>&1 | Out-Null
        }

        function Invoke-ApplyPodQuota {
            kubectl create namespace azure-arc-release --dry-run=client -o yaml | kubectl apply -f - 2>&1 | Out-Null
            $quota = @"
apiVersion: v1
kind: ResourceQuota
metadata:
  name: block-pods
  namespace: azure-arc-release
spec:
  hard:
    pods: "0"
"@
            $quota | kubectl apply -f - 2>&1 | Out-Null
        }
    }

    It 'MCR outbound block triggers prediagnostics-failure telemetry' {
        $clusterName = "prediag-test-mcr"
        Invoke-CoreDNSBlock -Hosts @("mcr.microsoft.com")
        $output = az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION 2>&1
        $? | Should -BeFalse
        ($output -join "`n") | Should -Match "Pre-onboarding Diagnostic|pre-checks"
        Invoke-RestoreCoreDNS
        az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $clusterName --force -y 2>&1 | Out-Null
    }

    It 'Entra endpoint block triggers prediagnostics-failure telemetry' {
        $clusterName = "prediag-test-entra"
        try {
            Invoke-CoreDNSBlock -Hosts @("login.microsoftonline.com")
            $output = az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION 2>&1
            $? | Should -BeFalse
            ($output -join "`n") | Should -Match "Pre-onboarding Diagnostic|pre-checks"
        }
        finally {
            Invoke-RestoreCoreDNS
            az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $clusterName --force -y 2>&1 | Out-Null
        }
    }

    It 'Combined MCR and Entra block triggers prediagnostics-failure telemetry' {
        $clusterName = "prediag-test-combined"
        try {
            Invoke-CoreDNSBlock -Hosts @("mcr.microsoft.com", "login.microsoftonline.com")
            $output = az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION 2>&1
            $? | Should -BeFalse
            ($output -join "`n") | Should -Match "Pre-onboarding Diagnostic|pre-checks"
        }
        finally {
            Invoke-RestoreCoreDNS
            az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $clusterName --force -y 2>&1 | Out-Null
        }
    }

    It 'CRD ownership conflict triggers prediagnostics-failure telemetry' {
        $clusterName = "prediag-test-crd"
        $crdName = "extensionconfigs.clusterconfig.azure.com"
        Invoke-ApplyBadCRD $crdName
        $output = az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION 2>&1
        $? | Should -BeFalse
        ($output -join "`n") | Should -Match "Pre-onboarding Diagnostic|pre-checks"
        kubectl delete crd $crdName --ignore-not-found=true 2>&1 | Out-Null
        az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $clusterName --force -y 2>&1 | Out-Null
    }

    It 'Job not schedulable triggers job-execution-error telemetry' {
        $clusterName = "prediag-test-nojob"
        Invoke-ApplyPodQuota
        $output = az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION 2>&1
        $? | Should -BeFalse
        ($output -join "`n") | Should -Match "Pre-onboarding Diagnostic|pre-checks"
        kubectl delete resourcequota block-pods -n azure-arc-release --ignore-not-found=true 2>&1 | Out-Null
        az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $clusterName --force -y 2>&1 | Out-Null
    }

    It 'Happy path has no prediagnostics failure telemetry' {
        $clusterName = "prediag-test-happy"
        az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $clusterName -l $ARC_LOCATION --no-wait
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        $n = 0
        do {
            $output = az connectedk8s show -n $clusterName -g $ENVCONFIG.resourceGroup
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Provisioning State: $provisioningState"
            if ($provisioningState -eq $SUCCEEDED) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Delete the connected instance' {
        az connectedk8s delete -g $ENVCONFIG.resourceGroup -n "prediag-test-happy" --force -y
        $? | Should -BeTrue

        az connectedk8s show -n "prediag-test-happy" -g $ENVCONFIG.resourceGroup
        $? | Should -BeFalse
    }
}
