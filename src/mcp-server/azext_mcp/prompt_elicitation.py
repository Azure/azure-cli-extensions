import asyncio
import builtins
from contextlib import contextmanager
from typing import Callable

from knack.log import get_logger

from mcp.server.fastmcp import Context

logger = get_logger(__name__)


class PromptElicitHandler:
    """Handler that intercepts knack prompts and built-in input() and uses MCP elicit for user interaction."""
    
    def __init__(self, ctx: Context):
        """Initialize with MCP context for elicit operations.
        
        Args:
            ctx: MCP Context object that provides elicit functionality
        """
        self.ctx = ctx
        self.original_functions = {}
        self._loop = None
        
    def _get_or_create_loop(self):
        """Get the current event loop or create one if needed."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create one
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
            loop = self._loop
        return loop
    
    def _run_async(self, coro):
        """Run an async coroutine from sync context."""
        loop = self._get_or_create_loop()
        if asyncio.iscoroutinefunction(coro) or asyncio.iscoroutine(coro):
            # Check if loop is already running
            if loop.is_running():
                import threading
                
                result_holder = {'result': None, 'exception': None}
                done_event = threading.Event()
                
                def run_in_thread():
                    """Run coroutine in a new event loop in this thread."""
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            result_holder['result'] = new_loop.run_until_complete(coro)
                        finally:
                            new_loop.close()
                            asyncio.set_event_loop(None)
                    except Exception as e:
                        result_holder['exception'] = e
                    finally:
                        done_event.set()
                
                # Start the thread and wait for completion
                thread = threading.Thread(target=run_in_thread, daemon=True)
                thread.start()
                
                # Wait for the thread to complete with timeout
                if done_event.wait(timeout=300):  # 5 minute timeout
                    if result_holder['exception']:
                        raise result_holder['exception']
                    return result_holder['result']
                else:
                    from knack.prompting import NoTTYException
                    raise NoTTYException("Prompt timeout")
            else:
                return loop.run_until_complete(coro)
        return coro
    
    def _create_prompt_wrapper(self) -> Callable:
        """Create a wrapper for the basic prompt function."""
        from .prompt_models import TextPrompt
        
        def prompt_wrapper(msg, help_string=None):
            prompt_msg = msg
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            
            logger.debug("Intercepting prompt: %s", msg)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, TextPrompt)
                if result.action == "accept":
                    return result.data.value
                # User cancelled - return empty string or raise based on requirements
                from knack.prompting import NoTTYException
                raise NoTTYException("User cancelled prompt")
            
            return self._run_async(async_elicit())
        
        return prompt_wrapper
    
    def _create_prompt_int_wrapper(self) -> Callable:
        """Create a wrapper for the integer prompt function."""
        from .prompt_models import IntegerPrompt
        
        def prompt_int_wrapper(msg, help_string=None):
            prompt_msg = msg
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            
            logger.debug("Intercepting integer prompt: %s", msg)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, IntegerPrompt)
                if result.action == "accept":
                    return result.data.value
                from knack.prompting import NoTTYException
                raise NoTTYException("User cancelled prompt")
            
            return self._run_async(async_elicit())
        
        return prompt_int_wrapper
    
    def _create_prompt_pass_wrapper(self) -> Callable:
        """Create a wrapper for the password prompt function."""
        from .prompt_models import PasswordPrompt
        
        def prompt_pass_wrapper(msg='Password: ', confirm=False, help_string=None):
            prompt_msg = msg
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            if confirm:
                prompt_msg += "\nYou will need to confirm the password."
            
            logger.debug("Intercepting password prompt: %s", msg)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, PasswordPrompt)
                if result.action == "accept":
                    return result.data.password
                from knack.prompting import NoTTYException
                raise NoTTYException("User cancelled prompt")
            
            return self._run_async(async_elicit())
        
        return prompt_pass_wrapper
    
    def _create_prompt_y_n_wrapper(self) -> Callable:
        """Create a wrapper for the yes/no prompt function."""
        from .prompt_models import YesNoPrompt
        
        def prompt_y_n_wrapper(msg, default=None, help_string=None):
            y = 'Y' if default == 'y' else 'y'
            n = 'N' if default == 'n' else 'n'
            prompt_msg = f"{msg} ({y}/{n})"
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            
            logger.debug("Intercepting y/n prompt: %s (default: %s)", msg, default)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, YesNoPrompt)
                if result.action == "accept":
                    return result.data.answer
                # Use default if cancelled and default exists
                if default:
                    return default == 'y'
                from knack.prompting import NoTTYException
                raise NoTTYException("User cancelled prompt")
            
            return self._run_async(async_elicit())
        
        return prompt_y_n_wrapper
    
    def _create_prompt_t_f_wrapper(self) -> Callable:
        """Create a wrapper for the true/false prompt function."""
        from .prompt_models import TrueFalsePrompt
        
        def prompt_t_f_wrapper(msg, default=None, help_string=None):
            t = 'T' if default == 't' else 't'
            f = 'F' if default == 'f' else 'f'
            prompt_msg = f"{msg} ({t}/{f})"
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            
            logger.debug("Intercepting t/f prompt: %s (default: %s)", msg, default)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, TrueFalsePrompt)
                if result.action == "accept":
                    return result.data.answer
                # Use default if cancelled and default exists
                if default:
                    return default == 't'
                from knack.prompting import NoTTYException
                raise NoTTYException("User cancelled prompt")
            
            return self._run_async(async_elicit())
        
        return prompt_t_f_wrapper
    
    def _create_prompt_choice_list_wrapper(self) -> Callable:
        """Create a wrapper for the choice list prompt function."""
        from pydantic import BaseModel, Field
        from typing_extensions import Annotated
        
        def prompt_choice_list_wrapper(msg, a_list, default=1, help_string=None):
            # Format choices for display
            options = []
            for i, x in enumerate(a_list):
                if isinstance(x, dict) and 'name' in x:
                    option_text = f"[{i+1}] {x['name']}"
                    if 'desc' in x:
                        option_text += f" - {x['desc']}"
                else:
                    option_text = f"[{i+1}] {x}"
                options.append(option_text)
            
            choices_text = '\n'.join(options)
            prompt_msg = f"{msg}\n{choices_text}\nPlease select (default: {default})"
            if help_string:
                prompt_msg += f"\n(Help: {help_string})"
            
            logger.debug("Intercepting choice prompt: %s (default: %s)", msg, default)
            
            # Create a dynamic model with the right validation
            class DynamicChoicePrompt(BaseModel):
                choice_index: Annotated[int, Field(
                    description=f"The index of the selected choice (1-{len(a_list)})",
                    ge=1,
                    le=len(a_list)
                )]
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, DynamicChoicePrompt)
                if result.action == "accept":
                    return result.data.choice_index - 1  # Convert to 0-based index
                # Use default if cancelled
                return default - 1
            
            return self._run_async(async_elicit())
        
        return prompt_choice_list_wrapper
    
    def _create_input_wrapper(self) -> Callable:
        """Create a wrapper for the built-in input() function."""
        from .prompt_models import TextPrompt
        
        def input_wrapper(prompt=''):
            prompt_msg = prompt if prompt else "Enter input:"
            
            logger.debug("Intercepting built-in input: %s", prompt)
            
            async def async_elicit():
                result = await self.ctx.elicit(prompt_msg, TextPrompt)
                if result.action == "accept":
                    return result.data.value
                # User cancelled - return empty string (matches default input behavior on EOF)
                return ""
            
            return self._run_async(async_elicit())
        
        return input_wrapper
    
    def __enter__(self):
        """Enter the context and replace prompting functions with elicit wrappers."""
        import knack.prompting
        
        # Store original functions
        self.original_functions = {
            'prompt': knack.prompting.prompt,
            'prompt_int': knack.prompting.prompt_int,
            'prompt_pass': knack.prompting.prompt_pass,
            'prompt_y_n': knack.prompting.prompt_y_n,
            'prompt_t_f': knack.prompting.prompt_t_f,
            'prompt_choice_list': knack.prompting.prompt_choice_list,
            'input': builtins.input,  # Store built-in input function
        }
        
        # Replace with our elicit-based wrappers
        knack.prompting.prompt = self._create_prompt_wrapper()
        knack.prompting.prompt_int = self._create_prompt_int_wrapper()
        knack.prompting.prompt_pass = self._create_prompt_pass_wrapper()
        knack.prompting.prompt_y_n = self._create_prompt_y_n_wrapper()
        knack.prompting.prompt_t_f = self._create_prompt_t_f_wrapper()
        knack.prompting.prompt_choice_list = self._create_prompt_choice_list_wrapper()
        builtins.input = self._create_input_wrapper()  # Replace built-in input function
        
        logger.debug("Prompt elicit handler activated (including built-in input)")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and restore original prompting functions."""
        import knack.prompting
        
        # Restore original functions
        for name, func in self.original_functions.items():
            if name == 'input':
                builtins.input = func  # Restore built-in input function
            else:
                setattr(knack.prompting, name, func)
        
        # Clear the stored references
        self.original_functions.clear()
        
        # Clean up event loop if we created one
        if self._loop:
            self._loop.close()
            self._loop = None
        
        logger.debug("Prompt elicit handler deactivated (built-in input restored)")
        return False


@contextmanager
def elicit_prompts(ctx: Context):
    """Context manager for handling CLI prompts through MCP elicit.
    
    This intercepts all knack prompt functions AND the built-in input() function
    and routes them through the MCP elicit mechanism for proper user interaction.
    
    Args:
        ctx: MCP Context object that provides elicit functionality
        
    Usage:
        with elicit_prompts(ctx):
            # Run CLI commands - any prompts (including input()) will use MCP elicit
            result = cli_bridge.invoke_command_by_json(...)
    """
    handler = PromptElicitHandler(ctx)
    with handler:
        yield handler
