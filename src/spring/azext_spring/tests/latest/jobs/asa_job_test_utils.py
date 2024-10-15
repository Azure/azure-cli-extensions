# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
import json

from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview.models import (EnvSecretsCollection, JobResource,
                                                                               Secret)

sample_job_resource_json_str = r'''
{
  "properties": {
    "provisioningState": "Succeeded",
    "triggerConfig": {
      "triggerType": "Manual"
    },
    "source": {
      "type": "BuildResult",
      "buildResultId": "<default>"
    },
    "template": {
      "environmentVariables": [
        {
          "name": "key1",
          "value": "value1"
        },
        {
          "name": "env2",
          "value": "value2"
        },
        {
          "name": "secretKey1",
          "secretValue": "*"
        }
      ],
      "args": [
        "arg1",
        "arg2"
      ]
    }
  },
  "systemData": {
    "createdBy": "sample-user",
    "createdByType": "User",
    "createdAt": "2021-08-11T03:16:03.944Z",
    "lastModifiedBy": "sample-user",
    "lastModifiedByType": "User",
    "lastModifiedAt": "2021-08-11T03:17:03.944Z"
  },
  "type": "Microsoft.AppPlatform/Spring/jobs",
  "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AppPlatform/Spring/myservice/jobs/test-job",
  "name": "test-job"
}
'''

sample_job_resource = lambda: JobResource.deserialize(json.loads(sample_job_resource_json_str))

expected_create_job_payload = '''
{
  "properties": {
    "template": {
      "environmentVariables": [],
      "resourceRequests": {
        "cpu": "500m",
        "memory": "2Gi"
      }
    },
    "managedComponentReferences": [],
    "triggerConfig": {
      "triggerType": "Manual"
    }
  }
}
'''

expected_start_job_payload = '''
{
  "environmentVariables": [],
  "args": [
    "sleep",
    "30"
  ],
  "resourceRequests": {
    "cpu": "1",
    "memory": "512Mi"
  }
}
'''


class UpdateJobCaseData(object):
    def get_job_before(self):
        pass

    def envs(self):
        pass

    def secret_envs(self):
        pass

    def args(self):
        pass

    def list_env_secrets_collection(self):
        pass

    def expected_update_job_payload(self):
        pass

    def get_job_after(self):
        pass


class UpdateJobCase1Data(UpdateJobCaseData):
    def get_job_before(self):
        return JobResource.deserialize(json.loads(r'''
        {
          "properties": {
            "provisioningState": "Succeeded",
            "triggerConfig": {
              "triggerType": "Manual"
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "template": {
              "environmentVariables": [
                {
                  "name": "key1",
                  "value": "value1"
                },
                {
                  "name": "env2",
                  "value": "value2"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "*"
                }
              ],
              "args": [
                "arg1",
                "arg2"
              ]
            }
          },
          "systemData": {
            "createdBy": "sample-user",
            "createdByType": "User",
            "createdAt": "2021-08-11T03:16:03.944Z",
            "lastModifiedBy": "sample-user",
            "lastModifiedByType": "User",
            "lastModifiedAt": "2021-08-11T03:17:03.944Z"
          },
          "type": "Microsoft.AppPlatform/Spring/jobs",
          "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AppPlatform/Spring/myservice/jobs/test-job",
          "name": "test-job"
        }
        '''))

    def envs(self):
        return {"prop1": "v_prop1"}

    def secret_envs(self):
        return None

    def args(self):
        return None

    def list_env_secrets_collection(self):
        return EnvSecretsCollection(
            value=[
                Secret(
                    name="secretKey1",
                    value="secretValue1"
                )
            ]
        )

    def expected_update_job_payload(self):
        return JobResource.deserialize(json.loads('''
        {
          "properties": {
            "template": {
              "environmentVariables": [
                {
                  "name": "prop1",
                  "value": "v_prop1"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "secretValue1"
                }
              ],
              "args": [
                "arg1",
                "arg2"
              ],
              "resourceRequests": {}
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "triggerConfig": {
              "triggerType": "Manual"
            }
          }
        }
        '''))

    def get_job_after(self):
        return JobResource.deserialize(json.loads(r'''
        {
          "properties": {
            "provisioningState": "Succeeded",
            "triggerConfig": {
              "triggerType": "Manual"
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "template": {
              "environmentVariables": [
                {
                  "name": "prop1",
                  "value": "v_prop1"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "*"
                }
              ],
              "args": [
                "arg1",
                "arg2"
              ]
            }
          },
          "systemData": {
            "createdBy": "sample-user",
            "createdByType": "User",
            "createdAt": "2021-08-11T03:16:03.944Z",
            "lastModifiedBy": "sample-user",
            "lastModifiedByType": "User",
            "lastModifiedAt": "2021-08-11T03:17:03.944Z"
          },
          "type": "Microsoft.AppPlatform/Spring/jobs",
          "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AppPlatform/Spring/myservice/jobs/test-job",
          "name": "test-job"
        }
        '''))


