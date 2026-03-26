import os
import sys
import json
import asyncio
import logging
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# 1. Setup Logging & Version
# Phase 1.3: Unified Hub now prioritizes 'sample_input.json' from each cell folder
# for the UI auto-fill feature, ensuring tool-specific test data is always visible.
VERSION = f"v1.3.0 (Stability Patch) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("US StockMCPHub")
logger.info(f"=== Starting Unified US Stock MCP Hub {VERSION} ===")

# 2. Initialize FastMCP
mcp = FastMCP("US Stock Cells Hub", dependencies=["urllib3", "requests"])

# 3. Path Configuration (Relative to project root now)
# mcp/server.py -> parent -> parent
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CELLS_DIR = PROJECT_ROOT / "cells"

# 4. Resilience Settings
CELL_TIMEOUT = 30.0
BLACKLISTED_CELLS = set()
_TOOL_LIST_CACHE: Optional[List[str]] = None
_TOOL_PATH_MAP: Dict[str, Path] = {}
_METADATA_CACHE: Dict[str, Dict[str, Any]] = {}

def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists(): return None
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else None
    except Exception: return None

def _resolve_cell_dir(marker_path: Path) -> Path:
    if marker_path.name == "option_schema.json": return marker_path.parent
    if marker_path.name == "intro.json": return marker_path.parent.parent if marker_path.parent.name == "intro" else marker_path.parent
    if marker_path.name == "worker.py": return marker_path.parent.parent if marker_path.parent.name == "kernel_parts" else marker_path.parent
    return marker_path.parent

def _find_worker_file(cell_dir: Path) -> Optional[Path]:
    f1 = cell_dir / "worker.py"
    if f1.exists(): return f1
    f2 = cell_dir / "kernel_parts" / "worker.py"
    if f2.exists(): return f2
    return None

def _build_cell_description(cell_dir: Path, cell_name: str) -> str:
    s = _load_json_file(cell_dir / "option_schema.json")
    if s and s.get("description"): return s["description"]
    i = _load_json_file(cell_dir / "intro" / "intro.json") or _load_json_file(cell_dir / "intro.json")
    if i: return i.get("description") or i.get("summary_1line") or f"Tool: {cell_name}"
    return f"Tool: {cell_name}"

def _build_cell_metadata(cell_dir: Path, cell_name: str) -> Dict[str, Any]:
    """Builds metadata for a cell, prioritizing local 'sample_input.json' and 'option_schema.json'."""
    # 1. Base Defaults
    default_sample = {"symbol": "NVDA", "symbols": "NVDA"}
    meta = {
        "description": _build_cell_description(cell_dir, cell_name), 
        "sample_input": default_sample.copy()
    }
    
    # 2. Priority 1: sample_input.json (Legacy but explicit)
    sample_file = cell_dir / "sample_input.json"
    if sample_file.exists():
        shared_sample = _load_json_file(sample_file)
        if shared_sample:
            # Check for nested message/params structure used in some cells
            if "message" in shared_sample and isinstance(shared_sample["message"], dict):
                p = shared_sample["message"].get("params", shared_sample["message"])
                if isinstance(p, dict): meta["sample_input"].update(p)
            else:
                meta["sample_input"].update(shared_sample)

    # 3. Priority 2: option_schema.json (Standard)
    s = _load_json_file(cell_dir / "option_schema.json")
    if s:
        if s.get("sample_input"):
            meta["sample_input"].update(s["sample_input"])
        elif s.get("input_schema"):
            props = s["input_schema"].get("properties", {})
            defaults = {k: v["default"] for k, v in props.items() if isinstance(v, dict) and "default" in v}
            if defaults: meta["sample_input"].update(defaults)
            
    return meta

