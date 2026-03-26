# ?’Ž US Stock MCP (Unified Hub) Connection Guide

This document describes how to connect and use the US Stock MCP stack in various environments (IDE, Terminal, Web).

---

## 1. ?“‚ Project Structure
- **Core Server**: `mcp_hub/server.py` (The core server where logic and metadata for all tools are integrated)
- **Launchers**:
  - `mcp_hub/launch_stdio.py`: Standard Input/Output (stdio) method (For IDEs)
  - `mcp_hub/launch_sse.py`: HTTP/SSE method (For Web and Remote access)
  - `ui/Web_App_Launcher.py`: Dedicated Web Browser UI
  - `ui/Desktop_Launcher.py`: Dedicated Desktop App UI

---

## 2. ?”Œ Connection Methods

### A. Local (stdio) Method (Highly Recommended)
Use this when connecting directly from IDEs or chatbot programs. Forward slashes (`/`) are used to improve path compatibility.

- **Command**: Copy and use the line below as is.
```powershell
C:/program_files/.venv/Scripts/python.exe C:/program_files/server/cells_apply/US Stock_mcp_v1/mcp_hub/launch_stdio.py
```

### B. HTTP/SSE Method (Port 8011)
Use this when accessing the MCP server via standard HTTP protocol. Port **8011** is fixed to avoid conflicts with other projects.

1. Run server: `python mcp_hub/launch_sse.py`
2. Endpoint: `http://localhost:8011/sse`

### C. Dedicated UI Execution (For Monitoring)
- **Browser Only**: `python ui/Web_App_Launcher.py` (Port 6991)
- **Desktop Only**: `python ui/Desktop_Launcher.py` (Independent window app)

---

## ?› ï¸?Key Features
- **Fixed Port 8011**: Stability is enhanced by forcing the allocation of port 8011 through `uvicorn`.
- **Background Indexing**: All launchers (UI, SSE) preload tools in the background upon startup, ensuring fast access.
- **Custom Test Data**: Placing a `sample_input.json` file in each cell (tool) folder automatically fills in the default data in the UI (Port 6991).

---

## ?”’ Security and Configuration (Private Keys)
US Stock API keys are automatically searched in the following paths:
1. `C:\program_files\grace\config_grace_apis.json` (Central management path)
2. `[ProjectRoot]\config\config_grace_apis.json` (Local path)

*Created by Antigravity (Advanced Agentic Coding Team)*

