# Model Context Framework

## Overview

The **Model Context Framework** is a comprehensive Python framework designed to develop, experiment with, and extend tools for the **Model Context Protocol (MCP)** to enhance AI contextualization and agent interactions. This framework provides both client and server implementations, advanced tool management, and seamless integration with popular AI frameworks like AutoGen.

## What is This Framework?

This framework implements and extends the Model Context Protocol (MCP), which is a protocol for enabling AI models to access external tools, resources, and context in a standardized way. The framework includes:

- **Advanced MCP Server Implementation**: Extended server capabilities with dynamic tool loading, session management, and custom routing
- **Sophisticated MCP Client**: Enhanced client with session configuration, context management, and LangChain integration  
- **AutoGen Integration**: Seamless integration with Microsoft's AutoGen for multi-agent conversations
- **Dynamic Tool System**: Runtime tool registration, persistence, and environment-based configuration
- **Rich Examples**: Comprehensive examples demonstrating various usage patterns

## Key Features

### 🚀 **Extended MCP Server (ExtendedMCP)**
- **Dynamic Tool Registration**: Add tools at runtime with automatic persistence
- **Session Management**: Advanced session handling with custom configuration support
- **Custom Routing**: Add custom HTTP endpoints alongside MCP functionality
- **Environment Injection**: Automatically inject environment variables based on client configuration
- **Tool Persistence**: Save and restore tools across server restarts

### 🔌 **Advanced MCP Client**
- **Custom Session Management**: Enhanced client sessions with configuration support
- **Context Management**: Dynamic context switching during sessions  
- **LangChain Integration**: Convert MCP tools to LangChain-compatible tools
- **SSE & STDIO Support**: Support for both Server-Sent Events and standard I/O transport

### 🤖 **AutoGen Integration**
- **Azure OpenAI Support**: Pre-configured Azure OpenAI model clients
- **Agent Creation**: Simple assistant agents with streaming support
- **Web Browsing Agents**: Multimodal web surfing capabilities with Playwright
- **Team Orchestration**: Multi-agent conversation management

### 🛠️ **Built-in Tools**
- **Google Search**: Web search capabilities with configurable result limits
- **PowerPoint Generation**: Create presentations with titles, content, and references
- **Reference Processing**: Format and process citation lists
- **Custom Tool Loading**: Dynamic tool loading from code or function mappings

## Architecture

```
model_context_framework/
├── mcp_server/          # Extended MCP server implementations
│   ├── mcp_extension.py # Core ExtendedMCP class
│   ├── mcp_server_sse.py # SSE server example
│   └── plain_server_*.py # Alternative server implementations
├── mcp_client/          # Enhanced MCP client implementations  
│   ├── detailed_client_sse.py # Advanced SSE client
│   ├── langchain_client_adapter.py # LangChain integration
│   └── tool_injector.py # Tool injection utilities
├── autogen/            # AutoGen integration
│   ├── agents.py       # Agent definitions
│   ├── config.py       # Model client configuration
│   └── autogen_example*.py # Usage examples
├── tools/              # Tool implementations
│   ├── standard_tools.py # Built-in tools
│   └── persist_tools/  # Dynamically persisted tools
├── config/             # Configuration models
└── examples/           # Comprehensive examples
```

## Quick Start

### 1. Start an MCP Server

```python
from mcp_server.mcp_server_sse import mcp

# The server automatically includes built-in tools and runs on localhost:8010
if __name__ == "__main__":
    mcp.run(transport="sse")
```

### 2. Connect with MCP Client

```python
import asyncio
from mcp_client.detailed_client_sse import get_an_mcp_session, SSEConnection, ClientSessionConfig

# Configure connection
connection_params = SSEConnection(
    url="http://localhost:8010/sse",
    headers={},
    timeout=30.0,
    sse_read_timeout=30.0
)

session_params = ClientSessionConfig()

async def example():
    async with get_an_mcp_session("sse", connection_params, session_params) as session:
        # Call server tools
        result = await session.call_tool("echo_tool", {"message": "Hello!"})
        print(result)

asyncio.run(example())
```

### 3. Use with AutoGen

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent  
from autogen.config import mcp_model_client

async def chat_example():
    agent = AssistantAgent("assistant", model_client=mcp_model_client)
    result = await agent.run(task="Say hello and tell me about yourself!")
    await mcp_model_client.close()

asyncio.run(chat_example())
```

## Advanced Features

### Dynamic Tool Registration

Add tools to the server at runtime:

```python
# Add via HTTP API
import requests

