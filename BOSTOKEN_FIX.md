# LMStudio bosToken Error Fix

## Problem Description

When using LMStudio models with certain configurations, the model may throw an error related to a missing `bosToken` field in the prompt template configuration:

```
Error: missing bosToken field in prompt template
```

This error typically occurs when the model's prompt template is incomplete or misconfigured in LMStudio.

## Solution

The fix implements error handling in the `_call` method of the `LmstudioLLM` class that detects this specific error and automatically falls back to a simpler prompt configuration.

### Implementation Details

**Location:** `src/model_context_framework/llms/lmstudio_llm.py`, line ~98

**Original Code:**
```python
response = self.lm_model.respond(chat)
```

**Fixed Code:**
```python
try:
    response = self.lm_model.respond(chat)
except Exception as e:
    if "bosToken" in str(e):
        # Fallback: try with a simpler prompt
        simple_chat = lms.Chat()
        simple_chat.add_user_message(prompt)
        response = self.lm_model.respond(simple_chat)
    else:
        raise e
```

### How It Works

1. **Normal Operation**: The method tries to use the configured chat with the prompt prefix
2. **Error Detection**: If an exception containing "bosToken" is caught, it indicates the template issue
3. **Fallback**: Creates a simpler `lms.Chat()` without the prompt prefix and retries
4. **Other Errors**: Any other exceptions are re-raised to maintain existing error handling

### Benefits

- **Automatic Recovery**: No manual intervention required when bosToken errors occur
- **Minimal Impact**: Only affects calls that would have failed anyway
- **Backward Compatible**: All existing functionality continues to work normally
- **Graceful Degradation**: Falls back to simpler prompt structure when template issues occur

### Testing

The fix includes comprehensive tests that verify:

- ✅ bosToken errors trigger the fallback mechanism
- ✅ Fallback successfully recovers and returns results
- ✅ Non-bosToken errors are properly raised
- ✅ Normal operation continues unchanged
- ✅ Async calls also handle the error correctly

### Usage

No changes are required to existing code. The error handling is automatic and transparent:

```python
from model_context_framework.llms.lmstudio_llm import get_llm

llm = get_llm()
if llm:
    # This will now automatically handle bosToken errors
    response = llm.invoke("Your question here")
    print(response)
```

### Root Cause Resolution

While this fix provides automatic recovery, the root cause should still be addressed:

1. **Check LMStudio Model Configuration**: Ensure the loaded model has a complete prompt template
2. **Reload the Model**: Try reloading the model in LMStudio
3. **Update LMStudio**: Ensure you're using a recent version of LMStudio
4. **Model Compatibility**: Some models may require specific template configurations

The fallback mechanism ensures your application continues to work while you address the underlying configuration issue.