from pydantic import BaseModel, Field
from typing import Any, Optional

class SSEConnection(BaseModel):
    url: str = Field(
        ...,
        description="The URL of the SSE endpoint. This should include the protocol (http/https) and the host address."
    )
    headers: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional HTTP headers to include when connecting to the SSE endpoint (e.g., authentication tokens)."
    )
    timeout: float = Field(
        ...,
        description="The HTTP connection timeout in seconds. This is how long to wait for the connection to be established."
    )
    sse_read_timeout: float = Field(
        ...,
        description="The timeout in seconds for reading SSE events from the server. It defines the maximum wait time for receiving new events."
    )

class ClientSessionConfig(BaseModel):
    read_timeout_seconds: Optional[float] = Field(
         default=None,
         description="The timeout in seconds for reading from the input stream. This value defines how long the client waits for a message before timing out."
    )
    sampling_callback: Optional[Any] = Field(
         default=None,
         description="An async callback function invoked for handling sampling messages from the server."
    )
    list_roots_callback: Optional[Any] = Field(
         default=None,
         description="An async callback function used to handle requests for listing roots from the server."
    )
    logging_callback: Optional[Any] = Field(
         default=None,
         description="An async callback function invoked to handle logging messages from the server."
    )
    message_handler: Optional[Any] = Field(
         default=None,
         description="An async callback function for processing incoming messages from the server."
    )
