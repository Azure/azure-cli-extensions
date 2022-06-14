from argparse import Namespace
from kubernetes import client, config, watch, utils
from binascii import a2b_hex
import csv
import errno
import subprocess
from logging import exception
import os
import json
import tempfile
import time
import datetime
import base64
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from base64 import b64encode, b64decode
import stat
import platform
from unicodedata import name
from azure.core.exceptions import ClientAuthenticationError
import yaml
import requests
import urllib.request
import shutil
from _thread import interrupt_main
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core._profile import Profile
from azure.cli.core.util import sdk_no_wait
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _resource_providers_client
from azext_connectedk8s._client_factory import get_graph_client_service_principals
import azext_connectedk8s._constants as consts
import azext_connectedk8s.custom as custom
from glob import glob
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity, ListClusterUserCredentialProperties
from threading import Timer, Thread
import sys
import hashlib
import re
from azure.cli.core import get_default_cli
import urllib.request
logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

def connect(host='http://portal.azure.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False
# test

def check_connectivity():
    if connect():
        return True
    else:
        print("Error: Please check your internet connection and then try again.\n")
        return False


def GeneratingFolder(time_stamp):
    #Creating the Diagnoser Folder and adding it if its not already present
    path="C:\\Users\\t-svagadia\\Diagnoser"
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    #Creating Subfolder with the given timestamp to store all the logs 
    path="C:\\Users\\t-svagadia\\Diagnoser\ "+time_stamp
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def agents_logger(api_instance,time_stamp):

    #To retrieve all of the pods that are presesnt in the Cluster
    all_agents = api_instance.list_namespaced_pod(namespace = "azure-arc")

    # Traversing thorugh all agents 
    for agent_pod in all_agents.items:

        #Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
        agent_name=agent_pod.metadata.name
        path=("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Arc_Agents_logs")
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        path=("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Arc_Agents_logs\ "+agent_name)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        #Traversing through all of the containers present inside each pods 
        for each_container in agent_pod.spec.containers:

            #Fetching the Container name 
            container_name=each_container.name
            
            #Creating a text file with the name of the container and adding that containers logs in it
            container_log=api_instance.read_namespaced_pod_log(name=agent_name,container=container_name,namespace = "azure-arc")
            with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Arc_Agents_logs\ "+agent_name+"\ "+container_name+".txt",'w+') as container_file:
                container_file.write(str(container_log))



def deployments_logger(api_instance, time_stamp):

    #Creating new Deployment Logs folder in the given timestamp folder
    path="C:\\Users\\t-svagadia\\Diagnoser\ "+time_stamp+"\Deployment_logs"  
    try:
        os.mkdir(path)
    except FileExistsError:
        pass 

    # To retrieve all the the deployements that are present in the Cluster
    all_deployments = api_instance.list_namespaced_deployment("azure-arc")
    
    #Traversing through all the deployments present 
    for deployment in all_deployments.items:

        #Fetching the deployment name
        deployment_name=deployment.metadata.name

        #Creating a text file with the name of the deployment and adding deployment status in it
        with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Deployment_logs\ "+deployment_name+".txt",'w+') as deployment_file:
            deployment_file.write(str(deployment.status))
        
    
def check_agent_state(api_instance,time_stamp):

    with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Agent_State.txt",'w+') as agent_state:

        agents = api_instance.list_namespaced_pod(namespace="azure-arc")
        if not agents.items:
            return "Agents have not been added to cluster"
        agents_ready_amount = 0
        counter=0
        for each_agent in agents.items:
            agent_state.write(each_agent.metadata.name+" = "+each_agent.status.phase+"\n")
            if each_agent.status.phase == 'Pending' or each_agent.status.phase=="pending":
                counter=1
        if counter:
            print("Error: One or More Azure Arc agents are in Pending state. It may be caused due to insufficient resource availability in the cluster.\n Learn more at scaleup link. \n")
                   


def check_msi_expirytime(connected_cluster,time_stamp):


    Expiry_date=str(connected_cluster.managed_identity_certificate_expiration_time)
    Current_date_temp=datetime.datetime.now().utcnow().replace(microsecond=0,tzinfo=datetime.timezone.utc).isoformat()
    Current_date=Current_date_temp.replace('T',' ')

    if (Expiry_date<Current_date):
        print("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n For further help visit this link:\n")

    

def check_agent_version(connected_cluster,azure_arc_agent_version):
    
    user_agent_version=connected_cluster.agent_version
    user_version=user_agent_version.split('.')
    agent_version=azure_arc_agent_version.split('.')

    if((int(user_version[0])<int(agent_version[0])) or (int(agent_version[1])-int(user_version[1])>2)):
        logger.warning("Error: We found that you are on an older agent version thats not supported.\n Please visit this link to know the agent version support policy 'link'.\n")

    

def check_outbound(api_instance,api_instance3,time_stamp,namespace):

    namespace="default"
    path="TroubleshootTemplates\\test_deployment.yaml"

    config.load_kube_config()
    k8s_client = client.ApiClient()
    yaml_file = "TroubleshootTemplates\\test_deployment.yaml"
    try:
        api_utils=utils.create_from_yaml(k8s_client, yaml_file)  
        #print(api_utils)
    except Exception as e:
        pass

    #api_response=api_instance3.create_namespaced_job(namespace,body)
    #print(api_response)
    w = watch.Watch()
    counter=0
    for event in w.stream(api_instance3.list_namespaced_job,namespace=namespace,label_selector="",timeout_seconds=180):
        #print(event["object"])
        try:
            if event["object"].metadata.name=="testdeployment" and event["object"].status.conditions[0].type== "Complete":
                counter=1
                w.stop()
                #print(event["object"].status.succeeded)
                #print(event["object"].metadata.name+" Job successfully executed\n")
        except Exception as e:
            continue
        else:
            continue
    
    if(counter==0):
        subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\test_deployment.yaml"],stdout=subprocess.DEVNULL)
        print("Container not created.")
    else:
        try:
            job_name="testdeployment"
            dns_log="000"
            all_pods = api_instance.list_namespaced_pod(namespace)
            # Traversing thorugh all agents 
            for testdeployment_pod in all_pods.items:

                #Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name=testdeployment_pod.metadata.name
                #print(pod_name)
                if(pod_name.startswith(job_name)):
                    #print(pod_name)
                    #Creating a text file with the name of the container and adding that containers logs in it
                    network_log=api_instance.read_namespaced_pod_log(name=pod_name,container="networktest1", namespace = namespace)


            diagnostic_container_check(network_log,time_stamp)
            subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\test_deployment.yaml"],stdout=subprocess.DEVNULL)
           
            # api_instance3.delete_namespaced_job(job_name,namespace)
            # api_instance.delete_namespaced_pod(pod_name,namespace)

        except Exception as e:
            subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\test_deployment.yaml"],stdout=subprocess.DEVNULL)
            print("Some error occured during execution.")



def diagnostic_container_check(network_log,time_stamp):
    #print(network_log)

    outbound_check=network_log[-4:-1:]   
    dns_check=network_log[0:len(network_log)-5:]
    # print(dns_check)                
    # print(outbound_check)
    if(outbound_check!="000" ):
        with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Outbound_Network_Check.txt",'w+') as dns:
            dns.write("Response code "+outbound_check+": Your Outbound network connectivity is working fine.")
    else:
        print("Error: Unable to reach outbound public internet from within the cluster. Seems your outbound network is down for some reason.\n To know more please visit this 'link' \n")
        with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\Outbound_Check.txt",'w+') as dns:
            dns.write("Response code "+outbound_check+": Your outbound network connectivity is down for some reasons.")

    if("NXDOMAIN" in dns_check or "connection timed out" in dns_check):
        print("Error: There is some error with your DNS connectivity inside the cluster.\n For further help please visit 'link'.\n")
        with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\DNS_Check.txt",'w+') as dns:
            dns.write("Response code "+dns_check+": For some reason your cluster DNS is not working properly.")
    else:
        with open("C:\\Users\\t-svagadia\\Diagnoser\ "+ time_stamp+"\DNS_Check.txt",'w+') as dns:
            dns.write("Response code "+dns_check+": Your Cluster DNS is working properly.")