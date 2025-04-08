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
         description="An async callback function invoked for handling sampling requests from the server. It should send data as requested by the server."
    )
    list_roots_callback: Optional[Any] = Field(
         default=None,
         description="An async callback function used to handle requests for listing roots from the server. This can be used for "
    )
    logging_callback: Optional[Any] = Field(
         default=None,
         description="An async callback function invoked to handle logging messages from the server. This will return absolutely nothing back to the server"
    )
    message_handler: Optional[Any] = Field(
         default=None,
         description="An async callback function for processing incoming messages from the server. It shouldn't be used unless you have cusom implementation perfectly in place"
    )
    # config_params: Optional[dict[str, str]] = Field(
    #     default=None,
    #     description="Optional configuration parameters to be sent to the server after the handshake. This can include session-specific settings."
    # )

class RequestConfig(BaseModel):
    """Configuration for a request to the server."""
    headers: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional headers to include in the request."
    )
    params: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional query parameters to include in the request."
    )
    body: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional body content for the request."
    )

class ResponseConfig(BaseModel):
    """Configuration for a response from the server."""
    status_code: int = Field(
        ...,
        description="HTTP status code of the response."
    )
    headers: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional headers included in the response."
    )
    body: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional body content of the response."
    )
    error: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional error information included in the response."
    )