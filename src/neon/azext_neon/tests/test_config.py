# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Test configuration for Neon CLI extension tests.
"""

# Test constants
TEST_ORGANIZATION_NAME_PREFIX = "test-neon-org"
TEST_PROJECT_NAME_PREFIX = "test-neon-project"
TEST_BRANCH_NAME_PREFIX = "test-neon-branch"
TEST_ENDPOINT_NAME_PREFIX = "test-neon-endpoint"
TEST_DATABASE_NAME_PREFIX = "test_neon_db"
TEST_ROLE_NAME_PREFIX = "test_neon_role"

# Default test values
DEFAULT_LOCATION = "centraluseuap"
DEFAULT_PG_VERSION = 17
DEFAULT_REGION_ID = "eastus2"
DEFAULT_ENDPOINT_TYPE = "read_only"

# Test marketplace details (for testing purposes)
TEST_MARKETPLACE_DETAILS = {
    "publisher_id": "neon1722366567200",
    "offer_id": "neon_serverless_postgres_azure_prod",
    "plan_id": "neon_serverless_postgres_azure_prod_free",
    "plan_name": "Free Plan",
    "term_unit": "P1M",
    "term_id": "gmz7xq9ge3py"
}

# Test user details (for testing purposes)
TEST_USER_DETAILS = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "upn": "test@example.com",
    "phone": "+1234567890"
}

# Test company details (for testing purposes)
TEST_COMPANY_DETAILS = {
    "company_name": "TestCompany",
    "country": "USA",
    "business_phone": "+1234567890"
}

# Commands that are expected to potentially fail in test environments
# (due to service limits, resource dependencies, etc.)
COMMANDS_ALLOWED_TO_FAIL = [
    "endpoint create",  # May fail due to endpoint limits
    "get-connection-uri",  # May require specific project state
    "get-postgres-version"  # May not be available in all environments
]

# Test timeout settings (in seconds)
DEFAULT_TIMEOUT = 300  # 5 minutes
LONG_RUNNING_TIMEOUT = 600  # 10 minutes

# Test retry settings
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds
