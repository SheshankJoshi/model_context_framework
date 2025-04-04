# Auto-generated on Fri Apr  4 18:58:53 2025
def dynamic_example_tool(arg1: str) -> str:
    """
    Example dynamically injected tool.
    It returns a message with the provided argument and checks for an environment key.
    Also demonstrates usage of a bound variable.
    """
    import os
    def helper():
        return "helper value"
    bound_value = helper()
    required_key = os.environ.get("EXAMPLE_CONFIG", "default")
    return f"Dynamic tool received: {arg1} with config {required_key} and bound value {bound_value}"
