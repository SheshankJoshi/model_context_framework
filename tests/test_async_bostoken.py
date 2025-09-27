#!/usr/bin/env python

"""Test async functionality with bosToken error handling."""

import asyncio
from unittest.mock import Mock
from model_context_framework.llms.lmstudio_llm import LmstudioLLM
import lmstudio as lms


async def test_async_bostoken_handling():
    """Test that async calls also handle bosToken errors correctly."""
    print("Testing async bosToken error handling...")
    
    # Create a mock model
    mock_model = Mock(spec=lms.LLM)
    mock_model.identifier = "test-async-model"
    
    # Mock response for fallback
    mock_response = Mock()
    mock_response.content = "Async response: Hello World!"
    mock_response.metadata = {"tokens_used": 5}
    
    # First call raises bosToken error, second succeeds
    mock_model.respond.side_effect = [
        Exception("Error: missing bosToken field in prompt template"),
        mock_response
    ]
    
    # Create LLM instance
    llm = LmstudioLLM(lm_model=mock_model)
    
    # Test async call
    result = await llm._acall("Test async prompt")
    
    print(f"✅ Async call succeeded: '{result}'")
    print(f"📊 Metadata: {llm.last_metadata}")
    print(f"🔧 Model respond() called {mock_model.respond.call_count} times")
    
    assert result == "Async response: Hello World!"
    assert mock_model.respond.call_count == 2


async def main():
    """Run the async test."""
    print("=== Async bosToken Handling Test ===\n")
    await test_async_bostoken_handling()
    print("\n=== Async test completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(main())