tool_data = {
    "name": "my_custom_tool",
    "func_name": "my_function", 
    "description": "A custom tool",
    "code": "def my_function(x): return x * 2",
    "persist": True
}

response = requests.post("http://localhost:8010/dynamic/add_tool", json=tool_data)
```

### Session Configuration

Clients can send configuration that gets injected as environment variables:

```python
custom_context = {
    "API_KEY": "secret_key",
    "DATABASE_URL": "postgresql://..."
}

async with get_an_mcp_session("sse", connection_params, session_params, context=custom_context) as session:
    # Server tools can now access these via os.environ
    result = await session.call_tool("database_tool", {})
```

### LangChain Integration

Convert MCP tools to LangChain tools:

```python  
from langchain_mcp_adapters.tools import load_mcp_tools

async with get_an_mcp_session("sse", connection_params, session_params) as session:
    langchain_tools = await load_mcp_tools(session)
    result = await langchain_tools[0].arun({"message": "test"})
```

## Built-in Tools

### Google Search Tool
- Search Google with configurable result limits
- Requires Google Search API credentials

### PowerPoint Generation Tool  
- Create presentations with title and content slides
- Automatic reference slide generation
- Saves to current working directory

### Reference Processing Tool
- Format and process citation lists
- Clean text output for academic use

## Examples

The framework includes comprehensive examples:

- **Basic MCP Server/Client**: Simple echo server and client interaction
- **AutoGen Integration**: Multi-agent conversations with web browsing
- **Dynamic Tool Loading**: Runtime tool registration and persistence
- **Session Management**: Advanced client configuration examples

## Configuration

### Server Configuration
```python
mcp_settings = {
    "host": "127.0.0.1", 
    "port": 8010,
    "sse_path": "/sse",
    "message_path": "/messages/",
    "log_level": "DEBUG"
}
```

### Client Configuration  
```python
connection_params = SSEConnection(
    url="http://localhost:8010/sse",
    headers={},
    timeout=30.0,
    sse_read_timeout=30.0
)

session_params = ClientSessionConfig(
    logging_callback=custom_logging_callback
)
```

## Installation

```bash
# Clone the repository
git clone https://github.com/SheshankJoshi/model_context_framework.git
cd model_context_framework

# Install dependencies
pip install -r requirements_dev.txt

# Install the package in development mode
pip install -e .
```

## Dependencies

- **mcp**: Core Model Context Protocol implementation
- **fastmcp**: FastMCP server framework  
- **autogen-agentchat**: Microsoft AutoGen framework
- **langchain**: LangChain framework integration
- **pydantic**: Data validation and configuration
- **starlette**: ASGI web framework for server
- **python-pptx**: PowerPoint generation
- **httpx**: HTTP client library

## Development

### Running Tests
```bash
pytest tests/
```

### Running Examples
```bash
# Start server
python src/model_context_framework/mcp_server/mcp_server_sse.py

# In another terminal, run client
python src/model_context_framework/test_client.py
```

## Use Cases

- **AI Agent Development**: Build sophisticated AI agents with external tool access
- **Research and Experimentation**: Prototype new MCP capabilities and extensions
- **Multi-Agent Systems**: Create complex agent interactions with AutoGen integration  
- **Tool Integration**: Seamlessly connect AI models to external APIs and services
- **Educational Projects**: Learn about the Model Context Protocol and AI agent architectures

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality  
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- **Author**: Sheshank Joshi (sheshank.joshi@gmail.com)  
- **Framework**: Built on the Model Context Protocol specification
- **Template**: Created with Cookiecutter and audreyr/cookiecutter-pypackage

## Links

- **Repository**: https://github.com/SheshankJoshi/model_context_framework
- **Issues**: https://github.com/SheshankJoshi/model_context_framework/issues
- **Documentation**: https://model-context-framework.readthedocs.io

---

## What Makes This Framework Special?

This framework goes beyond basic MCP implementations by providing:

1. **Production-Ready Extensions**: Advanced session management, dynamic tool loading, and robust error handling
2. **Seamless Integration**: Works with popular AI frameworks like AutoGen and LangChain out of the box  
3. **Developer Experience**: Rich examples, clear documentation, and intuitive APIs
4. **Flexibility**: Supports both SSE and STDIO transports, custom routing, and environment-based configuration
5. **Extensibility**: Easy to add new tools, customize behavior, and integrate with existing systems

Whether you're building AI agents, experimenting with the Model Context Protocol, or creating sophisticated multi-agent systems, this framework provides the tools and infrastructure you need to succeed.