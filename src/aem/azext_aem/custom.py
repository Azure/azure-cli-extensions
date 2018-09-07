# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_data_service_client

logger = get_logger(__name__)

aem_extension_info = {
    'Linux': {
        'publisher': 'Microsoft.OSTCExtensions',
        'name': 'AzureEnhancedMonitorForLinux',
        'version': '3.0'
    },
    'Windows': {
        'publisher': 'Microsoft.AzureCAT.AzureEnhancedMonitoring',
        'name': 'AzureCATExtensionHandler',
        'version': '2.2'
    }
}


def set_aem(cmd, resource_group_name, vm_name, skip_storage_analytics=False):
    aem = EnhancedMonitoring(cmd, resource_group_name, vm_name,
                             vm_client=get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_COMPUTE),
                             storage_client=get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE),
                             skip_storage_analytics=skip_storage_analytics)
    aem.enable()


def delete_aem(cmd, resource_group_name, vm_name):
    aem = EnhancedMonitoring(cmd, resource_group_name, vm_name,
                             vm_client=get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_COMPUTE),
                             storage_client=None)
    aem.delete()


def verify_aem(cmd, resource_group_name, vm_name, wait_time_in_minutes=15, skip_storage_check=False):
    aem = EnhancedMonitoring(cmd, resource_group_name, vm_name,
                             vm_client=get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_COMPUTE),
                             storage_client=get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE))
    aem.verify(skip_storage_check, wait_time_in_minutes)


class EnhancedMonitoring(object):
    def __init__(self, cmd, resource_group, vm_name, vm_client,
                 storage_client, skip_storage_analytics=None):
        self._vm_client = vm_client
        self._storage_client = storage_client
        self._resource_group = resource_group
        self._cmd = cmd
        self._vm = vm_client.virtual_machines.get(resource_group, vm_name, expand='instanceView')
        os_type = self._vm.storage_profile.os_disk.os_type.value.lower()
        self._extension = aem_extension_info['Linux'] if (os_type == 'linux') else aem_extension_info['Windows']
        self._skip_storage_analytics = skip_storage_analytics

    def enable(self):
        pub_cfg, pri_cfg = self._build_extension_cfgs(self._get_disk_info())
        VirtualMachineExtension = self._cmd.get_models('VirtualMachineExtension',
                                                       resource_type=ResourceType.MGMT_COMPUTE,
                                                       operation_group='virtual_machine_extensions')
        existing_ext = self._get_aem_extension()
        extension_instance_name = existing_ext.name if existing_ext else self._extension['name']
        existing_ext = VirtualMachineExtension(location=self._vm.location,
                                               publisher=self._extension['publisher'],
                                               virtual_machine_extension_type=self._extension['name'],
                                               protected_settings={
                                                   'cfg': [{'key': k, 'value': pri_cfg[k]} for k in pri_cfg]
                                               },
                                               type_handler_version=self._extension['version'],
                                               settings={
                                                   'cfg': [{'key': k, 'value': pub_cfg[k]} for k in pub_cfg]
                                               },
                                               auto_upgrade_minor_version=True)
        return self._vm_client.virtual_machine_extensions.create_or_update(self._resource_group, self._vm.name,
                                                                           extension_instance_name,
                                                                           existing_ext)

    def delete(self):
        existing_ext = self._get_aem_extension()
        if not existing_ext:
            raise CLIError("'{}' is not installed".format(self._extension['name']))
        return self._vm_client.virtual_machine_extensions.delete(self._resource_group, self._vm.name,
                                                                 existing_ext.name)

    def verify(self, skip_storage_check, wait_time_in_minutes):
        import datetime
        success = True
        aem_ext = self._get_aem_extension()
        result = {}
        succ_word, fail_word = 'OK', 'Not OK'
        if aem_ext:
            logger.warning('Azure Enhanced Monitoring Extension for SAP Installation check: %s', succ_word)
        else:
            raise CLIError('Azure Enhanced Monitoring Extension for SAP was not installed')
        disk_info = self._get_disk_info()
        managed_disk = disk_info['managed_disk']
        # os disk
        logger.warning('Storage Metrics check...')
        if not skip_storage_check:
            unmanaged_disks = [] if managed_disk else [disk_info['os_disk']] + disk_info['data_disks']
            for disk in unmanaged_disks:
                storage_account_name = disk['account_name']
                logger.warning("\tStorage Metrics check for '%s'...", storage_account_name)
                if disk['is_premium']:
                    logger.warning("\t\tStorage Metrics not available for Premium Storage account '%s'...",
                                   storage_account_name)
                else:
                    logger.warning("\t\tStorage Metrics configuration check for '%s'...", storage_account_name)
                    storage_client = self._get_storage_client(storage_account_name, disk['key'])
                    service_properties = storage_client.get_blob_service_properties()
                    storage_cfg_ok = EnhancedMonitoring._check_storage_analytics(service_properties)
                    if storage_cfg_ok:
                        logger.warning('\t\tStorage Metrics configuration check: %s', succ_word)
                    else:
                        success = False
                        logger.error('\t\tMetrics configuration check: %s', fail_word)
                    if storage_cfg_ok:
                        logger.warning("\t\tStorage Metrics data check for '%s'. Wait up to %s minutes ...",
                                       storage_account_name, wait_time_in_minutes)
                        filter_str = "Timestamp gt datetime'{}'".format(
                            (datetime.datetime.utcnow() + datetime.timedelta(minutes=-5)).isoformat())
                        result = self._check_table_and_content(storage_account_name, disk['key'],
                                                               '$MetricsMinutePrimaryTransactionsBlob', filter_str,
                                                               wait_time_in_minutes)
                        if result:
                            logger.warning("\t\tStorage Metrics data check '%s': %s", storage_account_name, succ_word)
                        else:
                            success = False
                            logger.error("\t\tStorage Metrics data check '%s': %s", storage_account_name, fail_word)

        logger.warning('Azure Enhanced Monitoring Extension for SAP public configuration check...')
        expected, _ = self._build_extension_cfgs(disk_info)
        expected.pop('wad.isenabled')
        public_cfg = {x['key']: x['value'] for x in self._vm.resources[0].settings['cfg']}
        diffs = {k: [expected[k], public_cfg.get(k, None)] for k in expected if expected[k] != public_cfg.get(k, None)}
        if diffs:
            success = False
            for err in diffs:
                logger.error("\tConfiguration Error: Expected: '%s' Actual: '%s'", diffs[err][0], diffs[err][1])
        else:
            logger.warning('Configuration OK')

        if not success:
            raise CLIError('Configuration Not OK.')

    def _build_extension_cfgs(self, disk_info):
        vm_size = str(self._vm.hardware_profile.vm_size)
        pub_cfg = pri_cfg = {}
        vm_size_mapping = {
            'ExtraSmall': 'ExtraSmall (A0)',
            'Standard_A0': 'ExtraSmall (A0)',
            'Basic_A0': 'ExtraSmall (A0)',
            'Small': 'Small (A1)',
            'Medium': 'Medium (A2)',
            'Large': 'Large (A3)',
            'ExtraLarge': 'ExtraLarge (A4)'
        }
        vm_size_mapping.get(vm_size, vm_size)
        pub_cfg.update({
            'vmsize': vm_size,
            'vm.role': 'IaaS',
            'vm.memory.isovercommitted': 0,
            'vm.cpu.isovercommitted': 1 if vm_size == 'ExtraSmall (A0)' else 0,
            'script.version': '3.0.0.0',
            'verbose': '0',
            'href': 'http://aka.ms/sapaem'
        })
        vm_sla_mappings = EnhancedMonitoring._populate_vm_sla_mappings()
        vm_sla = vm_sla_mappings.get(vm_size)
        if vm_sla:
            pub_cfg.update({
                'vm.sla.throughput': vm_sla['TP'],
                'vm.sla.iops': vm_sla['IOPS']
            })

        managed_disk = disk_info['managed_disk']

        # os disk
        os_disk = disk_info['os_disk']
        if os_disk['is_premium']:
            sla = EnhancedMonitoring._get_disk_sla(os_disk['size'])
            pub_cfg.update({
                'osdisk.type': 'Premium',
                'osdisk.sla.throughput': sla['TP'],
                'osdisk.sla.iops': sla['IOPS'],
            })
        if managed_disk and not os_disk['is_premium']:
            logger.warning('Standard Managed Disks are not supported. '
                           'Extension will be installed but no disk metrics will be available.')
        else:
            pub_cfg.update({
                'osdisk.name': os_disk['name'],
                'osdisk.caching': os_disk['caching'],
            })
            if not managed_disk:
                pub_cfg.update({
                    'osdisk.account': os_disk['account_name']
                })
            if not os_disk['is_premium']:
                pub_cfg.update({
                    'osdisk.type': 'Standard',
                    'osdisk.connminute': os_disk['account_name'] + '.minute',
                    'osdisk.connhour': os_disk['account_name'] + '.hour',
                })
        # data disks
        for i, disk in enumerate(disk_info['data_disks']):
            suffix = '.' + str(i + 1)
            if disk['is_premium']:
                sla = EnhancedMonitoring._get_disk_sla(disk['size'])
                pub_cfg.update({
                    'disk.type' + suffix: 'Premium',
                    'disk.sla.throughput' + suffix: sla['TP'],
                    'disk.sla.iops' + suffix: sla['IOPS'],
                })

            if managed_disk and not disk['is_premium']:
                logger.warning('Standard Managed Disks are not supported. '
                               'Extension will be installed but no disk metrics will be available.')
            else:
                pub_cfg.update({
                    'disk.lun' + suffix: disk['lun'],
                    'disk.name' + suffix: disk['name'],
                    'disk.caching' + suffix: disk['caching'],
                })
                if not managed_disk:
                    pub_cfg.update({
                        'disk.account' + suffix: disk['account_name']
                    })
                if not os_disk['is_premium']:
                    pub_cfg.update({
                        'disk.type' + suffix: 'Standard',
                        'disk.connminute' + suffix: disk['account_name'] + '.minute',
                        'disk.connhour' + suffix: disk['account_name'] + '.hour',
                    })

        if not managed_disk:
            unmanaged_disks = [disk_info['os_disk']] + disk_info['data_disks']
            for disk in unmanaged_disks:
                account_name = disk['account_name']
                if disk['is_premium']:
                    logger.info("'%s' is skipped - Storage Account Metrics are not available "
                                "for Premium Type Storage.", disk['name'])
                    pub_cfg.update({
                        account_name + '.hour.ispremium': 1,
                        account_name + '.minute.ispremium': 1,
                    })
                else:
                    if not self._skip_storage_analytics:
                        self._enable_storage_analytics(account_name, disk['key'])
                    pri_cfg.update({
                        account_name + '.hour.key': disk['key'],
                        account_name + '.minute.key': disk['key'],
                    })
                    pub_cfg.update({
                        account_name + '.hour.uri': disk['table_endpoint'] + '$MetricsHourPrimaryTransactionsBlob',
                        account_name + '.minute.uri': disk['table_endpoint'] + '$MetricsMinutePrimaryTransactionsBlob',
                        account_name + '.hour.name': disk['account_name'],
                        account_name + '.minute.name': disk['account_name']
                    })

        pub_cfg['wad.isenabled'] = 0
        return pub_cfg, pri_cfg

    def _get_aem_extension(self):
        existing_ext = None
        if self._vm.resources:
            existing_ext = next((x for x in self._vm.resources
                                 if x.virtual_machine_extension_type.lower() == self._extension['name'].lower() and
                                 x.publisher.lower() == self._extension['publisher'].lower()), None)
        return existing_ext

    def _get_disk_info(self):
        from msrestazure.tools import parse_resource_id  # pylint: disable=import-error
        disks_info = {}
        disks_info['managed_disk'] = bool(getattr(self._vm.storage_profile.os_disk, 'managed_disk', None))
        if disks_info['managed_disk']:
            res_info = parse_resource_id(self._vm.storage_profile.os_disk.managed_disk.id)
            disk = self._vm_client.disks.get(res_info['resource_group'], res_info['name'])
            disks_info['os_disk'] = {
                'name': disk.name,
                'size': disk.disk_size_gb,
                'is_premium': disk.sku.tier.lower() == 'premium',
                'caching': self._vm.storage_profile.os_disk.caching.value,
            }
            disks_info['data_disks'] = []
            for data_disk in self._vm.storage_profile.data_disks:
                res_info = parse_resource_id(data_disk.managed_disk.id)
                disk = self._vm_client.disks.get(res_info['resource_group'], res_info['name'])
                disks_info['data_disks'].append({
                    'name': disk.name,
                    'size': disk.disk_size_gb,
                    'is_premium': disk.sku.tier.lower() == 'premium',
                    'caching': data_disk.caching.value,
                    'lun': data_disk.lun
                })
        else:
            storage_accounts = list(self._storage_client.storage_accounts.list())
            blob_uri = self._vm.storage_profile.os_disk.vhd.uri
            parts = list(filter(None, blob_uri.split('/')))
            storage_account_name = parts[1].split('.')[0]
            disk_name, container_name = parts[-1], parts[-2]
            storage_account = next(x for x in storage_accounts if x.name.lower() == storage_account_name.lower())
            rg = parse_resource_id(storage_account.id)['resource_group']
            key = self._storage_client.storage_accounts.list_keys(rg, storage_account.name).keys[0].value
            disks_info['os_disk'] = {
                'name': disk_name,
                'account_name': storage_account_name,
                'table_endpoint': storage_account.primary_endpoints.table,
                'is_premium': storage_account.sku.tier.value.lower() == 'premium',
                'caching': self._vm.storage_profile.os_disk.caching.value,
                'key': key
            }
            if disks_info['os_disk']['is_premium']:
                disks_info['os_disk']['size'] = self._get_blob_size(storage_account.name, container_name,
                                                                    disk_name, key)

            disks_info['data_disks'] = []
            for data_disk in self._vm.storage_profile.data_disks:
                blob_uri = data_disk.vhd.uri
                parts = list(filter(None, blob_uri.split('/')))
                storage_account_name = parts[1].split('.')[0]
                disk_name, container_name = parts[-1], parts[-2]
                storage_account = next(x for x in storage_accounts if x.name.lower() == storage_account_name.lower())
                rg = parse_resource_id(storage_account.id)['resource_group']
                key = self._storage_client.storage_accounts.list_keys(rg, storage_account.name).keys[0].value
                is_premium = storage_account.sku.tier.value.lower() == 'premium'
                disks_info['data_disks'].append({
                    'name': disk_name,
                    'account_name': storage_account_name,
                    'table_endpoint': storage_account.primary_endpoints.table,
                    'is_premium': is_premium,
                    'caching': self._vm.storage_profile.os_disk.caching.value,
                    'key': key,
                    'lun': data_disk.lun
                })
                if is_premium:
                    disks_info['data_disks'][-1]['size'] = self._get_blob_size(storage_account.name, container_name,
                                                                               disk_name, key)

        return disks_info

    def _get_blob_size(self, storage_account_name, container, blob, key):
        storage_client = self._get_storage_client(storage_account_name, key)
        # convert to GB
        return int(storage_client.get_blob_properties(container, blob).properties.content_length / (1 << 30))

    def _get_storage_client(self, storage_account_name, key):
        BlockBlobService = get_sdk(self._cmd.cli_ctx, ResourceType.DATA_STORAGE,
                                   'blob.blockblobservice#BlockBlobService')
        return get_data_service_client(
            self._cmd.cli_ctx,
            BlockBlobService,
            storage_account_name,
            key,
            endpoint_suffix=self._cmd.cli_ctx.cloud.suffixes.storage_endpoint)  # pylint: disable=no-member

    def _enable_storage_analytics(self, storage_account_name, key):
        storage_client = self._get_storage_client(storage_account_name, key)
        service_properties = storage_client.get_blob_service_properties()
        if not EnhancedMonitoring._check_storage_analytics(service_properties):
            t_logging, t_retention_policy, t_metrics = get_sdk(self._cmd.cli_ctx, ResourceType.DATA_STORAGE, 'Logging',
                                                               'RetentionPolicy', 'Metrics', mod='common.models')
            retention_policy = t_retention_policy(enabled=True, days=13)
            logging = t_logging(delete=True, read=True, write=True, retention_policy=retention_policy)
            minute_metrics = t_metrics(enabled=True, include_apis=True, retention_policy=retention_policy)
            if getattr(service_properties, 'hour_metrics', None):
                service_properties.hour_metrics.retention_policy.days = 13
            storage_client.set_blob_service_properties(logging, minute_metrics=minute_metrics,
                                                       hour_metrics=service_properties.hour_metrics)

    @staticmethod
    def _check_storage_analytics(service_properties):
        return (service_properties and service_properties.logging and
                service_properties.minute_metrics and service_properties.minute_metrics.include_apis and
                service_properties.minute_metrics.retention_policy.days)

    def _check_table_and_content(self, storage_account_name, key, table_name,
                                 filter_string, timeout_in_minutes):
        import time
        sleep_period = 15
        TableService = get_sdk(self._cmd.cli_ctx, ResourceType.DATA_COSMOS_TABLE, 'table#TableService')
        table_client = get_data_service_client(
            self._cmd.cli_ctx,
            TableService,
            storage_account_name,
            key,
            endpoint_suffix=self._cmd.cli_ctx.cloud.suffixes.storage_endpoint)

        seconds = 60 * timeout_in_minutes
        waited = 0
        while waited < seconds:
            entities = table_client.query_entities(table_name, filter_string)
            if entities.items:
                return True
            logger.warning("\t\t\tWait %s seconds for table '%s' has date propagated ...",
                           sleep_period, table_name)
            time.sleep(sleep_period)
            waited += sleep_period

        return False

    @staticmethod
    def _get_disk_sla(disk_size):
        sla = {}
        if 0 < disk_size <= 32:
            # P4
            sla['IOPS'] = 120
            sla['TP'] = 125
        elif 0 < disk_size <= 64:
            # P6
            sla['IOPS'] = 240
            sla['TP'] = 50
        elif 0 < disk_size <= 128:
            # P10
            sla['IOPS'] = 500
            sla['TP'] = 100
        elif 0 < disk_size <= 512:
            # P20
            sla['IOPS'] = 2300
            sla['TP'] = 150
        elif 0 < disk_size <= 1024:
            # P30
            sla['IOPS'] = 5000
            sla['TP'] = 200
        elif 0 < disk_size <= 2048:
            # P40
            sla['IOPS'] = 7500
            sla['TP'] = 250
        elif 0 < disk_size <= 4095:
            # P50
            sla['IOPS'] = 7500
            sla['TP'] = 250
        else:
            raise CLIError("unsupported disk size for Premium Storage: '{}'".format(disk_size))
        return sla

    @staticmethod
    def _populate_vm_sla_mappings():
        mapping = {}
        mapping['Standard_DS1'] = {
            'IOPS': 3200,
            'TP': 32,
        }
        mapping.update(dict.fromkeys(['Standard_DS1_v2', 'Standard_D2s_v3', 'Standard_E2s_v3'], {
            'IOPS': 3200,
            'TP': 48,
        }))
        mapping['Standard_DS2'] = {
            'IOPS': 6400,
            'TP': 64,
        }
        mapping.update(dict.fromkeys(['Standard_DS2_v2', 'Standard_D4s_v3', 'Standard_E4s_v3', 'Standard_E4-2s_v3'], {
            'IOPS': 6400,
            'TP': 96,
        }))
        mapping['Standard_DS3'] = {
            'IOPS': 12800,
            'TP': 128,
        }
        mapping.update(
            dict.fromkeys(
                ['Standard_DS3_v2', 'Standard_D8s_v3', 'Standard_E8s_v3', 'Standard_E8-2s_v3', 'Standard_E8-4s_v3'], {
                    'IOPS': 12800,
                    'TP': 192,
                }))
        mapping['Standard_DS4'] = {
            'IOPS': 25600,
            'TP': 256,
        }
        mapping.update(
            dict.fromkeys(
                ['Standard_DS4_v2', 'Standard_D16s_v3', 'Standard_E16s_v3', 'Standard_E16-4s_v3',
                 'Standard_E16-8s_v3'], {'IOPS': 25600, 'TP': 384}
            )
        )
        mapping.update(dict.fromkeys(['Standard_DS5_v2', 'Standard_D32s_v3'], {
            'IOPS': 51200,
            'TP': 768,
        }))
        mapping['Standard_DS11'] = {
            'IOPS': 6400,
            'TP': 64,
        }
        mapping['Standard_DS11_v2'] = {
            'IOPS': 6400,
            'TP': 96,
        }
        mapping['Standard_DS12'] = {
            'IOPS': 12800,
            'TP': 128,
        }
        mapping['Standard_DS12_v2'] = {
            'IOPS': 12800,
            'TP': 192,
        }
        mapping['Standard_DS13'] = {
            'IOPS': 25600,
            'TP': 256,
        }
        mapping['Standard_DS13_v2'] = {
            'IOPS': 25600,
            'TP': 384,
        }
        mapping['Standard_DS14'] = {
            'IOPS': 51200,
            'TP': 512,
        }
        mapping.update(
            dict.fromkeys(
                ['Standard_DS14_v2', 'Standard_E32s_v3', 'Standard_E32-8s_v3', 'Standard_E32-16s_v3'], {
                    'IOPS': 51200,
                    'TP': 768,
                }))
        mapping['Standard_DS15_v2'] = {
            'IOPS': 64000,
            'TP': 960,
        }
        mapping['Standard_GS1'] = {
            'IOPS': 5000,
            'TP': 125,
        }
        mapping['Standard_GS2'] = {
            'IOPS': 10000,
            'TP': 250,
        }
        mapping['Standard_GS3'] = {
            'IOPS': 20000,
            'TP': 500,
        }
        mapping['Standard_GS4'] = {
            'IOPS': 40000,
            'TP': 1000,
        }
        mapping['Standard_GS5'] = {
            'IOPS': 80000,
            'TP': 2000,
        }
        mapping.update(
            dict.fromkeys(['Standard_M8-2ms', 'Standard_M8-4ms', 'Standard_M8ms'], {
                'IOPS': 5000,
                'TP': 125,
            }))
        mapping.update(
            dict.fromkeys(['Standard_M16-4ms', 'Standard_M16-8ms', 'Standard_M16ms'], {
                'IOPS': 10000,
                'TP': 250,
            }))
        mapping.update(
            dict.fromkeys(
                ['Standard_M32-8ms', 'Standard_M32-16ms', 'Standard_M32ms', 'Standard_M32ls', 'Standard_M32ts'], {
                    'IOPS': 20000,
                    'TP': 500,
                }))
        mapping.update(
            dict.fromkeys(
                ['Standard_M64ms', 'Standard_M64s', 'Standard_M64ls', 'Standard_M64-16ms', 'Standard_M64-32ms'], {
                    'IOPS': 40000,
                    'TP': 1000,
                }))
        mapping.update(
            dict.fromkeys(
                ['Standard_M128s', 'Standard_M128ms', 'Standard_M128-32ms', 'Standard_M128-64ms'], {
                    'IOPS': 80000,
                    'TP': 2000,
                }))
        mapping.update(
            dict.fromkeys(
                ['Standard_E64s_v3', 'Standard_D64s_v3', 'Standard_E64-16s_v3', 'Standard_E64-32s_v3',
                 'Standard_E64is_v3'], {'IOPS': 80000, 'TP': 1200}
            )
        )
        return mapping
