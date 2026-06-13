"""
Azure OpenAI API client implementation
"""

import openai
from openai import AsyncAzureOpenAI
from typing import Dict, List, Any, Optional
import tiktoken
import asyncio
import json
import re
from utils.logger import LoggerMixin

class AzureOpenAIClient(LoggerMixin):
    """Client for interacting with Azure OpenAI API"""
    
    GPT4_MAX_TOKENS = 8192  # GPT-4 context window
    GPT35_MAX_TOKENS = 4096  # GPT-3.5 context window
    RESPONSE_TOKENS = 1000  # Reserve tokens for response
    BATCH_SIZE = 6  # Process 6 parameters per batch
    
    def __init__(self, endpoint: str, api_key: str, deployment: str,
                 hierarchy_levels: Optional[List[str]] = None):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Model deployment name
            hierarchy_levels: Optional list of hierarchy levels
        """
        super().__init__()
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version="2023-05-15",
            azure_endpoint=endpoint
        )
        self.deployment = deployment
        self.hierarchy_levels = hierarchy_levels or ['factory', 'line']
        
        # Set model-specific configurations
        self.is_gpt4 = "gpt-4" in deployment.lower() or "gpt4" in deployment.lower()
        self.max_tokens = self.GPT4_MAX_TOKENS if self.is_gpt4 else self.GPT35_MAX_TOKENS
        self.available_tokens = self.max_tokens - self.RESPONSE_TOKENS
        self.encoding = tiktoken.encoding_for_model("gpt-4" if self.is_gpt4 else "gpt-3.5-turbo")
        
    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        tokens = self.encoding.encode(text)
        return len(tokens)
    
    def _create_batches(self, items: List[Dict[str, Any]], 
                       system_prompt: str) -> List[List[Dict[str, Any]]]:
        """Create batches of fixed size while respecting token limits"""
        batches = []
        current_batch = []
        current_tokens = self._count_tokens(system_prompt)
        
        for item in items:
            item_tokens = self._count_tokens(json.dumps(item))
            if len(current_batch) >= self.BATCH_SIZE or current_tokens + item_tokens > self.available_tokens:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [item]
                current_tokens = self._count_tokens(system_prompt) + item_tokens
            else:
                current_batch.append(item)
                current_tokens += item_tokens
                
        if current_batch:
            batches.append(current_batch)
            
        return batches
    
    async def analyze_parameters(self, parameters: List[Dict[str, Any]], 
                               system_prompt: str, 
                               max_retries: int = 3) -> Dict[str, Dict[str, Any]]:
        """Analyze parameters using Azure OpenAI"""
        results = {}
        batches = self._create_batches(parameters, system_prompt)
        
        # Create response template with current hierarchy levels
        response_template = self._create_response_template()
        
        for batch_idx, batch in enumerate(batches):
            self.logger.info(f"Processing batch {batch_idx + 1} of {len(batches)}")
            
            # Format batch parameters for prompt
            param_text = json.dumps(batch, indent=2)
            prompt = (
                f"{system_prompt}\n\n"
                f"{response_template}\n\n"
                f"Parameters to analyze (use exact names):\n{param_text}"
            )
            
            for attempt in range(max_retries):
                try:
                    messages = [
                        {"role": "system", "content": "You are a specialized Kubernetes Configuration Analyzer. You must use exact parameter names and follow the format strictly."},
                        {"role": "user", "content": prompt}
                    ]
                    
                    response = await self.client.chat.completions.create(
                        model=self.deployment,
                        messages=messages,
                        temperature=0.0,
                        max_tokens=self.RESPONSE_TOKENS,
                        n=1,
                        response_format={"type": "json_object"}
                    )
                    
                    # Get response content
                    result_text = response.choices[0].message.content
                    
                    # Parse and validate response
                    batch_results = self._parse_response(result_text)
                    if batch_results:
                        results.update(batch_results)
                        break
                    elif attempt < max_retries - 1:
                        # Retry with more explicit instructions
                        prompt = self._add_error_context(prompt, result_text)
                        await asyncio.sleep(2 ** attempt)
                        
                except Exception as e:
                    self.logger.error(f"Error processing batch {batch_idx + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        self.logger.warning(f"Failed to process batch after {max_retries} attempts")
                    else:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return results
    
    def _create_response_template(self) -> str:
        """Create response template with current hierarchy levels"""
        levels_str = "|".join([f'"{level}"' for level in self.hierarchy_levels])
        return f"""
