# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import json
import base64
from unittest import mock

from azext_sftp import connectivity_utils


class SftpConnectivityUtilsTest(unittest.TestCase):
    """Test suite for SFTP connectivity utilities.
    
    Owner: johnli1
    """

    def test_format_relay_info_string_success(self):
        """Test format_relay_info_string with valid relay information."""
        # Arrange
        relay_info = {
            'namespaceName': 'test-namespace',
            'namespaceNameSuffix': 'servicebus.windows.net',
            'hybridConnectionName': 'test-connection',
            'accessKey': 'test-access-key',
            'expiresOn': '2025-07-04T10:00:00Z',
            'serviceConfigurationToken': 'test-token'
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        # Decode the base64 result to verify the structure
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        self.assertIn('relay', parsed_result)
        relay_data = parsed_result['relay']
        
        self.assertEqual(relay_data['namespaceName'], 'test-namespace')
        self.assertEqual(relay_data['namespaceNameSuffix'], 'servicebus.windows.net')
        self.assertEqual(relay_data['hybridConnectionName'], 'test-connection')
        self.assertEqual(relay_data['accessKey'], 'test-access-key')
        self.assertEqual(relay_data['expiresOn'], '2025-07-04T10:00:00Z')
        self.assertEqual(relay_data['serviceConfigurationToken'], 'test-token')

    def test_format_relay_info_string_minimal_data(self):
        """Test format_relay_info_string with minimal required fields."""
        # Arrange
        relay_info = {
            'namespaceName': 'minimal',
            'namespaceNameSuffix': 'suffix',
            'hybridConnectionName': 'connection',
            'accessKey': 'key',
            'expiresOn': '2025-01-01T00:00:00Z',
            'serviceConfigurationToken': 'token'
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
        # Verify it's valid base64
        try:
            decoded = base64.b64decode(result.encode('ascii'))
            json.loads(decoded.decode('ascii'))
        except (ValueError, json.JSONDecodeError):
            self.fail("Result is not valid base64-encoded JSON")

    def test_format_relay_info_string_special_characters(self):
        """Test format_relay_info_string with special characters in data."""
        # Arrange
        relay_info = {
            'namespaceName': 'test-namespace-with-dashes',
            'namespaceNameSuffix': 'test.suffix.com',
            'hybridConnectionName': 'connection_with_underscores',
            'accessKey': 'key+with/special=chars',
            'expiresOn': '2025-12-31T23:59:59.999Z',
            'serviceConfigurationToken': 'token-with-various_special.chars'
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        relay_data = parsed_result['relay']
        self.assertEqual(relay_data['namespaceName'], 'test-namespace-with-dashes')
        self.assertEqual(relay_data['accessKey'], 'key+with/special=chars')

    def test_format_relay_info_string_unicode_characters(self):
        """Test format_relay_info_string with unicode characters."""
        # Arrange
        relay_info = {
            'namespaceName': 'test-unicode-αβγ',
            'namespaceNameSuffix': 'suffix-δεζ',
            'hybridConnectionName': 'connection-ηθι',
            'accessKey': 'key-κλμ',
            'expiresOn': '2025-06-15T12:30:45Z',
            'serviceConfigurationToken': 'token-νξο'
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        self.assertIsInstance(result, str)
        
        # Verify roundtrip encoding/decoding works
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        relay_data = parsed_result['relay']
        self.assertEqual(relay_data['namespaceName'], 'test-unicode-αβγ')

    def test_format_relay_info_string_empty_values(self):
        """Test format_relay_info_string with empty string values."""
        # Arrange
        relay_info = {
            'namespaceName': '',
            'namespaceNameSuffix': '',
            'hybridConnectionName': '',
            'accessKey': '',
            'expiresOn': '',
            'serviceConfigurationToken': ''
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        relay_data = parsed_result['relay']
        for key in relay_data:
            self.assertEqual(relay_data[key], '')

    def test_format_relay_info_string_large_values(self):
        """Test format_relay_info_string with large string values."""
        # Arrange
        large_string = 'x' * 1000  # 1000 character string
        relay_info = {
            'namespaceName': large_string,
            'namespaceNameSuffix': large_string,
            'hybridConnectionName': large_string,
            'accessKey': large_string,
            'expiresOn': '2025-07-04T10:00:00Z',
            'serviceConfigurationToken': large_string
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert
        self.assertIsInstance(result, str)
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        relay_data = parsed_result['relay']
        self.assertEqual(relay_data['namespaceName'], large_string)

    @mock.patch('json.dumps')
    def test_format_relay_info_string_json_error_handling(self, mock_dumps):
        """Test format_relay_info_string handles JSON serialization errors."""
        # Arrange
        mock_dumps.side_effect = TypeError("Object not serializable")
        relay_info = {
            'namespaceName': 'test',
            'namespaceNameSuffix': 'test',
            'hybridConnectionName': 'test',
            'accessKey': 'test',
            'expiresOn': 'test',
            'serviceConfigurationToken': 'test'
        }
        
        # Act & Assert
        with self.assertRaises(TypeError):
            connectivity_utils.format_relay_info_string(relay_info)

    def test_format_relay_info_string_structure_validation(self):
        """Test that format_relay_info_string produces the expected JSON structure."""
        # Arrange
        relay_info = {
            'namespaceName': 'test-namespace',
            'namespaceNameSuffix': 'servicebus.windows.net',
            'hybridConnectionName': 'test-connection',
            'accessKey': 'test-access-key',
            'expiresOn': '2025-07-04T10:00:00Z',
            'serviceConfigurationToken': 'test-token'
        }
        
        # Act
        result = connectivity_utils.format_relay_info_string(relay_info)
        
        # Assert - Verify the exact structure matches expectations
        decoded_bytes = base64.b64decode(result.encode('ascii'))
        decoded_string = decoded_bytes.decode('ascii')
        parsed_result = json.loads(decoded_string)
        
        # Check top-level structure
        self.assertEqual(list(parsed_result.keys()), ['relay'])
        
        # Check relay object has all required fields
        relay_data = parsed_result['relay']
        expected_keys = {
            'namespaceName', 'namespaceNameSuffix', 'hybridConnectionName',
            'accessKey', 'expiresOn', 'serviceConfigurationToken'
        }
        self.assertEqual(set(relay_data.keys()), expected_keys)


if __name__ == '__main__':
    unittest.main()
