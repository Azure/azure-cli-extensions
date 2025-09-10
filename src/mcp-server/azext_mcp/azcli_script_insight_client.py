"""
Simple client example showing the methods for calling Azure Function App endpoints

IMPORTANT: The what-if service requires client-side authentication to operate under the 
caller's subscription and permissions. Server-side authentication is not supported for 
what-if operations as it would not provide access to the caller's subscription.

This client now uses DefaultAzureCredential which supports multiple authentication methods:
- Azure CLI: az login
- Environment variables (service principal): AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
- Managed Identity (when running in Azure environments)
- Visual Studio/VS Code authentication
    
The what-if service will use your configured credentials to access your subscription
and preview deployment changes under your permissions.
"""

import requests
import json
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential
from datetime import datetime, timezone


# Configuration
FUNCTION_APP_URL = "https://azcli-script-insight.azurewebsites.net"


def get_azure_cli_access_token() -> Optional[str]:
    """
    Get access token for the caller's subscription using DefaultAzureCredential
    
    This uses DefaultAzureCredential which supports multiple authentication methods
    to obtain an access token that can be used to authenticate with Azure Resource Manager APIs.
    
    Returns:
        Access token string if successful, None if failed
    """
    token_info = get_azure_cli_token_info()
    return token_info.get("accessToken") if token_info else None


def get_azure_cli_token_info() -> Optional[Dict[str, Any]]:
    """
    Get complete token information using DefaultAzureCredential including expiration
    
    This function now uses DefaultAzureCredential which supports multiple authentication methods:
    - Azure CLI (az login)
    - Managed Identity (in Azure environments)
    - Environment variables (service principal)
    - Visual Studio/VS Code authentication
    - And more...
    
    Returns:
        Dictionary with token info including accessToken, expiresOn, etc., or None if failed
    """
    try:
        # Use DefaultAzureCredential for broader authentication support
        credential = DefaultAzureCredential()

        # Get access token for Azure Resource Manager
        token = credential.get_token("https://management.azure.com/.default")

        token_info = {
            "accessToken": token.token,
            "expiresOn": datetime.fromtimestamp(token.expires_on, tz=timezone.utc).isoformat(),
            "tokenType": "Bearer"
        }

        return token_info

    except Exception as e:
        print(f"Error getting access token with DefaultAzureCredential: {str(e)}")
        return None


def translate_cli_to_bicep(function_app_url: str, azcli_script: str) -> Dict[str, Any]:
    """
    Translate Azure CLI script to Bicep template
    
    Args:
        function_app_url: Base URL of your Azure Function App
        azcli_script: Azure CLI script to translate
        
    Returns:
        Dictionary with translation result
    """
    url = f"{function_app_url.rstrip('/')}/api/cli_to_bicep"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {"azcli_script": azcli_script}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "success": False}


def what_if_preview(function_app_url: str, azcli_script: str, subscription_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Preview deployment changes using Azure what-if functionality
    
    Args:
        function_app_url: Base URL of your Azure Function App
        azcli_script: Azure CLI script to analyze
        subscription_id: Optional fallback subscription ID if not in script
        
    Returns:
        Dictionary with what-if preview result
    """
    url = f"{function_app_url.rstrip('/')}/api/what_if_preview"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Validate that access token is provided (required for what-if operations)
    # Get access token from Azure CLI
    access_token = get_azure_cli_access_token()
    if not access_token:
        return {
            "error": "Failed to get access token from Azure CLI. Please ensure you are logged in with 'az login'",
            "details": "The what-if service requires client credentials to access your subscription. Please provide an access token.",
            "success": False
        }
    # Use Authorization header for access token
    headers['Authorization'] = f'Bearer {access_token}'
    
    payload = {"azcli_script": azcli_script}
    if subscription_id:
        payload["subscription_id"] = subscription_id
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "success": False}


def analyze_azcli_script(function_app_url: str, azcli_script: str) -> Dict[str, Any]:
    """
    Analyze Azure CLI script for best practices and recommendations
    
    Args:
        function_app_url: Base URL of your Azure Function App
        azcli_script: Azure CLI script to analyze
        
    Returns:
        Dictionary with analysis result
    """
    url = f"{function_app_url.rstrip('/')}/api/analyze_azcli_script"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {"azcli_script": azcli_script}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "status": "error"}


# Example usage
if __name__ == "__main__":

    # Sample Azure CLI script
    sample_script = "# Create a resource group with uppercase name  \n az group create --name azcli-script-insight --location eastus  \n   \n # Create a VM directly instead of using an ARM template  \n az vm create --resource-group azcli-script-insight --name MyVM_01 --image UbuntuLTS --size Standard_D2s_v3 --admin-username azureuser --generate-ssh-keys  \n   \n # Create a VMSS without auto-scaling  \n az vmss create --resource-group azcli-script-insight --name MyVMSS --image UbuntuLTS --instance-count 3 --admin-username azureuser --generate-ssh-keys \n # Create a web app without managed identity  \n az webapp create --resource-group azcli-script-insight --plan MyAppServicePlan --name MyWebApp  \n   \n # Create duplicate resource group (redundant)  \n az group create --name azcli-script-insight --location eastus  \n   \n # Loop through VMs and query details individually (inefficient)  \n for vm in $(az vm list --resource-group azcli-script-insight --query \"[].name\" -o tsv); do  \n     az vm show --resource-group azcli-script-insight --name $vm  \n done"
    # 1. Translate CLI to Bicep
    print("=== CLI to Bicep Translation ===")
    translation_result = translate_cli_to_bicep(FUNCTION_APP_URL, sample_script)
    if translation_result.get("success"):
        print("Translation successful!")
        print(f"Bicep Template:\n{translation_result['bicep_template']}")
    else:
        print(f"Translation failed: {translation_result.get('error')}")
    
    # 2. What-If Preview (requires client-side Azure CLI credentials)
    print("\n=== What-If Preview (Client-side Azure CLI Auth) ===")
    whatif_cli_result = what_if_preview(FUNCTION_APP_URL, sample_script, subscription_id = '6b085460-5f21-477e-ba44-1035046e9101')
    if whatif_cli_result.get("success"):
        print("What-if preview with CLI auth successful!")
        print(f"Changes: {json.dumps(whatif_cli_result['what_if_result'], indent=2)}")
    else:
        print(f"{whatif_cli_result}")

    # 3. Analyze Script
    print("\n=== Script Analysis ===")
    analysis_result = analyze_azcli_script(FUNCTION_APP_URL, sample_script)
    if analysis_result.get("status") == "success":
        print("Analysis successful!")
        print(f"Analysis: {json.dumps(analysis_result['analysis'], indent=2)}")
    else:
        print(f"Analysis failed: {analysis_result.get('error')}")
