# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import logging
import os
import time
from typing import Union
from azure.cli.core.azclierror import (
    ClientError,
    CLIInternalError,
)

from ._util import (
    AzCli,
    SemanticVersion,
    ColoredFormatter,
)
from ..pwinput import pwinput

EXT_ARC_APPLIANCE = 'arcappliance'
EXT_CUSTOM_LOCATION = 'customlocation'
EXT_CONNECTED_VMWARE = 'connectedvmware'
MIN_ARC_APPLIANCE_VERSION = '1.0.2'

SUPPORT_MSG = "\nPlease reach out to arc-vmware-feedback@microsoft.com or create a support ticket for Arc enabled VMware vSphere in Azure portal."

def confirmation_prompt(msg):
    print(msg)
    while True:
        inp = input('Yes(y)/No(n)?')
        inp = inp.lower()
        if inp in ('y', 'yes'):
            return True
        elif inp in ('n', 'no'):
            return False

class Onboard:
    def __init__(
            self,
            location: str,
            appliance_rg: str,
            appliance_name: str,
            custom_location_name: str,
            vcenter_name: str,
            appliance_subscription_id: str,
            custom_location_subscription_id: str,
            vcenter_subscription_id: str,
            custom_location_rg: str,
            vcenter_rg: str,
            dir_path: str,
            logfile_name: str,
            force: bool
        ):
        self.location = location
        self.appliance_rg = appliance_rg
        self.appliance_name = appliance_name
        self.custom_location_name = custom_location_name
        self.vcenter_name = vcenter_name
        self.appliance_subscription_id = appliance_subscription_id
        self.custom_location_subscription_id = custom_location_subscription_id
        self.vcenter_subscription_id = vcenter_subscription_id
        self.custom_location_rg = custom_location_rg
        self.vcenter_rg = vcenter_rg
        self.dir_path = dir_path
        self.logfile = os.path.join(dir_path, logfile_name)
        self.force = force
        self._appliance_id = None
        self._custom_location_id = None
        self.vc_username = None
        self.vc_password = None
        self.vc_address = None
        self.vc_fqdn = None
        self.vc_port = None
        logger = logging.getLogger(__name__)
        fh = logging.FileHandler(self.logfile)
        fh.setFormatter(
            logging.Formatter(
                fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S',
        ))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(
            ColoredFormatter('%(asctime)s %(levelname)-8s %(message)s')
        )
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)
        self.logger = logger
        self.az = AzCli(self.logger, self.logfile).run


    def run(self):
        self._validate_az()
        self._create_appliance()
        self._create_cluster_extension()
        self._create_custom_location()
        self._connect_vcenter()
        self._log_suceess()


    def _validate_az(self):
        self.logger.info('Validating az version...')
        verStr, err = self.az('version')
        if err:
            raise CLIInternalError(f'az version command failed: {err}')

        azVersion = json.loads(verStr)
        extensions = azVersion['extensions']

        required_extensions = {
            EXT_ARC_APPLIANCE,
            EXT_CUSTOM_LOCATION,
            EXT_CONNECTED_VMWARE,
        }
        not_installed_extensions = required_extensions - set(extensions.keys())
        if not_installed_extensions:
            raise ClientError(f'Following extensions are not installed: {not_installed_extensions}')
        arcappl_ver = extensions[EXT_ARC_APPLIANCE]
        if SemanticVersion(arcappl_ver) < SemanticVersion(MIN_ARC_APPLIANCE_VERSION):
            raise ClientError(f'Current version of {EXT_ARC_APPLIANCE} extension is {arcappl_ver}. Please upgrade {EXT_ARC_APPLIANCE} extension to version {MIN_ARC_APPLIANCE_VERSION} or above using the command `az upgrade`')


    def _fetch_vcenter_credentials(self):
        creds_ok = all(inp is not None for inp in [self.vc_address, self.vc_username, self.vc_password])
        while not creds_ok:
            print(
                "\nProvide vCenter details.\n"
                "  * For example, if your vCenter URL is https://vcenter.contoso.com/ then enter vcenter.contoso.com in 'FQDN or IP Address' field.\n"
                "  * If your vCenter URL is http://10.11.12.13:9090 then enter 10.11.12.13:9090 in 'FQDN or IP Address' field.\n"
            )
            creds: dict[str, Union[str, None]] = {
                'address': self.vc_address,
                'username': self.vc_username,
                'password': self.vc_password,
            }
            while not creds['address']:
                print('Please provide vcenter FQDN or IP address: ', end='')
                creds['address'] = input()
                if not creds['address']:
                    print('Parameter is required, please try again')
                if creds['address'].startswith("http://") or creds['address'].startswith("https://") or creds['address'].endswith("/"):
                    print('Please provide only FQDN or IP address in the FQDN:PORT format, do not provide protocol.')
                    creds['address'] = None
                    continue
                if ':' in creds['address']:
                    _, port_str = creds['address'].rsplit(':', 1)
                    try:
                        _ = int(port_str)
                    except ValueError:
                        print(f'"{port_str}" is not a valid port number, please try again')
                        creds['address'] = None
                        continue
            while not creds['username']:
                print('Please provide vcenter username: ', end='')
                creds['username'] = input()
                if not creds['username']:
                    print('Parameter is required, please try again')
            while not creds['password']:
                creds['password'] = pwinput('Please provide vcenter password: ')
                if not creds['password']:
                    print('Parameter is required, please try again')
                    continue
                passwdConfim = pwinput('Please confirm vcenter password: ')
                if creds['password'] != passwdConfim:
                    print('Passwords do not match, please try again')
                    creds['password'] = None
            print('Confirm vcenter details? [Y/n]: ', end='')
            res = input().lower()
            if res in ['y', '']:
                self.vc_address, self.vc_username, self.vc_password = (
                    creds['address'], creds['username'], creds['password'])
                self.vc_fqdn, self.vc_port = self.vc_address, 443
                if ':' in self.vc_address:
                    self.vc_fqdn, port_str = self.vc_address.rsplit(':', 1)
                    self.vc_port = int(port_str)
                creds_ok = True
            elif res != 'n':
                print('Please type y/n or leave empty.')


    def _evaluate_force_flag(self) -> bool:
        resource_config_file_path = os.path.join(self.dir_path, f'{self.appliance_name}-resource.yaml')
        infra_config_file_path = os.path.join(self.dir_path, f'{self.appliance_name}-infra.yaml')
        appliance_config_file_path = os.path.join(self.dir_path, f'{self.appliance_name}-appliance.yaml')

        missingFiles = []
        if not os.path.exists(resource_config_file_path):
            missingFiles.append(resource_config_file_path)
        if not os.path.exists(infra_config_file_path):
            missingFiles.append(infra_config_file_path)
        if not os.path.exists(appliance_config_file_path):
            missingFiles.append(appliance_config_file_path)

        if not missingFiles:
            # If all the config files are present and the appliance is not in running state,
            # we always run with --force flag.
            self.logger.info('Using --force flag as all the required config files are present.')
            return True

        if len(missingFiles) == 3:
            if self.force:
                # If no config files are found, it might indicate that the script hasn't been
                # executed in the current directory to create the Azure resources before.
                # We let 'az arcappliance run' command handle the force flag.
                self.logger.error(f'Warning: None of the required config files are present. If this is the first attempt, please run the script without --force flag. Else, please check the working directory: {self.dir_path}')
            return self.force

        if self.force:
            # Handle missing config files occuring due to createconfig failure.
            missingMsg = '\n'.join(missingFiles)
            self.logger.warning('Ignoring --force flag as one or more of the required config files are missing.')
            msg = f'Missing configuration files:\n{missingMsg}\n'
            self.logger.info(msg)
        return False


    def _create_appliance(self):
        self.logger.info('Creating Arc appliance')
        applStr, err = self.az(
            'arcappliance',
            'show',
            '--debug',
            '--subscription', self.appliance_subscription_id,
            '--resource-group', self.appliance_rg,
            '--name', self.appliance_name,
        )

        applObj, applStatus = None, None
        if not err:
            applObj = json.loads(applStr)
            applStatus = applObj['status']

        invokeApplianceRun = True
        if applStatus == 'Running':
            invokeApplianceRun = False
            if self.force:
                invokeApplianceRun = confirmation_prompt('The resource bridge is already running. Running with --force flag will delete the existing resource bridge and create a new one. Do you want to continue?')
        else:
            self.force = self._evaluate_force_flag()
            if not self.force:
                deleteAppl = False
                if applStatus == 'WaitingForHeartbeat':
                    deleteAppl = True
                elif applStatus:
                    deleteAppl = confirmation_prompt(f'An existing Arc resource bridge is already present in Azure (status: {applStatus}). Do you want to delete it?')
                if deleteAppl:
                    assert applObj is not None
                    print('Deleting the existing Arc Appliance resource from azure...')
                    self.az(
                        'resource',
                        'delete',
                        '--debug',
                        '--ids', applObj['id'],
                        '--yes',
                    )
        if invokeApplianceRun:
            self._fetch_vcenter_credentials()
            forceParam = []
            if self.force:
                forceParam = ['--force']
            _, err = self.az(
                'arcappliance',
                'run',
                'vmware',
                *forceParam,
                '--subscription', self.appliance_subscription_id,
                '--resource-group', self.appliance_rg,
                '--name', self.appliance_name,
                '--location', self.location,
                '--address', self.vc_address,
                '--username', self.vc_username,
                '--password', self.vc_password,
                capture_output=False
            )
        else:
            print('The Arc resource bridge is already running. Skipping the creation of resource bridge.')

        applStr, _ = self.az(
            'arcappliance',
            'show',
            '--subscription', self.appliance_subscription_id,
            '--resource-group', self.appliance_rg,
            '--name', self.appliance_name,
        )
        applStatus = None
        if applStr:
            applObj = json.loads(applStr)
            applStatus = applObj['status']
        if not applStatus or applStatus == 'WaitingForHeartbeat':
            raise ClientError(f'Appliance VM creation failed. {SUPPORT_MSG}')
        
        assert applObj is not None
        self._appliance_id = applObj['id']
        
        print('Waiting for the appliance to be ready...')
        for i in range(5):
            print("Sleeping for 60 seconds...")
            time.sleep(60)
            applStatus, _ = self.az(
                'resource',
                'show',
                '--debug',
                '--ids', self._appliance_id,
                '--query', 'properties.status',
                '-o', 'tsv',
            )
            if applStatus == 'Running':
                break
            print(f'Appliance is not ready yet, retrying... ({i+1}/5)')

        if applStatus != 'Running':
            raise ClientError(f'Appliance is not in running state. Current state: {applStatus}. {SUPPORT_MSG}')

        print('Arc resource bridge is up and running')


    def _create_cluster_extension(self):
        resourceStr, err = self.az(
            'k8s-extension',
            'create',
            '--debug',
            '--subscription', self.appliance_subscription_id,
            '--resource-group', self.appliance_rg,
            '--name', 'azure-vmwareoperator',
            '--extension-type', 'Microsoft.vmware',
            '--scope', 'cluster',
            '--cluster-type', 'appliances',
            '--cluster-name', self.appliance_name,
            '--config', 'Microsoft.CustomLocation.ServiceAccount=azure-vmwareoperator',
        )
        if err:
            raise CLIInternalError(f'az k8s-extension create command failed, please check the log file for more details: {self.logfile}')

        resource = json.loads(resourceStr)
        self._cluster_extension_id = resource['id']
        if not self._cluster_extension_id:
            raise ClientError(f'Cluster extension creation failed. {SUPPORT_MSG}')

        provState, _ = self.az(
            'resource',
            'show',
            '--debug',
            '--ids', self._cluster_extension_id,
            '--query', 'properties.provisioningState',
            '-o', 'tsv',
        )
        if provState != 'Succeeded':
            raise ClientError(f'Provisioning State of cluster extension is not succeeded. Current state: {provState}. {SUPPORT_MSG}')


    def _create_custom_location(self):
        resourceStr, err = self.az(
            'customlocation',
            'create',
            '--debug',
            '--subscription', self.custom_location_subscription_id,
            '--resource-group', self.custom_location_rg,
            '--name', self.custom_location_name,
            '--location', self.location,
            '--namespace', self.custom_location_name.lower().replace('[^a-z0-9-]', ''),
            '--host-resource-id', self._appliance_id,
            '--cluster-extension-ids', self._cluster_extension_id,
        )
        if err:
            raise CLIInternalError(f'az customlocation create command failed, please check the log file for more details: {self.logfile}')

        resourceObj = json.loads(resourceStr)
        self._custom_location_id = resourceObj['id']
        if not self._custom_location_id:
            raise ClientError(f'Custom location creation failed. {SUPPORT_MSG}')

        provState, _ = self.az(
            'resource',
            'show',
            '--debug',
            '--ids', self._custom_location_id,
            '--query', 'properties.provisioningState',
            '-o', 'tsv',
        )
        if provState != 'Succeeded':
            raise ClientError(f'Provisioning State of custom location is not succeeded. Current state: {provState}. {SUPPORT_MSG}')
        
    
    def _connect_vcenter(self):
        self._fetch_vcenter_credentials()

        self.az(
            'connectedvmware',
            'vcenter',
            'connect',
            '--subscription', self.vcenter_subscription_id,
            '--resource-group', self.vcenter_rg,
            '--name', self.vcenter_name,
            '--custom-location', self._custom_location_id,
            '--location', self.location,
            '--fqdn', self.vc_fqdn,
            '--port', str(self.vc_port),
            '--username', self.vc_username,
            '--password', self.vc_password,
        )
        vcenterStr, err = self.az(
            'connectedvmware',
            'vcenter',
            'show',
            '--subscription', self.vcenter_subscription_id,
            '--resource-group', self.vcenter_rg,
            '--name', self.vcenter_name,
        )
        if err:
            raise CLIInternalError(f'az connectedvmware vcenter show command failed, please check the log file for more details: {self.logfile}')

        vcenterObj = json.loads(vcenterStr)
        self._vcenter_id = vcenterObj['id']
        if not self._vcenter_id:
            raise ClientError(f'Connect vCenter failed. {SUPPORT_MSG}')

        provState, _ = self.az(
            'resource',
            'show',
            '--debug',
            '--ids', self._vcenter_id,
            '--query', 'properties.provisioningState',
            '-o', 'tsv',
        )
        if provState != 'Succeeded':
            raise ClientError(f'Provisioning State of vCenter is not succeeded. Current state: {provState}. {SUPPORT_MSG}')


    def _log_suceess(self):
        self.logger.info(
            'Your vCenter has been successfully onboarded to Azure Arc!\n'
            'To continue onboarding and to complete Arc enabling your vSphere resources, view your vCenter resource in Azure portal.\n'
            f'https://portal.azure.com/#resource{self._vcenter_id}/overview'
        )
