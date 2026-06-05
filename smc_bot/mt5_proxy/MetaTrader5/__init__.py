"""
MetaTrader5 Proxy — routes all calls to the MT5 Bridge REST API on the Windows host.
Used inside Docker containers where the real MetaTrader5 package cannot work.
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from types import SimpleNamespace

BRIDGE_URL = os.environ.get("MT5_BRIDGE_URL", "http://host.docker.internal:8765")

# ── Constants ──────────────────────────────────────────────────────────────

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

TRADE_ACTION_DEAL = 1
TRADE_ACTION_SLTP = 3

ORDER_TIME_GTC = 0
ORDER_TIME_DAY = 1
ORDER_TIME_SPECIFIED = 2
ORDER_TIME_SPECIFIED_DAY = 3

ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2

TRADE_RETCODE_DONE = 10009

TIMEFRAME_M1 = 1
TIMEFRAME_M2 = 2
TIMEFRAME_M3 = 3
TIMEFRAME_M4 = 4
TIMEFRAME_M5 = 5
TIMEFRAME_M6 = 6
TIMEFRAME_M10 = 10
TIMEFRAME_M12 = 12
TIMEFRAME_M15 = 15
TIMEFRAME_M20 = 20
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 16385
TIMEFRAME_H2 = 16386
TIMEFRAME_H3 = 16387
TIMEFRAME_H4 = 16388
TIMEFRAME_H6 = 16390
TIMEFRAME_H8 = 16392
TIMEFRAME_H12 = 16396
TIMEFRAME_D1 = 16408
TIMEFRAME_W1 = 32769
TIMEFRAME_MN1 = 49153

DEAL_ENTRY_IN = 0
DEAL_ENTRY_OUT = 1
DEAL_ENTRY_OUT_BY = 2
DEAL_ENTRY_INOUT = 3

DEAL_TYPE_BUY = 0
DEAL_TYPE_SELL = 1

COPY_TICKS_ALL = -1
COPY_TICKS_INFO = 1
COPY_TICKS_TRADE = 2

# ── HTTP Client ────────────────────────────────────────────────────────────


class _BridgeClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, data=None):
        url = f"{self._base_url}{path}"
        params = None
        body = None

        if data is not None and method == "GET":
            params = urllib.parse.urlencode(
                {k: v for k, v in data.items() if v is not None}
            )
        elif data is not None:
            body = json.dumps(data).encode()
        elif method == "POST":
            body = b"{}"

        if params:
            url = f"{url}?{params}"

        req = urllib.request.Request(url, method=method, data=body)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()
            return {"_error": True, "code": e.code, "message": body_text}
        except urllib.error.URLError as e:
            return {"_error": True, "code": 0, "message": str(e.reason)}
        except OSError as e:
            return {"_error": True, "code": 0, "message": str(e)}

    def _to_sn(self, obj):
        if isinstance(obj, dict):
            return SimpleNamespace(
                **{k: self._to_sn(v) for k, v in obj.items()}
            )
        if isinstance(obj, list):
            return [self._to_sn(v) for v in obj]
        return obj


_client = _BridgeClient(BRIDGE_URL)


# ── MT5 API Functions ─────────────────────────────────────────────────────


def initialize(path=None, timeout=None):
    """Initialize connection to MT5 terminal via bridge."""
    payload = {}
    if path is not None:
        payload["path"] = path
    if timeout is not None:
        payload["timeout"] = timeout
    result = _client._request("POST", "/initialize", payload)
    if result.get("_error"):
        return False
    return result.get("result", False)


def shutdown():
    """Shutdown MT5 connection."""
    _client._request("POST", "/shutdown")
    return True


def login(login_id, password, server):
    """Login to trading account."""
    result = _client._request(
        "POST",
        "/login",
        {"login": int(login_id), "password": str(password), "server": str(server)},
    )
    if result.get("_error"):
        return False
    if not result.get("result", False):
        return False
    return True


def last_error():
    """Return last error code and description."""
    result = _client._request("GET", "/last_error")
    return (result.get("code", 0), result.get("description", ""))


def account_info():
    """Get current account info."""
    result = _client._request("GET", "/account_info")
    if result and not result.get("_error"):
        return _client._to_sn(result)
    return None


def terminal_info():
    """Get terminal info."""
    result = _client._request("GET", "/terminal_info")
    if result and not result.get("_error"):
        return _client._to_sn(result)
    return None


def symbol_info(symbol):
    """Get symbol info."""
    result = _client._request("GET", f"/symbol_info/{urllib.parse.quote(symbol)}")
    if result and not result.get("_error") and result.get("name"):
        return _client._to_sn(result)
    return None


def symbol_select(symbol, enable=True):
    """Select symbol in MarketWatch."""
    result = _client._request(
        "POST", "/symbol_select", {"symbol": symbol, "enable": enable}
    )
    if result.get("_error"):
        return False
    return result.get("result", False)


def symbol_info_tick(symbol):
    """Get current tick for symbol."""
    result = _client._request(
        "GET", f"/symbol_info_tick/{urllib.parse.quote(symbol)}"
    )
    if result and not result.get("_error") and result.get("bid") is not None:
        return _client._to_sn(result)
    return None


def copy_rates_from_pos(symbol, timeframe, start_pos=0, count=100):
    """Get historical rates. Returns list of dicts (pandas-compatible)."""
    result = _client._request(
        "GET",
        "/copy_rates_from_pos",
        {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_pos": int(start_pos),
            "count": int(count),
        },
    )
    if isinstance(result, list):
        return result
    return []


def positions_get(symbol=None, ticket=None):
    """Get open positions."""
    params = {}
    if symbol is not None:
        params["symbol"] = symbol
    if ticket is not None:
        params["ticket"] = int(ticket)
    result = _client._request("GET", "/positions_get", params)
    if isinstance(result, list):
        return _client._to_sn(result)
    return []


def history_deals_get(from_date=None, to_date=None):
    """Get deal history."""
    params = {}
    if from_date is not None:
        if isinstance(from_date, datetime):
            params["from_date"] = from_date.isoformat()
        else:
            params["from_date"] = str(from_date)
    if to_date is not None:
        if isinstance(to_date, datetime):
            params["to_date"] = to_date.isoformat()
        else:
            params["to_date"] = str(to_date)
    result = _client._request("GET", "/history_deals_get", params)
    if isinstance(result, list):
        return _client._to_sn(result)
    return []


def order_send(request):
    """Send order/trade request."""
    if not isinstance(request, dict):
        if hasattr(request, "_asdict"):
            request = request._asdict()
        else:
            request = dict(vars(request))
    result = _client._request("POST", "/order_send", request)
    if result and not result.get("_error"):
        return _client._to_sn(result)
    return None
