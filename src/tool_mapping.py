# You can dynamically place your tools externally, and then map them here so that they can be loaded dynamically.
# It is possible to send a whole file or a python module containing a bunch of functions, on to the server,
# and then map them here.

def Hello(name: str) -> str:
    """Return a greeting message."""
    # This function is a placeholder for a tool that returns a greeting message.
    # It takes a name as input and returns a string.
    # The function is defined to be compatible with the MCP framework.
    # The docstring is used to provide a description of the tool.
    return f"Hello {name}!"

def Goodbye(name: str) -> str:
    """Return a farewell message."""
    # This function is a placeholder for a tool that returns a farewell message.
    # It takes a name as input and returns a string.
    # The function is defined to be compatible with the MCP framework.
    # The docstring is used to provide a description of the tool.
    return f"Goodbye {name}!"

mapping_tools = {"Hello": Hello,
                 "Goodbye": Goodbye}
