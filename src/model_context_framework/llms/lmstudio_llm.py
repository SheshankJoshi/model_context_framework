"""
LMStudio LLM Wrapper for LangChain Integration.

This module provides a LangChain-compatible wrapper for LMStudio LLM models,
enabling easy integration of local LMStudio models into LangChain workflows.

The wrapper handles model loading, conversation management, and response processing
while providing comprehensive error handling for common issues like server 
connectivity and model availability.

Usage:
    from model_context_framework.llms.lmstudio_llm import get_llm
    
    llm = get_llm()
    if llm:
        response = llm.invoke("Your question here")
        print(response)

Requirements:
    - LMStudio server running on localhost:1234
    - At least one model loaded in LMStudio  
    - lmstudio Python package installed
"""

from __future__ import annotations
from langchain.llms.base import LLM
import lmstudio as lms
import asyncio
import re
from typing import Optional, Any, Sequence
from pydantic import Field

LMSTUDIO_SERVER_API_HOST = "localhost:1234"

# This must be the *first* SDK interaction (otherwise the SDK will
# implicitly attempt to access the default server instance)
default_client = lms.get_default_client(LMSTUDIO_SERVER_API_HOST)

class LmstudioLLM(LLM):
    """
    A LangChain LLM wrapper for LMStudio LLM models.
    
    This class provides a LangChain-compatible interface to LMStudio models,
    enabling seamless integration with LangChain workflows and applications.
    
    Attributes:
        lm_model: The underlying LMStudio LLM model instance
        prompt_prefix: System prompt prefix for all conversations
        last_metadata: Metadata from the most recent model response
        
    Example:
        >>> llm = get_llm()  # Get an LMStudio LLM instance
        >>> if llm:
        ...     response = llm.invoke("What is the capital of France?")
        ...     print(response)
    """
    lm_model: lms.LLM = Field(...)
    prompt_prefix: str = Field("You are a helpful assistant, who just answers questions promptly")
    last_metadata: dict = Field(default_factory=dict)

    class Config:
        extra = "allow"

    def __init__(
        self,
        lm_model: Optional[lms.LLM] = None,
        prompt_prefix: str = "You are a helpful assistant, who just answers questions promptly",
        **kwargs: Any
    ):
        # If no model is provided, load the default
        if not lm_model:
            client = lms.get_default_client(LMSTUDIO_SERVER_API_HOST)
            loaded_models = client.list_loaded_models()
            if not loaded_models:
                raise ValueError("No models loaded. Please load a model first.")
            lm_model = loaded_models[0]  # type: ignore
            if not isinstance(lm_model, lms.LLM):
                raise ValueError("Provided model is not a valid lmstudio model.")
        # Pass the required fields to the BaseModel constructor.
        super().__init__(
            name=lm_model.identifier,
            verbose=True,
            lm_model=lm_model,  #type: ignore
            prompt_prefix=prompt_prefix, #type: ignore
            last_metadata={}, #type: ignore
            **kwargs
        )

    @property
    def _llm_type(self) -> str:
        return "lmstudio"

    def _call(self, prompt: str, stop: Optional[Sequence[str]] = None, run_manager: Any = None, **kwargs: Any) -> str:
        # Create a fresh chat with the prompt prefix, then add the user prompt.
        chat = lms.Chat(self.prompt_prefix)
        chat.add_user_message(prompt)
        # Call the model synchronously with error handling for bosToken issues.
        try:
            response = self.lm_model.respond(chat)
        except Exception as e:
            if "bosToken" in str(e):
                # Fallback: try with a simpler prompt
                simple_chat = lms.Chat()
                simple_chat.add_user_message(prompt)
                response = self.lm_model.respond(simple_chat)
            else:
                # Re-raise other exceptions as they are unrelated to bosToken issue
                raise e
        # Extract response text and metadata.
        if not isinstance(response, str):
            try:
                text = response.content
                meta = getattr(response, "metadata", {})
            except AttributeError:
                text = str(response)
                meta = {}
        else:
            text = response
            meta = {}

        # --- Extract LLM Metadata ---
        if "tokens_used" not in meta:
            meta["estimated_tokens"] = len(text.split())
        object.__setattr__(self, "last_metadata", meta)
        # --- End of Metadata Extraction ---

        # --- Temporary Fix Start ---
        if "</think>" in text and "<think>" not in text:
            index = text.find("</think>")
            text = text[:index] + "<think>" + text[index:]
        # --- Temporary Fix End ---

        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        return text.strip()

    async def _acall(self, prompt: str, stop: Optional[Sequence[str]] = None, run_manager: Any = None, **kwargs: Any) -> str:
        return await asyncio.to_thread(self._call, prompt, stop=stop, run_manager=run_manager, **kwargs)

    def predict(self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any) -> str:
        return self._call(text, stop=stop, **kwargs)

    def invoke(self, input: Any, config: Optional[Any] = None, **kwargs: Any) -> str:
        # Assumes that input has a to_string() method.
        stop = config.stop if config and hasattr(config, "stop") else None
        if isinstance(input, str):
            inp = input
        elif hasattr(input, "to_string"):
            inp = input.to_string()
        else:
            inp = str(input)
        return self._call(inp, stop=stop, **kwargs)

def get_llm() -> Optional[LmstudioLLM]:
    """
    Get an LMStudio LLM instance with proper error handling.
    
    Returns:
        LmstudioLLM instance if LMStudio is running and has models loaded, None otherwise.
        
    Raises:
        No exceptions are raised - all errors are caught and logged.
    """
    try:
        loaded_models = default_client.list_loaded_models()
        if not loaded_models:
            print("Warning: No models are loaded in LMStudio. Please load a model first.")
            return None
            
        model = loaded_models[0]
        print(f"Successfully connected to LMStudio. Using model: {model}")
        
        llm = LmstudioLLM(
            lm_model=model,  # type: ignore
            prompt_prefix="You are a helpful assistant, who just answers questions promptly"
        )
        return llm
    except Exception as e:
        print(f"Error connecting to LMStudio: {e}")
        print("Please ensure:")
        print("1. LMStudio is running")
        print("2. LMStudio server is accessible at localhost:1234")
        print("3. At least one model is loaded in LMStudio")
        return None

if __name__ == "__main__":
    print("Testing LMStudio LLM wrapper...")
    llm = get_llm()
    if llm:
        print("\nTesting with a simple question...")
        result = llm.invoke("What is the capital of France?")
        print(f"Response: {result}")
        print(f"Metadata: {llm.last_metadata}")
        print("\nLMStudio LLM wrapper is working correctly!")
    else:
        print("\nLMStudio LLM wrapper test failed - no model available.")
        print("Please start LMStudio and load a model, then try again.")