class UpdateJobCase2Data(UpdateJobCaseData):
    def get_job_before(self):
        return JobResource.deserialize(json.loads(r'''
        {
          "properties": {
            "provisioningState": "Succeeded",
            "triggerConfig": {
              "triggerType": "Manual"
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "template": {
              "environmentVariables": [
                {
                  "name": "key1",
                  "value": "value1"
                },
                {
                  "name": "env2",
                  "value": "value2"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "*"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "*"
                }
              ],
              "args": [
                "arg1",
                "arg2"
              ]
            }
          },
          "systemData": {
            "createdBy": "sample-user",
            "createdByType": "User",
            "createdAt": "2021-08-11T03:16:03.944Z",
            "lastModifiedBy": "sample-user",
            "lastModifiedByType": "User",
            "lastModifiedAt": "2021-08-11T03:17:03.944Z"
          },
          "type": "Microsoft.AppPlatform/Spring/jobs",
          "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AppPlatform/Spring/myservice/jobs/test-job",
          "name": "test-job"
        }
        '''))

    def envs(self):
        return None

    def secret_envs(self):
        return {"secretKey1": "secretValue1_2"}

    def args(self):
        return "arg3"

    def list_env_secrets_collection(self):
        return EnvSecretsCollection(
            value=[
                Secret(
                    name="secretKey1",
                    value="secretValue1"
                ),
                Secret(
                    name="secretKey2",
                    value="secretValue2"
                )
            ]
        )

    def expected_update_job_payload(self):
        return JobResource.deserialize(json.loads('''
        {
          "properties": {
            "template": {
              "environmentVariables": [
                {
                  "name": "key1",
                  "value": "value1"
                },
                {
                  "name": "env2",
                  "value": "value2"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "secretValue1_2"
                }
              ],
              "args": [
                "arg3"
              ],
              "resourceRequests": {}
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "triggerConfig": {
              "triggerType": "Manual"
            }
          }
        }
        '''))

    def get_job_after(self):
        return JobResource.deserialize(json.loads(r'''
        {
          "properties": {
            "provisioningState": "Succeeded",
            "triggerConfig": {
              "triggerType": "Manual"
            },
            "source": {
              "type": "BuildResult",
              "buildResultId": "<default>"
            },
            "template": {
              "environmentVariables": [
                {
                  "name": "key1",
                  "value": "value1"
                },
                {
                  "name": "env2",
                  "value": "value2"
                },
                {
                  "name": "secretKey1",
                  "secretValue": "*"
                }
              ],
              "args": [
                "arg3"
              ]
            }
          },
          "systemData": {
            "createdBy": "sample-user",
            "createdByType": "User",
            "createdAt": "2021-08-11T03:16:03.944Z",
            "lastModifiedBy": "sample-user",
            "lastModifiedByType": "User",
            "lastModifiedAt": "2021-08-11T03:17:03.944Z"
          },
          "type": "Microsoft.AppPlatform/Spring/jobs",
          "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AppPlatform/Spring/myservice/jobs/test-job",
          "name": "test-job"
        }
        '''))
