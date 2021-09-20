import os
import pytest
import subprocess


# Function to pull helm charts
def pull_helm_chart(registry_path):
    os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
    cmd_helm_chart_pull = ["helm", "chart", "pull", registry_path]
    response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_chart_pull, error_helm_chart_pull = response_helm_chart_pull.communicate()
    if response_helm_chart_pull.returncode != 0:
        pytest.fail("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))
    return output_helm_chart_pull.decode("ascii")


# Function to export helm charts
def export_helm_chart(registry_path, destination):
    cmd_helm_chart_export = ["helm", "chart", "export", registry_path, "--destination", destination]
    response_helm_chart_export = subprocess.Popen(cmd_helm_chart_export, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_chart_export, error_helm_chart_export = response_helm_chart_export.communicate()
    if response_helm_chart_export.returncode != 0:
        pytest.fail("Unable to export helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_export.decode("ascii"))
    return output_helm_chart_export.decode("ascii")


# Function to add a helm repository
def add_helm_repo(repo_name, repo_url):
    cmd_helm_repo = ["helm", "repo", "add", repo_name, repo_url]
    response_helm_repo = subprocess.Popen(cmd_helm_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_repo, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        pytest.fail("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))
    return output_helm_repo.decode("ascii")


# Function to install helm charts
def install_helm_chart(helm_release_name, helm_release_namespace, helm_chart_path, wait=False, **kwargs):
    cmd_helm_install = ["helm", "install", helm_release_name, helm_chart_path, "--namespace", helm_release_namespace]
    if wait:
        cmd_helm_install.extend(["--wait"])
    for key, value in kwargs.items():
        cmd_helm_install.extend(["--set", "{}={}".format(key, value)])
    response_helm_install = subprocess.Popen(cmd_helm_install, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_install, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        pytest.fail("Unable to install helm release: " + error_helm_install.decode("ascii"))
    return output_helm_install.decode("ascii")


# Function to delete helm chart
def delete_helm_release(helm_release_name, helm_release_namespace):
    cmd_helm_delete = ["helm", "delete", helm_release_name, "--namespace", helm_release_namespace]
    response_helm_delete = subprocess.Popen(cmd_helm_delete, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_delete, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        pytest.fail("Error occured while deleting the helm release: " + error_helm_delete.decode("ascii"))
    return output_helm_delete.decode("ascii")


# Function to list helm release
def list_helm_release(helm_release_namespace):
    cmd_helm_list = ["helm", "list", "--namespace", helm_release_namespace]
    response_helm_list = subprocess.Popen(cmd_helm_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_helm_list, error_helm_list = response_helm_list.communicate()
    if response_helm_list.returncode != 0:
        pytest.fail("Error occured while fetching the helm release: " + error_helm_list.decode("ascii"))
    return output_helm_list.decode("ascii")
