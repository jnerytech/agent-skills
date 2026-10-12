# Chapter 13: Building and consuming MCP servers

## Core Idea
The Model Context Protocol (MCP) replaces bespoke, per-team tool wrappers with a standardized client/server architecture, so agents (MCP hosts) discover and invoke tools from any MCP server — local or remote — exactly as they would local tools.

## Frameworks Introduced
- **Model Context Protocol (MCP) host/client/server architecture**: a classic client/server model where the MCP host process (the agent or application) connects to one or more MCP servers via an MCP client; each server exposes a collection of tools (and optionally prompts/resources) the host can selectively use.
  - When to use: whenever an agent needs to consume external context (APIs, databases, files, services) without hand-rolling a wrapper for each source.
  - How: (1) a provider exposes its service as an MCP server (local via STDIO or remote via Streamable HTTP); (2) the agent's MCP client connects and lists available tools; (3) the agent invokes tools through the same tool-calling protocol used for local tools.
- **FastMCP 2**: the actively maintained, community-driven Python SDK for building and consuming MCP servers, superseding FastMCP 1.
  - When to use: to implement an MCP server (decorator-based tool definition) or a lightweight test client, without reimplementing the protocol from scratch.
  - How: decorate an async function with `@mcp.tool(...)`, instantiate `FastMCP("name")`, and call `mcp.run(transport=..., host=..., port=..., path=...)`; on the client side, use `fastmcp.Client` with a `StreamableHttpTransport`.
- **MultiServerMCPClient (LangChain/LangGraph MCP integration)**: aggregates and consumes tools from multiple MCP servers via a simple configuration dict, converting them into native LangChain tools.
  - When to use: when building LangGraph/LangChain agents that must combine MCP-served tools with local, framework-native tools in the same agent.
  - How: instantiate `MultiServerMCPClient({server_name: {"url": ..., "transport": "streamable_http"}})`, call `await mcp_client.get_tools()`, and merge the result with local tools in the agent's `tools` list.

## Key Concepts
- **MCP server**: a process that exposes a collection of tools (and optionally prompts/resources) through the MCP protocol, backed by some underlying service or data source.
- **MCP client**: the component, embedded in the host application, that connects to an MCP server, discovers its tools, and issues calls to them.
- **MCP host**: the agent or application process that uses one or more MCP clients to connect to MCP servers; in the chapter's test script this is a minimal standalone script.
- **FastMCP**: the official-adjacent Python SDK (`fastmcp` package) for building MCP servers and clients; FastMCP 2 adds easier deployment/composition, security features, dynamic tool rewriting, and testing utilities over FastMCP 1.
- **Streamable HTTP transport**: the transport used for remote MCP servers in production (and, per the chapter, by default even for local development); contrasted with STDIO, used for local/dev servers or local-resource access.
- **STDIO transport**: standard input/output transport for MCP servers, typically local-only, simpler for development.
- **MCP Inspector**: a Node.js-based web UI tool (`npx @modelcontextprotocol/inspector`) that connects to any MCP server to list and interactively run its tools, without writing client code.
- **CallToolResult**: the standardized wrapper returned by an MCP tool call, containing `content`, `structured_content`, `data`, and `is_error`, following the same tool-calling protocol as local tools.
- **MCP server portal**: a public directory of ready-made MCP servers (e.g., the official `modelcontextprotocol/servers` repo, mcp.so, smithery.ai, mcpservers.org).

## Mental Models
- **MCP as REST-for-tools**: the host/client/server split mirrors REST APIs or WebSockets exposing endpoints for consumption — the payoff is that adding or swapping a context source becomes a configuration change, not a new integration to write and maintain.
- **Integration work moves to the source**: instead of every agent team wrapping the same public APIs, the provider of the service builds the MCP server once; agents "subscribe" to it. The unit of reuse shifts from "my wrapper code" to "the provider's server."
- **Local tools and MCP tools are interchangeable at the agent boundary**: once a client has retrieved an MCP server's tools, they slot into the same `tools` list and calling convention as locally defined tools — a well-architected agent needs little to no logic change to add remote MCP capability.
- **Validate before you integrate**: MCP Inspector exists as a protocol-level sanity check (connect, list tools, run tool) decoupled from any agent code, so failures are isolated to "is my server correct" before "is my agent wiring correct."

