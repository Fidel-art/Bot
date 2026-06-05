"""
MT5 Bridge Server - REST API wrapper for MetaTrader 5
Runs on the Windows host. Exposes MT5 operations to Docker containers
via HTTP. Accessed by containers at http://host.docker.internal:8765
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import threading
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import MetaTrader5 as mt5

app = FastAPI(title="MT5 Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Per-thread MT5 initialization tracking
_local = threading.local()


def _ensure_mt5():
    """Ensure MT5 is initialized on the current thread."""
    if not getattr(_local, 'initialized', False):
        for attempt in range(3):
            if mt5.initialize(timeout=10000):
                _local.initialized = True
                return True
            time.sleep(1)
        return False
    return True


class OrderRequest(BaseModel):
    action: int
    symbol: str
    volume: float
    price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    deviation: Optional[int] = None
    magic: Optional[int] = None
    comment: Optional[str] = None
    type_time: Optional[int] = None
    type_filling: Optional[int] = None
    type: Optional[int] = None


class LoginRequest(BaseModel):
    login: int
    password: str
    server: str


class InitializeRequest(BaseModel):
    path: Optional[str] = None
    timeout: Optional[int] = None


class SymbolSelectRequest(BaseModel):
    symbol: str
    enable: bool = True


def _nt_to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, '_asdict'):
        return {k: _nt_to_dict(v) for k, v in obj._asdict().items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (list, tuple)):
        return [_nt_to_dict(v) for v in obj]
    # Handle numpy structured arrays (returned by copy_rates_*)
    if hasattr(obj, 'dtype') and hasattr(obj, 'tolist'):
        names = obj.dtype.names
        if names:
            # Structured array with named fields → list of dicts
            return [{name: _nt_to_dict(row[name]) for name in names} for row in obj]
        return _nt_to_dict(obj.tolist())
    return obj


@app.post("/initialize")
def handle_initialize(req: InitializeRequest):
    _ensure_mt5()
    return {"result": True, "last_error": None}


@app.post("/shutdown")
def handle_shutdown():
    if getattr(_local, 'initialized', False):
        mt5.shutdown()
        _local.initialized = False
    return {"result": True}


@app.post("/login")
def handle_login(req: LoginRequest):
    _ensure_mt5()
    result = mt5.login(req.login, req.password, req.server)
    return {"result": result, "last_error": mt5.last_error() if not result else None}


@app.get("/last_error")
def handle_last_error():
    code, desc = mt5.last_error()
    return {"code": code, "description": desc}


@app.get("/account_info")
def handle_account_info():
    _ensure_mt5()
    return _nt_to_dict(mt5.account_info())


@app.get("/terminal_info")
def handle_terminal_info():
    _ensure_mt5()
    return _nt_to_dict(mt5.terminal_info())


@app.get("/symbol_info/{symbol}")
def handle_symbol_info(symbol: str):
    _ensure_mt5()
    return _nt_to_dict(mt5.symbol_info(symbol))


@app.post("/symbol_select")
def handle_symbol_select(req: SymbolSelectRequest):
    _ensure_mt5()
    result = mt5.symbol_select(req.symbol, req.enable)
    return {"result": result, "last_error": mt5.last_error() if not result else None}


@app.get("/symbol_info_tick/{symbol}")
def handle_symbol_info_tick(symbol: str):
    _ensure_mt5()
    return _nt_to_dict(mt5.symbol_info_tick(symbol))


@app.get("/copy_rates_from_pos")
def handle_copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int = 0, count: int = 100):
    _ensure_mt5()
    mt5.symbol_select(symbol, True)
    rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
    return _nt_to_dict(rates) if rates is not None else []


@app.get("/positions_get")
def handle_positions_get(symbol: Optional[str] = None, ticket: Optional[int] = None):
    _ensure_mt5()
    kwargs = {}
    if symbol:
        kwargs["symbol"] = symbol
    if ticket is not None:
        kwargs["ticket"] = ticket
    positions = mt5.positions_get(**kwargs)
    return _nt_to_dict(positions) if positions is not None else []


@app.get("/history_deals_get")
def handle_history_deals_get(from_date: Optional[str] = None, to_date: Optional[str] = None):
    _ensure_mt5()
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    deals = mt5.history_deals_get(from_dt, to_dt)
    return _nt_to_dict(deals) if deals is not None else []


@app.post("/order_send")
def handle_order_send(order: OrderRequest):
    _ensure_mt5()
    request = {
        "action": order.action,
        "symbol": order.symbol,
        "volume": order.volume,
        "price": order.price,
    }
    if order.sl is not None:
        request["sl"] = order.sl
    if order.tp is not None:
        request["tp"] = order.tp
    if order.deviation is not None:
        request["deviation"] = order.deviation
    if order.magic is not None:
        request["magic"] = order.magic
    if order.comment:
        request["comment"] = order.comment
    if order.type_time is not None:
        request["type_time"] = order.type_time
    if order.type_filling is not None:
        request["type_filling"] = order.type_filling
    if order.type is not None:
        request["type"] = order.type
    result = mt5.order_send(request)
    return _nt_to_dict(result)


@app.get("/health")
def handle_health():
    ok = _ensure_mt5()
    if ok:
        account = mt5.account_info()
        return {
            "status": "ok",
            "mt5_initialized": True,
            "connected": account is not None,
            "account": account.login if account else None,
            "server": account.server if account else None,
            "balance": float(account.balance) if account else None,
            "equity": float(account.equity) if account else None,
        }
    code, desc = mt5.last_error()
    return {"status": "error", "mt5_initialized": False, "error_code": code, "error_message": desc}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MT5 Bridge Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    print(f"Starting MT5 Bridge on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