def _build_tool_index() -> None:
    """
    Scans the 'cells/' directory to discover available tools and build their metadata cache.
    This function should be called before any tool registration or metadata retrieval.
    """
    global _TOOL_LIST_CACHE, _TOOL_PATH_MAP, _METADATA_CACHE
    if _TOOL_LIST_CACHE is not None: return

    _TOOL_PATH_MAP = {}
    _METADATA_CACHE = {}
    if not CELLS_DIR.exists():
        logger.error(f"Cells directory not found: {CELLS_DIR}")
        _TOOL_LIST_CACHE = []
        return

    discovered_names = set()

    def consider_cell(cell_dir: Path):
        """Helper to register a cell folder as a tool."""
        name = cell_dir.name
        if name in BLACKLISTED_CELLS or name in discovered_names:
            return
        
        discovered_names.add(name)
        _TOOL_PATH_MAP[name] = cell_dir
        
        # FIX: Correctly populate metadata using the dedicated helper
        # This ensures 'sample_input' is correctly cached for UI auto-fill.
        _METADATA_CACHE[name] = _build_cell_metadata(cell_dir, name)
        logger.info(f"  + Registered: {name}")

    logger.info(f"Scanning ecosystem in: {CELLS_DIR}")
    for dp, _, fns in os.walk(CELLS_DIR):
        current = Path(dp)
        # Search for marker files (option_schema.json or worker.py)
        if "option_schema.json" in fns:
            consider_cell(current)
        elif "worker.py" in fns:
            # Handle standard worker structure or nested kernel_parts structure
            consider_cell(current.parent if current.name == "kernel_parts" else current)

    _TOOL_LIST_CACHE = sorted(list(discovered_names))
    logger.info(f"Indexing Complete: Found {len(_TOOL_LIST_CACHE)} tools.")

def coerce_params(tool_name: str, raw_input: Any) -> Dict[str, Any]:
    """
    Intelligently normalizes input parameters for legacy cells.
    Handles List -> Comma-Separated String and Singular/Plural key mapping.
    Also provides a fallback to 'sample_input' from metadata if input is empty.
    """
    params = {}
    logger.info(f"[COERCE] Tool: {tool_name} | Raw Input: {raw_input}")
    
    # 1. Direct Input Extraction
    if isinstance(raw_input, dict):
        # A. Handle 'kwargs' wrapper (often sent by AI models/MCP clients)
        kw = raw_input.get("kwargs")
        if kw:
            if isinstance(kw, str) and kw.strip().startswith("{"):
                try: 
                    kw_parsed = json.loads(kw)
                    if isinstance(kw_parsed, dict): params.update(kw_parsed)
                except: pass
            elif isinstance(kw, dict):
                params.update(kw)

        # B. Handle 'message' -> 'params' nesting
        if "message" in raw_input and isinstance(raw_input["message"], dict):
            m = raw_input["message"]
            p = m.get("params", m) if isinstance(m.get("params"), dict) else m
            if isinstance(p, dict): params.update(p)
        
        # C. General 'params' key
        elif "params" in raw_input and isinstance(raw_input["params"], dict):
            params.update(raw_input["params"])
        
        # D. Direct merge (if no wrapper or after processing wrappers)
        if not params:
            params = raw_input.copy()
            
    elif isinstance(raw_input, str):
        t = raw_input.strip()
        if t.startswith("{") and t.endswith("}"):
            try:
                parsed = json.loads(t)
                if isinstance(parsed, dict): return coerce_params(tool_name, parsed)
            except: pass
        # Fallback for raw string (e.g., "NVDA")
        params = {"query": t} if any(k in (tool_name or "").lower() for k in ("news", "query")) else {"symbol": t}
    else:
        # Final fallback
        params = {"symbol": str(raw_input)} if raw_input else {}

    # 2. Type Normalization (List -> Comma-Separated String)
    def normalize_value(val):
        if isinstance(val, list):
            return ",".join([str(x).upper() for x in val])
        if isinstance(val, str):
            return val.strip().upper()
        return str(val)

    # 3. Key Normalization & Symbol Extraction
    raw_sym = (
        params.get("symbols") or 
        params.get("symbol") or 
        params.get("ticker") or 
        params.get("tickers") or
        params.get("query")
    )
    
    # 4. Fallback to Sample Input if totally empty or missing symbol
    if not raw_sym:
        # Standardize lookup key (lowercase)
        lookup_key = tool_name.lower().strip()
        meta = _METADATA_CACHE.get(lookup_key)
        
        if meta and "sample_input" in meta:
            sample = meta["sample_input"]
            logger.info(f"[COERCE] Using sample_input fallback for {lookup_key}: {sample}")
            if isinstance(sample, dict):
                # Only update keys that are missing to preserve other explicit inputs (like feed)
                for k, v in sample.items():
                    if k not in params: params[k] = v
                raw_sym = (params.get("symbols") or params.get("symbol") or params.get("ticker") or params.get("query"))
            else:
                raw_sym = sample

    if raw_sym:
        str_val = normalize_value(raw_sym)
        singular_val = str_val.split(",")[0] if str_val else ""
        
        # Populate common aliases
        for k in ["symbol", "ticker", "query"]:
            params[k] = singular_val
        for k in ["symbols", "tickers"]:
            params[k] = str_val

    logger.info(f"[COERCE] Result: {params}")
    return params

