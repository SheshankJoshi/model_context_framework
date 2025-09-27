import mcp.types as types
from mcp.shared.context import RequestContext
config_root = types.Root(
    uri="file://",  # Replaced with a plain string as FileUrl is not available
)


# Define your callback functions:
async def custom_sampling_callback(context: RequestContext, params: types.CreateMessageRequestParams):
    try:
        ...
    except Exception as e:
    # Custom logic; for now just return an error message.
        return types.ErrorData(code=types.INVALID_REQUEST, message="Custom sampling not supported")

async def custom_list_roots_callback(context: RequestContext):
    # Custom logic; here return error message.
    print("Request Received with context:", context)
    try:
        print("Server has requested the list of roots")
        return types.ListRootsResult(roots=["file://", "http://", "https://"])
    except Exception as e:
        return types.ErrorData(code=types.INVALID_REQUEST, message="Custom list roots not supported")

async def custom_logging_callback(params: types.LoggingMessageNotificationParams):
    # For logging notifications, you might simply print them.
    print(f"Custom logging: {params.data}")
    
async def custom_db_config_callback(context: RequestContext):
    some_condition = True  # Replace with actual condition to check for DB config
    try:
        if not some_condition:
            raise ValueError("No DB config set")
        
        return {"conn_str": "something"}
    except Exception as e:
        return types.ErrorData(code=types.INVALID_REQUEST, message=str(e))