# # from azure.storage.blob import BlobServiceClient
# # import os

# # # def cf_storage(cli_ctx, subscription_id=None):
# # #     return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_STORAGE, subscription_id=subscription_id)
# # token_in = "?sv=2020-02-10&ss=bfqt&srt=sco&sp=rwdlacuptfx&se=2021-05-21T16:09:41Z&st=2021-05-20T08:09:41Z&spr=https&sig=dumQ54K1tQ9oHj2S%2BNsSS84du1NVn3rm472GS0%2Bzfok%3D"

# # log_storage_account_url = f"https://teststarp.blob.core.windows.net/"


# # blob_service_client = BlobServiceClient(account_url=log_storage_account_url, credential=token_in)
# # # try:
# # #     new_container = blob_service_client.create_container("testccarp2")
# # #     properties = new_container.get_container_properties()
# # #     print(properties)
# # # except Exception as ex:
# # #     print("exception" + str(ex))

# # container_name="testccarp"
# # output_file=os.path.join(os.path.expanduser('~'), '.azure', 'az_connectedk8s_troubleshoot_output.tar.gz')
# # output_file = os.path.join(os.path.expanduser('~'), '.azure', 'connected8s_troubleshoot.log')

# # blob_client = blob_service_client.get_blob_client(container=container_name, blob="log_file")

# # with open(output_file, "rb") as data:
# #     blob_client.upload_blob(data)

# import requests
# import re
# import time
# # import gc

# import functools

# def timer(func):
#     @functools.wraps(func)
#     def wrapper_timer(*args, **kwargs):
#         tic = time.perf_counter()
#         value = func(*args, **kwargs)
#         toc = time.perf_counter()
#         elapsed_time = toc - tic
#         print(f"Elapsed time: {elapsed_time:0.4f} seconds")
#         return value
#     return wrapper_timer

# @timer
# def fun1():
#     extension_name='connectedk8s'
#     git_url = "https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/index.json"
#     response = requests.get(git_url, timeout=10)
#     response_json = response.json()
#     version_list = []
#     for ver in response_json["extensions"][extension_name]:
#         version_list.append(ver["metadata"]["version"])
#     del response_json
#     del response
#     # gc.collect()
#     version_list.sort()
#     return version_list[-1]

# @timer
# def fun2():
#     extension_name='connectedk8s'
#     git_url = "https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/{}/setup.py".format(extension_name)
#     response = requests.get(git_url, timeout=10)
#     if response.status_code != 200:
#         # logger.info("Failed to fetch the latest version from '%s' with status code '%s' and reason '%s'",
#         #             git_url, response.status_code, response.reason)
#         return None
#     for line in response.iter_lines():
#         txt = line.decode('utf-8', errors='ignore')
#         if txt.startswith('VERSION'):
#             match = re.search(r'VERSION = \'(.*)\'$', txt)
#             if match:
#                 return match.group(1)
#             else:
#                 match = re.search(r'VERSION = \"(.*)\"$', txt)
#                 if match:
#                     return match.group(1)
#     return None

# print(fun1())
# print(fun2())


#         # container_name = cluster_name + "-" + str(uuid.uuid4().hex)  # Create a unique name for the container
#         # if len(container_name) > consts.STORAGE_CONTAINER_NAME_MAX_LENGTH:
#         #     container_name = container_name[:consts.STORAGE_CONTAINER_NAME_MAX_LENGTH]
#         # container_name.rstrip('-')


#         # try:
#         #     # Creating the .tar.gz for logs and deleting the actual log file
#         #     import tarfile
#         #     with tarfile.open(output_file, "w:gz") as tar:
#         #         tar.add(troubleshoot_log_path, 'connected8s_troubleshoot.log')
#         #     logging.shutdown()  # To release log file handler, so that the actual log file can be removed after archiving
#         #     os.remove(troubleshoot_log_path)
#         #     print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}The diagnostic logs have been collected and archived at '{output_file}'.")
#         # except Exception as ex:
#         #     tr_logger.error("Error occured while archiving the log file: {}".format(str(ex)))
#         #     raise Exception("Error occured while archiving the diagnostic log file: {}".format(str(ex)))


# # import subprocess
# # retry_attempts = 5
# # while(retry_attempts > 0)
# #     try:
# #         sub_out = subprocess.check_output(subprocess_cmd)
# #         break # Successful execution with return code 0
# #     except subprocess.CalledProcessError as ex:
# #         logger.debug("error code", ex.returncode, ex.output)
# #     retry_attempts -= 1


# import requests
# def get_latest_extension_version(extension_name='connectedk8s', max_retries=3, timeout=10):
#     git_url = "https://raw.githubusercontent.com/Azure/azure-cli-extensions/main/src/index.json"
#     #or "https://aka.ms/azure-cli-extension-index-v1"
#     try:
#         with requests.Session() as s:
#             s.mount(git_url, requests.adapters.HTTPAdapter(max_retries=max_retries))
#             response = s.get(git_url, timeout=timeout)
#             response_json = response.json()
#             version_list = []
#             for ver in response_json["extensions"][extension_name]:
#                 version_list.append(ver["metadata"]["version"])
#             version_list.sort()
#             return version_list[-1]
#     except Exception as ex:
#         pass
#     return None

# print(get_latest_extension_version())

from kubernetes import client as kube_client, config
def check_linux_amd64_node(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_arch == "amd64" and node_os == "linux":
                print(item.status.capacity.get("memory"))
                print(item.status.capacity.get("cpu"))
                # return True
    except Exception as e:  # pylint: disable=broad-except
        print(str(e))
        # logger.debug("Error occured while trying to find a linux/amd64 node: " + str(e))
        # utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault, 'Unable to find a linux/amd64 node',
        #                                    raise_error=False)
    return False

config.load_kube_config()
configuration = kube_client.Configuration()
# check_linux_amd64_node(configuration)

current_k8s_context = config.list_kube_config_contexts()[1]['context']
current_k8s_namespace = current_k8s_context['namespace']
namespace_exists = False
k8s_v1 = kube_client.CoreV1Api()
k8s_ns = k8s_v1.list_namespace()
for ns in k8s_ns.items:
    if ns.metadata.name == current_k8s_namespace:
        namespace_exists = True
        print("exists")
        print(ns.metadata.name)
        break
if namespace_exists is False:
    print("dont")