async def execute_cell_worker(cell_name: str, params_input: Any) -> Dict[str, Any]:
    params = coerce_params(cell_name, params_input)
    # Special defaults
    if "historical_bars" in cell_name:
        if "timeframe" not in params: params["timeframe"] = "1Day"
        if "start" not in params: params["start"] = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")
    
    _build_tool_index()
    cell_path = _TOOL_PATH_MAP.get(cell_name)
    if not cell_path: return {"ok": False, "error": f"Tool '{cell_name}' not found."}

    wf = _find_worker_file(cell_path)
    if not wf: return {"ok": False, "error": "Worker not found."}

    payload = {"message": {"params": params}, "lim_aplc": {"caller": "US StockMCPHub", "mode": "mcp"}}

    try:
        module_name = f"cells.{cell_name}.worker"
        spec = importlib.util.spec_from_file_location(module_name, str(wf))
        module = importlib.util.module_from_spec(spec)
        
        sys.path.insert(0, str(cell_path))
        if (cell_path / "kernel_parts").exists(): sys.path.insert(0, str(cell_path / "kernel_parts"))

        def run_sync():
            spec.loader.exec_module(module)
            if hasattr(module, "worker_main"): return module.worker_main(payload)
            if hasattr(module, "main"): return module.main()
            raise AttributeError("Entry point (worker_main/main) missing.")
            
        return await asyncio.wait_for(asyncio.to_thread(run_sync), timeout=CELL_TIMEOUT)
    except Exception as e:
        logger.exception(f"Tool {cell_name} Error: {e}")
        return {"ok": False, "error": str(e)}
    finally:
        # Simple cleanup (simplified for this plan)
        pass

def get_all_tool_names():
    _build_tool_index()
    return _TOOL_LIST_CACHE or []

def get_tool_metadata(name: str):
    _build_tool_index()
    return _METADATA_CACHE.get(name, {"description": "N/A"})

# 5. Diagnostic Tools
@mcp.tool()
async def get_hub_info():
    """Returns information about the running MCP Hub instance (Version, Timestamp)."""
    return json.dumps({
        "status": "Running",
        "version": VERSION,
        "indexed_tools": len(get_all_tool_names()),
        "cells_dir": str(CELLS_DIR),
        "note": "If you just updated server.py, please RESTART your MCP launcher/IDE to apply changes."
    }, indent=2)

@mcp.tool()
async def debug_coerce(tool_name: str = "test", **kwargs):
    """Echoes back how the hub coerces your input. Use this to test parameter mapping."""
    result = coerce_params(tool_name, kwargs)
    return json.dumps({
        "raw_input": kwargs,
        "coerced_result": result,
        "explanation": "This shows how 'symbol' vs 'symbols' and List vs String are being handled."
    }, indent=2)

def register_all_tools():
    _build_tool_index()
    # Note: Diagnostic tools are already registered via @mcp.tool()
    for name in _TOOL_LIST_CACHE or []:
        desc = _METADATA_CACHE.get(name, {}).get("description", f"Execute {name}")
        def create_func(n, d):
            async def func(**kwargs): 
                # Unified Execution Entry Point
                res = await execute_cell_worker(n, kwargs)
                return json.dumps(res, ensure_ascii=False, indent=2)
            func.__name__ = n
            func.__doc__ = d
            return func
        mcp.tool()(create_func(name, desc))

if __name__ == "__main__":
    # Default to stdio for CLI use
    register_all_tools()
    mcp.run()

