# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import json
import unittest

from azext_spring.jobs.models.job_execution_instance import JobExecutionInstanceCollection

NORMAL_LIST_RESPONSE_WITH_2_INSTANCES = '''
{
  "value": [
    {
      "name": "sample-job-execution-instance-0"
    },
    {
      "name": "sample-job-execution-instance-1"
    }
  ]
}
'''

NORMAL_LIST_RESPONSE_WITH_1_INSTANCE = '''
{
  "value": [
    {
      "name": "sample-job-execution-instance-0"
    }
  ]
}
'''

NORMAL_LIST_RESPONSE_WITH_0_INSTANCES = '''
{
  "value": []
}
'''

LIST_RESPONSE_WITH_ADDITIONAL_FIELDS = '''
{
  "unexpected_field": "field_1",
  "value": [
    {
      "name": "sample-job-execution-instance-0",
      "unexpected_field": "field_2"
    },
    {
      "name": "sample-job-execution-instance-1"
    }
  ]
}
'''

LIST_RESPONSE_WITH_INVALID_FIELDS = '''
{
  "wrong_field": [
    {
      "name": "sample-job-execution-instance-0"
    }
  ]
}
'''


class JobExecutionInstanceTest(unittest.TestCase):
    def testDeserializeMultiInstances(self):
        self._doTestDeserializeMultiInstances(NORMAL_LIST_RESPONSE_WITH_2_INSTANCES)
        self._doTestDeserializeMultiInstances(LIST_RESPONSE_WITH_ADDITIONAL_FIELDS)

    def testDeserializeSingleInstance(self):
        collection = JobExecutionInstanceCollection.deserialize(json.loads(NORMAL_LIST_RESPONSE_WITH_1_INSTANCE))
        self.assertIsNotNone(collection)
        self.assertIsNotNone(collection.value)
        self.assertEqual(type(collection.value), list)
        self.assertEqual(len(collection.value), 1)
        instance_0 = collection.value[0]
        self.assertEqual("sample-job-execution-instance-0", instance_0.name)

    def testDeserializeNoInstance(self):
        collection = JobExecutionInstanceCollection.deserialize(json.loads(NORMAL_LIST_RESPONSE_WITH_0_INSTANCES))
        self.assertIsNotNone(collection)
        self.assertIsNotNone(collection.value)
        self.assertEqual(type(collection.value), list)
        self.assertEqual(len(collection.value), 0)

    def testDeserializeInvalidResponse(self):
        json_object = json.loads(LIST_RESPONSE_WITH_INVALID_FIELDS)
        collection = JobExecutionInstanceCollection.deserialize(json_object)
        self.assertIsNotNone(collection)
        self.assertIsNone(collection.value)

    def _doTestDeserializeMultiInstances(self, responseStr):
        collection = JobExecutionInstanceCollection.deserialize(json.loads(responseStr))
        self.assertIsNotNone(collection)
        self.assertIsNotNone(collection.value)
        self.assertEqual(type(collection.value), list)
        self.assertEqual(len(collection.value), 2)
        instance_0 = collection.value[0]
        self.assertEqual("sample-job-execution-instance-0", instance_0.name)

        instance_1 = collection.value[1]
        self.assertEqual("sample-job-execution-instance-1", instance_1.name)
