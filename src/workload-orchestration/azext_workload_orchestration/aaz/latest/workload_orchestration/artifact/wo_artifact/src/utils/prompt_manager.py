"""
Manages loading and validation of GPT prompts
"""
import os
from typing import Optional
from utils.logger import LoggerMixin

class PromptManager(LoggerMixin):
    """
    Manages loading and validation of analysis prompts.
    Supports both default and custom prompts.
    """
    
    def __init__(self, prompt_path: Optional[str] = None):
        """
        Initialize prompt manager.
        
        Args:
            prompt_path: Optional path to custom prompt file
        """
        super().__init__()
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.prompts_dir = os.path.join(self.root_dir, 'prompts')
        self.default_prompt_path = os.path.join(self.prompts_dir, 'default', 'prompt.txt')
        self.custom_prompt_path = prompt_path

    def get_prompt(self) -> str:
        """
        Get prompt content, either from custom file or default.
        
        Returns:
            Prompt content as string
        """
        try:
            if self.custom_prompt_path:
                full_path = (
                    self.custom_prompt_path 
                    if os.path.isabs(self.custom_prompt_path)
                    else os.path.join(self.prompts_dir, self.custom_prompt_path)
                )
                
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        self.logger.info(f"Using custom prompt from: {full_path}")
                        return f.read()
                else:
                    self.logger.warning(
                        f"Custom prompt {full_path} not found, using default"
                    )
            
            # Fallback to default prompt
            return self._get_default_prompt()
            
        except Exception as e:
            self.logger.error(f"Error loading prompt: {str(e)}")
            return self._get_default_prompt()
            
    def _get_default_prompt(self) -> str:
        """
        Get default prompt content.
        
        Returns:
            Default prompt content
        """
        try:
            with open(self.default_prompt_path, 'r') as f:
                content = f.read()
            self.logger.info("Using default prompt")
            return content
        except Exception as e:
            self.logger.error(f"Failed to load default prompt: {str(e)}")
            raise RuntimeError("Could not load any valid prompt")
