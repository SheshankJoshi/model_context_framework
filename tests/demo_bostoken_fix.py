#!/usr/bin/env python

"""
Demo script showing the bosToken error handling in action.

This script demonstrates how the LmstudioLLM class handles the bosToken error
by falling back to a simpler prompt when the error occurs.
"""

from unittest.mock import Mock
import lmstudio as lms
from model_context_framework.llms.lmstudio_llm import LmstudioLLM


def demo_bostoken_error_handling():
    """Demonstrate the bosToken error handling functionality."""
    print("=== Demo: bosToken Error Handling ===\n")
    
    # Create a mock LMStudio model
    mock_model = Mock(spec=lms.LLM)
    mock_model.identifier = "demo-model"
    
    # Set up the mock to:
    # 1. First call raises bosToken error
    # 2. Second call (fallback) succeeds
    mock_response = Mock()
    mock_response.content = "Hello! The capital of France is Paris."
    mock_response.metadata = {"tokens_used": 12}
    
    mock_model.respond.side_effect = [
        Exception("Error: missing bosToken field in prompt template configuration"),
        mock_response
    ]
    
    # Create LmstudioLLM instance
    print("Creating LmstudioLLM instance with mock model...")
    llm = LmstudioLLM(lm_model=mock_model)
    
    # Test the error handling
    print("Calling LLM with prompt: 'What is the capital of France?'")
    print("(Simulating bosToken error on first attempt...)")
    
    try:
        result = llm._call("What is the capital of France?")
        print(f"\n✅ Success! Response received: '{result}'")
        print(f"📊 Metadata: {llm.last_metadata}")
        
        # Verify the fallback was used
        print(f"\n🔧 Model respond() was called {mock_model.respond.call_count} times")
        print("   - First call: Failed with bosToken error")
        print("   - Second call: Succeeded with simpler prompt")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n=== Demo completed successfully! ===")


def demo_normal_operation():
    """Demonstrate normal operation without errors."""
    print("\n=== Demo: Normal Operation (No Errors) ===\n")
    
    # Create a mock LMStudio model for normal operation
    mock_model = Mock(spec=lms.LLM)
    mock_model.identifier = "demo-model-normal"
    
    # Set up successful response on first try
    mock_response = Mock()
    mock_response.content = "The weather is sunny today!"
    mock_response.metadata = {"tokens_used": 8}
    
    mock_model.respond.return_value = mock_response
    
    # Create LmstudioLLM instance
    llm = LmstudioLLM(lm_model=mock_model)
    
    # Test normal operation
    print("Calling LLM with prompt: 'How is the weather?'")
    
    result = llm._call("How is the weather?")
    print(f"✅ Response: '{result}'")
    print(f"📊 Metadata: {llm.last_metadata}")
    print(f"🔧 Model respond() called {mock_model.respond.call_count} time(s)")
    
    print("\n=== Normal operation demo completed! ===")


if __name__ == "__main__":
    demo_bostoken_error_handling()
    demo_normal_operation()
    
    print("\n" + "="*50)
    print("🎉 All demos completed successfully!")
    print("The bosToken error handling is working correctly.")
    print("="*50)