You must return a JSON object with parameter analysis results. Each parameter name should use the exact full path from the input.

Required Format:
{{
    "parameter_name": {{
        "configurable": true/false,
        "managed_by": "IT/OT",
        "edit_level": {levels_str},
        "required": true/false
    }}
}}

Rules:
1. Use EXACT parameter names from input
2. All fields are required for each parameter
3. managed_by must be "IT" or "OT"
4. edit_level must be one of: {self.hierarchy_levels}
5. required must be true/false

Configurable Parameter Guidelines:
- Set to true if parameter should be modifiable in production
- Set to false for fixed and static system configurations
- Consider the following factors:
  * Runtime modifiability needs
  * Operational flexibility requirements
  * System stability impact
  * Security implications
  * Compliance requirements

Parameters typically configurable:
- Resource allocations (memory, CPU)
- Connection settings (ports, endpoints)
- Performance tuning parameters
- Operational thresholds
- Environment-specific values

Parameters typically not configurable:
- Core security settings
- System identifiers
- Protocol versions
- Fixed architectural components
- Compliance-mandated values

Hierarchy (edit_level) Understanding:
- Parameters at higher levels affect all environments below them
- Changes at higher levels have broader organizational impact
- Lower level parameters are more specific to local environments
- Consider the scope of impact when determining hierarchy level
- Parameters that affect multiple environments should be managed higher
- Local customizations should be allowed at appropriate levels
- Critical security and compliance settings belong at higher levels
- Operational parameters typically belong at levels closer to usage

IT (Information Technology) Context:
- Manages enterprise-wide security and infrastructure
- Handles authentication, certificates, and security policies
- Controls infrastructure configurations and networking
- Responsible for system-wide monitoring and compliance

OT (Operational Technology) Context:
- Manages factory-specific operational parameters
- Controls production-related configurations
- Handles day-to-day operational adjustments
- Responsible for local performance optimization

Required Field Guidelines:
- Set to true if parameter must be in solution template
- Set to false if parameter can be omitted from template"""

    def _add_error_context(self, prompt: str, failed_response: str) -> str:
        """Add error context to prompt for retry attempts"""
        error_context = (
            "\nPrevious response was invalid. Common issues found:\n"
            "1. Parameter names must match input exactly\n"
            "2. Each parameter must have all required fields\n"
            "3. managed_by must be exactly 'IT' or 'OT'\n"
            f"4. edit_level must be one of: {self.hierarchy_levels}\n"
            f"\nInvalid response was:\n{failed_response}\n\n"
            "Try again with the EXACT parameter names from the input."
        )
        return f"{prompt}\n{error_context}"
    
    def _parse_response(self, response: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """Parse and validate the API response"""
        try:
            # Find JSON content (handle cases where there might be additional text)
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                self.logger.error("No JSON content found in response")
                return None
            
            json_str = response[start:end]
            
            # Try to parse JSON
            result = json.loads(json_str)
            
            # Validate structure
            if not isinstance(result, dict):
                self.logger.error("Response is not a dictionary")
                return None
                
            # Validate each parameter result
            validated = {}
            for param_name, param_data in result.items():
                if self._validate_parameter_result(param_data):
                    validated[param_name] = param_data
                else:
                    self.logger.warning(f"Invalid result format for parameter {param_name}")
                    self.logger.warning(f"Invalid data: {param_data}")
                    
            return validated if validated else None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Invalid JSON: {json_str}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing response: {str(e)}")
            return None
            
    def _validate_parameter_result(self, result: Any) -> bool:
        """Validate the structure of a parameter result"""
        try:
            required_fields = {
                'configurable': lambda x: isinstance(x, bool),
                'managed_by': lambda x: x in ('IT', 'OT'),
                'edit_level': lambda x: x in self.hierarchy_levels,
                'required': lambda x: isinstance(x, bool)
            }
            
            return (
                isinstance(result, dict) and
                all(field in result for field in required_fields) and
                all(check(result[field]) for field, check in required_fields.items())
            )
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
