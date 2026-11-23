# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class BackupPolicyScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'vaultName': 'clitest-bkp-vault',
            'rg': 'dataprotectionclitest-rg'
        })

    @AllowLargeResponse()
    def test_dataprotection_backup_policy_create_and_delete(test):
        test.cmd('az dataprotection backup-vault create -g "{rg}" --vault-name "{vaultName}" -l "{location}" '
                 '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type "SystemAssigned" --soft-delete-state "AlwaysOn"')

        disk_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk').get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})
        test.cmd('az dataprotection backup-policy create -n "diskpolicy" --policy "{diskPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.Compute/disks")
        ])
        test.cmd('az dataprotection backup-policy delete -n "diskpolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        blob_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureBlob').get_output_in_json()
        test.kwargs.update({"blobPolicy": blob_policy_json})
        test.cmd('az dataprotection backup-policy create -n "blobpolicy" --policy "{blobPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.Storage/storageAccounts/blobServices")
        ])
        test.cmd('az dataprotection backup-policy delete -n "blobpolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        adls_blob_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDataLakeStorage').get_output_in_json()
        test.kwargs.update({"adlsBlobPolicy": adls_blob_policy_json})
        test.cmd('az dataprotection backup-policy create -n "adlsblobpolicy1" --policy "{adlsBlobPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.Storage/storageAccounts/adlsBlobServices")
        ])
        test.cmd('az dataprotection backup-policy delete -n "adlsblobpolicy1" -g "{rg}" --vault-name "{vaultName}" -y')

        # oss_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDatabaseForPostgreSQL').get_output_in_json()
        # test.kwargs.update({"ossPolicy": oss_policy_json})
        # test.cmd('az dataprotection backup-policy create -n "osspolicy" --policy "{ossPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
        #     test.check('properties.datasourceTypes[0]', "Microsoft.DBforPostgreSQL/servers/databases")
        # ])
        # test.cmd('az dataprotection backup-policy delete -n "osspolicy" -g "{rg}" --vault-name "{vaultName}" -y')

        aks_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureKubernetesService').get_output_in_json()
        test.kwargs.update({"aksPolicy": aks_policy_json})
        test.cmd('az dataprotection backup-policy create -n "akspolicy" --policy "{aksPolicy}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.datasourceTypes[0]', "Microsoft.ContainerService/managedClusters")
        ])
        test.cmd('az dataprotection backup-policy delete -n "akspolicy" -g "{rg}" --vault-name "{vaultName}" -y')

    @AllowLargeResponse()
    def test_dataprotection_backup_policy_manual(test):
        test.cmd('az dataprotection backup-vault create -g "{rg}" --vault-name "{vaultName}" -l "{location}" '
                 '--storage-settings datastore-type="VaultStore" type="LocallyRedundant" --type "SystemAssigned" --soft-delete-state "AlwaysOn"')

        disk_policy_json = test.cmd('az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk', checks=[
            test.check('datasourceTypes[0]', "Microsoft.Compute/disks")
        ]).get_output_in_json()
        test.kwargs.update({
            'policyName': "disk-policy",
            "diskPolicy": disk_policy_json
        })

        lifecycle_json = test.cmd('az dataprotection backup-policy retention-rule create-lifecycle --count 12 --type Days --source-datastore OperationalStore', checks=[
            test.check('deleteAfter.duration', "P12D"),
            test.check('sourceDataStore.dataStoreType', "OperationalStore")
        ]).get_output_in_json()
        test.kwargs.update({"lifecycle": lifecycle_json})

        disk_policy_json = test.cmd('az dataprotection backup-policy retention-rule set --name Daily --policy "{diskPolicy}" --lifecycles "{lifecycle}"', checks=[
            test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 2),
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})

        test.cmd('az dataprotection backup-policy retention-rule remove --name Daily --policy "{diskPolicy}"', checks=[
            test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 1)
        ])

        criteria_json = test.cmd('az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay', checks=[
            test.check('objectType', "ScheduleBasedBackupCriteria")
        ]).get_output_in_json()
        test.kwargs.update({"criteria": criteria_json})

        disk_policy_json = test.cmd('az dataprotection backup-policy tag set --name Daily --policy "{diskPolicy}" --criteria "{criteria}"', checks=[
            test.check("length(policyRules[0].trigger.taggingCriteria)", 2)
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})

        test.cmd('az dataprotection backup-policy tag remove --name Daily --policy "{diskPolicy}"', checks=[
            test.check("length(policyRules[0].trigger.taggingCriteria)", 1)
        ])

        schedule_json = test.cmd('az dataprotection backup-policy trigger create-schedule --interval-type Hourly --interval-count 6 --schedule-days 2021-05-02T05:30:00', checks=[
            test.check('[0]', "R/2021-05-02T05:30:00+00:00/PT6H")
        ]).get_output_in_json()
        test.kwargs.update({"repeating_time_interval": schedule_json[0]})

        disk_policy_json = test.cmd('az dataprotection backup-policy trigger set --policy "{diskPolicy}" --schedule "{repeating_time_interval}"', checks=[
            test.check('policyRules[0].trigger.schedule.repeatingTimeIntervals[0]', "R/2021-05-02T05:30:00+00:00/PT6H")
        ]).get_output_in_json()
        test.kwargs.update({"diskPolicy": disk_policy_json})
        test.cmd('az dataprotection backup-policy create -n "{policyName}" --policy "{diskPolicy}" -g "{rg}" --vault-name "{vaultName}"')

        test.cmd('az dataprotection backup-policy list -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.exists("[?name == '{policyName}']")
        ])
        test.cmd('az dataprotection backup-policy show -g "{rg}" --vault-name "{vaultName}" -n "{policyName}"', checks=[
            test.check('name', "{policyName}")
        ])

    @AllowLargeResponse()
    def test_dataprotection_backup_policy_generic_criteria(test):
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 1 2 27 28 LaSt', checks=[
            test.check('length(days_of_month)', 5)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 29', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month -1', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-month 0', expect_failure=True)
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --days-of-week Monday Tuesday Wednesday Thursday Friday Saturday Sunday', checks=[
            test.check('length(days_of_the_week)', 7)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --weeks-of-month FIRST second Third FoUrtH Last', checks=[
            test.check('length(weeks_of_the_month)', 5)
        ])
        test.cmd('az dataprotection backup-policy tag create-generic-criteria --months-of-year '
                 'JANUARY February MarCh april May June July August September October November December', checks=[
                     test.check('length(months_of_year)', 12)
                 ])

    def _bootstrap_blob_policy_and_lifecycles(test):
        """Load the AzureBlob default policy template and produce reusable
        Operational and Vault retention lifecycle JSON objects, stashing
        them all in ``test.kwargs`` for substitution into subsequent commands.
        """
        blob_policy_json = test.cmd(
            'az dataprotection backup-policy get-default-policy-template --datasource-type AzureBlob'
        ).get_output_in_json()

        op_lifecycle_30d = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 30 --type Days --source-datastore OperationalStore'
        ).get_output_in_json()

        op_lifecycle_60d = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 60 --type Days --source-datastore OperationalStore'
        ).get_output_in_json()

        vault_lifecycle_12w = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 12 --type Weeks --source-datastore VaultStore'
        ).get_output_in_json()

        test.kwargs.update({
            "blobPolicy": blob_policy_json,
            "opLifecycle30": op_lifecycle_30d,
            "opLifecycle60": op_lifecycle_60d,
            "vaultLifecycle12W": vault_lifecycle_12w,
        })

    @AllowLargeResponse()
    def test_default_policy_template_has_single_default_rule(test):
        """The default Blob policy template should ship with exactly one
        retention rule (``Default`` targeting VaultStore). The previous
        duplicate ``Default`` rule that targeted OperationalStore has been
        removed to fix the duplicate-tag issue described in
        ``DPPDefaultTagIssue_DesignDoc.md``.
        """
        blob_policy_json = test.cmd(
            'az dataprotection backup-policy get-default-policy-template --datasource-type AzureBlob',
            checks=[
                test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 1),
                test.check("policyRules[?objectType == 'AzureRetentionRule'] | [0].name", "Default"),
                test.check(
                    "policyRules[?objectType == 'AzureRetentionRule'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
            ]
        ).get_output_in_json()

        # No retention rule should already be named "Default_OperationalStore" in the template
        retention_rules = [r for r in blob_policy_json["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        assert all(r["name"] != "Default_OperationalStore" for r in retention_rules), \
            "Default_OperationalStore must not be pre-seeded in the AzureBlob default policy template"

    @AllowLargeResponse()
    def test_set_default_operational_store_with_op_lifecycle_succeeds(test):
        """``retention-rule set --name Default_OperationalStore`` with an
        OperationalStore lifecycle should add a new rule and leave the
        existing VaultStore ``Default`` rule untouched.
        """
        test._bootstrap_blob_policy_and_lifecycles()

        updated_policy = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"',
            checks=[
                test.check("length(policyRules[?objectType == 'AzureRetentionRule'])", 2),
                test.check(
                    "policyRules[?name == 'Default_OperationalStore'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "OperationalStore"
                ),
                test.check("policyRules[?name == 'Default_OperationalStore'] | [0].isDefault", True),
                test.check(
                    "policyRules[?name == 'Default'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
            ]
        ).get_output_in_json()

        # Defensive: ensure we did not introduce a duplicate name
        op_rule_names = [r["name"] for r in updated_policy["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        assert op_rule_names.count("Default") == 1
        assert op_rule_names.count("Default_OperationalStore") == 1

    @AllowLargeResponse()
    def test_set_default_with_op_lifecycle_throws_cross_store(test):
        """``--name Default`` paired with an OperationalStore lifecycle
        violates the manifest's ``defaultRetentionRuleNames`` mapping
        (``Default`` is reserved for VaultStore).
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_default_operational_store_with_vault_lifecycle_throws_cross_store(test):
        """``--name Default_OperationalStore`` paired with a VaultStore lifecycle
        violates the manifest's ``defaultRetentionRuleNames`` mapping
        (``Default_OperationalStore`` is reserved for OperationalStore).
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{blobPolicy}" --lifecycles "{vaultLifecycle12W}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_remove_default_still_hard_blocks(test):
        """Removing the ``Default`` rule is unsupported (ForbiddenError).
        This guard is intentionally preserved post-fix to match the PS
        cmdlet ``Edit-AzDataProtectionPolicyRetentionRuleClientObject``
        ``RemoveRetention`` parameter set.
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule remove '
            '--name Default --policy "{blobPolicy}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_default_operational_store_twice_overwrites_no_duplicate(test):
        """Two consecutive ``retention-rule set`` calls with the same
        ``--name Default_OperationalStore`` must overwrite the lifecycle
        in place (not create a second rule with the same name).
        """
        test._bootstrap_blob_policy_and_lifecycles()

        policy_with_op = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"'
        ).get_output_in_json()
        test.kwargs.update({"policyWithOp": policy_with_op})

        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{policyWithOp}" --lifecycles "{opLifecycle60}"',
            checks=[
                test.check("length(policyRules[?name == 'Default_OperationalStore'])", 1),
                test.check(
                    "policyRules[?name == 'Default_OperationalStore'] | [0].lifecycles[0].deleteAfter.duration",
                    "P60D"
                ),
            ]
        )

    @AllowLargeResponse()
    def test_set_weekly_with_op_lifecycle_throws_exclusive_source(test):
        """OperationalStore is declared exclusive in the AzureBlob manifest,
        so a non-default rule name (``Weekly``) cannot carry an
        OperationalStore lifecycle.
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Weekly --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_monthly_with_op_lifecycle_throws_exclusive_source(test):
        """Same exclusivity guard applies to the ``Monthly`` retention tag."""
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Monthly --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_yearly_with_op_lifecycle_throws_exclusive_source(test):
        """Same exclusivity guard applies to the ``Yearly`` retention tag."""
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Yearly --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_weekly_with_mixed_lifecycles_throws_exclusive_source(test):
        """Even when only ONE of multiple lifecycles touches the exclusive
        source store, ``--name Weekly`` must still fail -- the exclusivity
        check inspects every lifecycle, not just the first.
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Weekly --policy "{blobPolicy}" '
            '--lifecycles "{vaultLifecycle12W}" "{opLifecycle30}"',
            expect_failure=True
        )

    @AllowLargeResponse()
    def test_set_weekly_with_vault_only_lifecycle_succeeds(test):
        """``--name Weekly`` with a VaultStore-only lifecycle (vaulted LTR)
        must continue to succeed -- OperationalStore exclusivity only kicks
        in when an OperationalStore lifecycle is involved.
        """
        test._bootstrap_blob_policy_and_lifecycles()
        test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Weekly --policy "{blobPolicy}" --lifecycles "{vaultLifecycle12W}"',
            checks=[
                test.check(
                    "policyRules[?name == 'Weekly'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
            ]
        )

    @AllowLargeResponse()
    def test_remove_default_operational_store_succeeds(test):
        """``retention-rule remove --name Default_OperationalStore`` must
        succeed after the rule has been added: only ``Default`` (the VaultStore
        default) is hard-blocked from removal. The remaining ``Default`` rule
        is preserved and still targets VaultStore.

        Parity: PS ``Edit-AzDataProtectionPolicyRetentionRuleClientObject``
        "RemoveRetention AzureBlob -Name Default_OperationalStore removes
        successfully" test.
        """
        test._bootstrap_blob_policy_and_lifecycles()

        policy_with_op = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{blobPolicy}" --lifecycles "{opLifecycle30}"'
        ).get_output_in_json()
        test.kwargs.update({"policyWithOp": policy_with_op})

        policy_after_remove = test.cmd(
            'az dataprotection backup-policy retention-rule remove '
            '--name Default_OperationalStore --policy "{policyWithOp}"',
            checks=[
                test.check("length(policyRules[?name == 'Default_OperationalStore'])", 0),
                test.check(
                    "policyRules[?name == 'Default'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
            ]
        ).get_output_in_json()

        rule_names = [r["name"] for r in policy_after_remove["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        assert "Default_OperationalStore" not in rule_names
        assert rule_names.count("Default") == 1

    @AllowLargeResponse()
    def test_hybrid_policy_default_operationalstore_and_vault_tiers_coexist(test):
        """A full hybrid AzureBlob policy with an OperationalStore default rule
        plus VaultStore Weekly/Monthly/Yearly LTR rules must build without
        triggering cross-store or exclusivity errors, and every rule must
        end up with the expected source data store.

        Parity: PS ``Edit-AzDataProtectionPolicyRetentionRuleClientObject``
        "Weekly/Monthly/Yearly Vault + Default_OperationalStore Op coexist on
        same policy" test.
        """
        test._bootstrap_blob_policy_and_lifecycles()

        # Update Default VaultStore retention from 7 days (template default) to 60 days
        vault_lifecycle_60d = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 60 --type Days --source-datastore VaultStore'
        ).get_output_in_json()
        test.kwargs.update({"vaultLifecycle60D": vault_lifecycle_60d})

        policy_with_updated_default = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default --policy "{blobPolicy}" --lifecycles "{vaultLifecycle60D}"'
        ).get_output_in_json()
        test.kwargs.update({"policyStep0": policy_with_updated_default})

        # Add Default_OperationalStore (Op, 30 days)
        policy_with_op = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Default_OperationalStore --policy "{policyStep0}" --lifecycles "{opLifecycle30}"'
        ).get_output_in_json()
        test.kwargs.update({"policyStep1": policy_with_op})

        # Add Weekly (Vault, 12 weeks) -- reuses bootstrapped vaultLifecycle12W
        policy_with_weekly = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Weekly --policy "{policyStep1}" --lifecycles "{vaultLifecycle12W}"'
        ).get_output_in_json()
        test.kwargs.update({"policyStep2": policy_with_weekly})

        # Add Monthly (Vault, 6 months)
        monthly_vault_lifecycle = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 6 --type Months --source-datastore VaultStore'
        ).get_output_in_json()
        test.kwargs.update({"monthlyVaultLifecycle": monthly_vault_lifecycle})

        policy_with_monthly = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Monthly --policy "{policyStep2}" --lifecycles "{monthlyVaultLifecycle}"'
        ).get_output_in_json()
        test.kwargs.update({"policyStep3": policy_with_monthly})

        # Add Yearly (Vault, 1 year)
        yearly_vault_lifecycle = test.cmd(
            'az dataprotection backup-policy retention-rule create-lifecycle '
            '--count 1 --type Years --source-datastore VaultStore'
        ).get_output_in_json()
        test.kwargs.update({"yearlyVaultLifecycle": yearly_vault_lifecycle})

        final_policy = test.cmd(
            'az dataprotection backup-policy retention-rule set '
            '--name Yearly --policy "{policyStep3}" --lifecycles "{yearlyVaultLifecycle}"',
            checks=[
                test.check(
                    "policyRules[?name == 'Default'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
                test.check(
                    "policyRules[?name == 'Default'] | [0].lifecycles[0].deleteAfter.duration",
                    "P60D"
                ),
                test.check(
                    "policyRules[?name == 'Default_OperationalStore'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "OperationalStore"
                ),
                test.check(
                    "policyRules[?name == 'Weekly'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
                test.check(
                    "policyRules[?name == 'Monthly'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
                test.check(
                    "policyRules[?name == 'Yearly'] | [0].lifecycles[0].sourceDataStore.dataStoreType",
                    "VaultStore"
                ),
            ]
        ).get_output_in_json()

        retention_rule_names = [r["name"] for r in final_policy["policyRules"] if r["objectType"] == "AzureRetentionRule"]
        for expected in ("Default", "Default_OperationalStore", "Weekly", "Monthly", "Yearly"):
            assert expected in retention_rule_names, \
                "Expected retention rule '{}' missing from final hybrid policy".format(expected)
            assert retention_rule_names.count(expected) == 1, \
                "Retention rule '{}' is duplicated in final hybrid policy".format(expected)
