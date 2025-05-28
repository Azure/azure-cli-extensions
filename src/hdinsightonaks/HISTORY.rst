.. :changelog:

Release History
===============
1.0.0b3
++++++
* `az hdinsight-on-aks clusterpool upgrade history`: Support list a list of upgrade history.
* `az hdinsight-on-aks cluster upgrade history`: Support list a list of upgrade history.
* `az hdinsight-on-aks cluster upgrade rollback`: Support manual rollback upgrade for a cluster.
* `az hdinsight-on-aks cluster library manage`: Support manage libraries on HDInsight on AKS cluster.
* `az hdinsight-on-aks cluster create`: Support for cluster creation using multiple identity above version 1.2.0 use --identity-list.

1.0.0b2
++++++
* [Breaking Change] 'az hdinsight-on-aks cluster show-instance-view': Modified to 'az hdinsight-on-aks cluster instance-view show'.
* 'az hdinsight-on-aks clusterpool create': Support create cluster pool with user network profile with --subnet-id, --api-server-ip-ranges, --private-server-enabled, --outbound-type.
* 'az hdinsight-on-aks clusterpool upgrade list': Support get cluster pool available upgrade versions.
* 'az hdinsight-on-aks clusterpool upgrade run': Support upgrade cluster pool.
* 'az hdinsight-on-aks cluster create': Support create cluster with internal ingress use --internal-ingress-enabled.
* 'az hdinsight-on-aks cluster upgrade list': Support get cluster available upgrade versions.
* 'az hdinsight-on-aks cluster instance-view list': Support list a cluster instances.
* 'az hdinsight-on-aks clusterpool update': Updated property options from ['--cluster-pool-version'] to ['--cluster-pool-version', '--version'].

1.0.0b1
++++++
* Initial release.