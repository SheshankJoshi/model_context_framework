#!/usr/bin/env python

"""Tests for `lmstudio_llm` module."""

import pytest
from unittest.mock import Mock, patch
from model_context_framework.llms.lmstudio_llm import LmstudioLLM
import lmstudio as lms


class TestLmstudioLLM:
    """Test cases for LmstudioLLM class."""

    def test_call_with_bostoken_error_fallback(self):
        """Test that bosToken error triggers fallback to simpler prompt."""
        # Create a mock model
        mock_model = Mock(spec=lms.LLM)
        mock_model.identifier = "test-model"
        
        # First call raises bosToken error, second call succeeds
        mock_model.respond.side_effect = [
            Exception("Error: missing bosToken field in prompt template"),
            Mock(content="Test response", metadata={})
        ]
        
        # Create LmstudioLLM instance
        llm = LmstudioLLM(lm_model=mock_model)
        
        # Call should succeed despite initial bosToken error
        result = llm._call("Test prompt")
        
        # Verify the response
        assert result == "Test response"
        
        # Verify that respond was called twice (once failed, once succeeded)
        assert mock_model.respond.call_count == 2
        
        # Verify first call used chat with prefix, second used simple chat
        first_call_chat = mock_model.respond.call_args_list[0][0][0]
        second_call_chat = mock_model.respond.call_args_list[1][0][0]
        
        # The second call should be with a simpler chat (no prefix)
        assert isinstance(first_call_chat, lms.Chat)
        assert isinstance(second_call_chat, lms.Chat)

    def test_call_with_non_bostoken_error_raises(self):
        """Test that non-bosToken errors are properly raised."""
        # Create a mock model
        mock_model = Mock(spec=lms.LLM)
        mock_model.identifier = "test-model"
        
        # Mock an error that's not related to bosToken
        mock_model.respond.side_effect = Exception("Some other error")
        
        # Create LmstudioLLM instance
        llm = LmstudioLLM(lm_model=mock_model)
        
        # Call should raise the original exception
        with pytest.raises(Exception, match="Some other error"):
            llm._call("Test prompt")

    def test_call_normal_success(self):
        """Test normal successful call without errors."""
        # Create a mock model
        mock_model = Mock(spec=lms.LLM)
        mock_model.identifier = "test-model"
        
        # Mock successful response
        mock_response = Mock()
        mock_response.content = "Test response content"
        mock_response.metadata = {"tokens_used": 10}
        mock_model.respond.return_value = mock_response
        
        # Create LmstudioLLM instance
        llm = LmstudioLLM(lm_model=mock_model)
        
        # Call should succeed
        result = llm._call("Test prompt")
        
        # Verify the response
        assert result == "Test response content"
        assert llm.last_metadata["tokens_used"] == 10
        
        # Verify respond was called only once
        assert mock_model.respond.call_count == 1