## Anti-patterns
- **Wrapping every integration as a bespoke tool**: the pre-MCP norm — every team writes and maintains similar wrapper code for the same public APIs/services, duplicating effort across the ecosystem instead of consuming a shared, standardized server.
- **Implementing the MCP protocol from scratch**: not recommended even though the spec is open and technology-agnostic; doing so duplicates effort already solved by mature official SDKs (FastMCP 2 for Python, plus JS/Java/Kotlin/C# SDKs).
- **Skipping MCP Inspector validation**: going straight from server implementation to agent integration removes the fastest, code-free way to confirm the server and its tools work before adding agent-side complexity on top.
- **Building a custom MCP server for a service that already has an official one**: check GitHub, Slack, Google Drive, and similar vendor-provided servers before hand-rolling an integration.

## Code Examples
```python
import os
import json
from typing import Dict
from fastmcp import FastMCP
from dotenv import load_dotenv
from aiohttp import ClientSession

load_dotenv()
mcp = FastMCP("mcp-accuweather")

@mcp.tool(description="""Get weather conditions for a location.""")
async def get_weather_conditions(location: str) -> Dict:
    """Get weather conditions for a location."""
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    base_url = "http://dataservice.accuweather.com"
    async with ClientSession() as session:
        location_search_url = f"{base_url}/locations/v1/cities/search"
        params = {"apikey": api_key, "q": location}
        async with session.get(location_search_url, params=params) as response:
            locations = await response.json()
            if response.status != 200:
                raise Exception(f"Error fetching location data: {response.status}, {locations}")
            if not locations or len(locations) == 0:
                raise Exception("Location not found")
            location_key = locations[0]["Key"]
        current_conditions_url = f"{base_url}/currentconditions/v1/{location_key}"
        params = {"apikey": api_key, "details": "true"}
        async with session.get(current_conditions_url, params=params) as response:
            current_conditions = await response.json()
            if current_conditions and len(current_conditions) > 0:
                current = current_conditions[0]
                current_data = {
                    "temperature": {
                        "value": current["Temperature"]["Metric"]["Value"],
                        "unit": current["Temperature"]["Metric"]["Unit"]
                    },
                    "weather_text": current["WeatherText"],
                    "relative_humidity": current.get("RelativeHumidity"),
                    "precipitation": current.get("HasPrecipitation", False),
                    "observation_time": current["LocalObservationDateTime"]
                }
            else:
                current_data = "No current conditions available"
        return {
            "location": locations[0]["LocalizedName"],
            "location_key": location_key,
            "country": locations[0]["Country"]["LocalizedName"],
            "current_conditions": current_data,
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8020, path="/accu-mcp-server")
```
- **What it demonstrates**: a complete FastMCP 2 server exposing a single async `@mcp.tool`-decorated function backed by a real REST API (AccuWeather), served over Streamable HTTP.

```python
async def get_accuweather_tools():
    mcp_client = MultiServerMCPClient({
        "accuweather": {
            "url": "http://127.0.0.1:8020/accu-mcp-server",
            "transport": "streamable_http"
        }
    })
    return await mcp_client.get_tools()

async def main():
    accuweather_tools = await get_accuweather_tools()
    tools = [search_travel_info, *accuweather_tools]
    llm_model = ChatOpenAI(model="gpt-5-mini", use_responses_api=True)
    travel_info_agent = create_react_agent(
        model=llm_model,
        tools=tools,
        state_schema=AgentState,
        name="travel_info_agent",
        prompt="""You are a helpful assistant that can search travel information and
        get the weather forecast. Only use the tools to find the information you need
        (including town names).""",
    )
    await chat_loop(travel_info_agent)

if __name__ == "__main__":
    asyncio.run(main())
```
- **What it demonstrates**: consuming a remote MCP server from a LangGraph agent via `MultiServerMCPClient`, merging its tools with a local tool (`search_travel_info`) in one `create_react_agent` call.

## Reference Tables
| Portal | Description |
|---|---|
| github.com/modelcontextprotocol/servers | Anthropic's official MCP portal, listing official and community servers |
| mcp.so | Community-driven directory, 16,000+ servers |
| smithery.ai | 5,000+ tools, mostly MCP-compliant |
| mcpservers.org | ~1,500 servers |

| Approach to consuming MCP servers | When it applies |
|---|---|
| OpenAI Responses API native MCP support | Public MCP servers; OpenAI discovers and executes tools for you, no client code |
| FastMCP client | Direct SDK-level connect/authenticate/consume, any host application |
| LangChain/LangGraph `MultiServerMCPClient` | LangGraph/LangChain agents aggregating tools from multiple MCP servers via config |

## Worked Example
Building, testing, and integrating the AccuWeather weather MCP server end to end:

1. **Get credentials**: register at the AccuWeather developer portal, copy the Default App API key, and store it as `ACCUWEATHER_API_KEY=<key>` in `.env`.
2. **Implement the server** (`mcp/accuweather_mcp.py`): `load_dotenv()`, instantiate `mcp = FastMCP("mcp-accuweather")`, define `get_weather_conditions(location: str) -> Dict` decorated with `@mcp.tool(...)`. The tool logic: (a) call AccuWeather's `locations/v1/cities/search` endpoint to resolve `location` to a `location_key`; (b) call `currentconditions/v1/{location_key}` with `details=true`; (c) shape the response into a `current_data` dict (temperature/unit, weather text, humidity, precipitation flag, observation time); (d) return a dict combining location metadata and `current_conditions`. Run it with `mcp.run(transport="streamable-http", host="127.0.0.1", port=8020, path="/accu-mcp-server")`; launching it prints Uvicorn startup logs ending in `Uvicorn running on http://0.0.0.0:8020`.
3. **Validate with MCP Inspector**: install Node.js, run `npx @modelcontextprotocol/inspector` (confirms install, then opens the browser UI and prints a proxy URL/session token). In the UI, set Transport Type = Streamable HTTP, URL = `http://127.0.0.1:8020/accu-mcp-server`, Connection Type = Via Proxy, disable Authentication, click Connect — a green "Connected" status confirms the server is reachable. Under the Tools tab, click "List Tools" to see `get_weather_conditions`, select it, enter a location (e.g., "Penzance, UK") and click "Run Tool" to see live weather data returned — all without writing client code.
4. **Consume it from a test MCP host** (`mcp/test_accuweather_mcp.py`): build a `StreamableHttpTransport(url="http://localhost:8020/accu-mcp-server")`, wrap it in `Client(transport)`, and inside `async def main()`: open `async with client:`, print `client.is_connected()`, call `await client.list_tools()`, check `get_weather_conditions` is present, call `await client.call_tool("get_weather_conditions", {"location": "Penzance, UK"})`, and print the `CallToolResult` (content/structured_content/data/is_error). Run with `python test_accuweather_mcp.py`; the result confirms the tool responds with real AccuWeather data wrapped in the standard tool-calling result format.
5. **Integrate into the travel agent** (upgrading `main_03_01.py` into `main_07_01.py`): remove the old `weather_forecast` mock tool and `WeatherForecastService`; add the async `get_accuweather_tools()` function (shown in Code Examples) that instantiates `MultiServerMCPClient` pointed at the running server and returns `await mcp_client.get_tools()`.
6. **Make the chat loop async**: `chat_loop(agent)` becomes `async def`, reading input, building `state = {"messages": [HumanMessage(content=user_input)]}`, calling `await agent.ainvoke(state)`, and printing `result["messages"][-1].content`.
7. **Wire it together in `main()`**: `accuweather_tools = await get_accuweather_tools()`; `tools = [search_travel_info, *accuweather_tools]`; build `ChatOpenAI(model="gpt-5-mini", use_responses_api=True)`; call `create_react_agent(model=llm_model, tools=tools, state_schema=AgentState, name="travel_info_agent", prompt="...")`; `await chat_loop(travel_info_agent)`; run everything via `asyncio.run(main())`.
8. **Verify**: a debug breakpoint at LLM instantiation shows both `StructuredTool(name='search_travel_info', ...)` and `Tool(name='get_weather_conditions', ...)` in the merged tools list. Asking "What's the weather in Penzance?" now returns live AccuWeather data (e.g., "light rain with a temperature of 17°C") instead of the old mock response ("windy... 21°C"). More complex queries (e.g., "Suggest two beach Cornwall towns with nice weather") show the agent combining the local `search_travel_info` tool with live weather calls across multiple towns to reason about an answer.

## Key Takeaways
1. MCP standardizes tool exposure via a host/client/server architecture over JSON-RPC, so agents discover and call remote tools exactly like local ones.
2. Check for an existing official or community MCP server (via portals like the official GitHub repo, mcp.so, smithery.ai, mcpservers.org) before building a custom integration.
3. Use an official SDK (FastMCP 2 for Python) rather than implementing the protocol yourself — decorator-based `@mcp.tool` definitions auto-generate schemas from type hints.
4. Validate a new MCP server with MCP Inspector (connect, list tools, run tool) before wiring it into any agent code — it isolates server bugs from integration bugs.
5. `MultiServerMCPClient.get_tools()` converts MCP tools into native LangChain/LangGraph tools, so they can be concatenated directly with local tools in one agent's `tools` list.
6. Moving an agent to MCP tools generally requires making the surrounding chat loop and `main()` async (`ainvoke`, `asyncio.run`), since tool calls now cross the network.
7. A single agent can consume multiple MCP servers at once, treating them as one unified tool ecosystem, and mix them freely with local, non-MCP tools.

## Connects To
- **Ch 11**: the travel information agent and its local mock `weather_forecast` tool, which this chapter replaces with a live MCP-powered tool.
- **Ch 12**: multi-agent/multi-tool agent patterns that MCP tools slot into without architectural changes.
- **Anthropic's "Introducing the Model Context Protocol"**: the original announcement and specification (modelcontextprotocol.io) underlying the protocol covered in this chapter.
