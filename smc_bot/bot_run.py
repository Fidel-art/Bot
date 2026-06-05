"""
Bot Runner — Docker entry point for the trading bot container.
Watches for config files saved by the dashboard, then launches main.py.
All MT5 operations are routed via the MT5 Bridge on the Windows host.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

CONFIG_DIR = Path("config/trader_configs")
POLL_SECONDS = 5


def _current_trader_config() -> Path | None:
    if not CONFIG_DIR.is_dir():
        return None
    configs = sorted(CONFIG_DIR.glob("*_config.json"))
    return configs[-1] if configs else None


def _read_trader_id(config_path: Path) -> str:
    return config_path.stem.replace("_config", "")


def _start_bot(config_path: Path) -> bool:
    trader_id = _read_trader_id(config_path)
    print(f"[{time.strftime('%H:%M:%S')}] Launching bot for trader: {trader_id}")

    env = os.environ.copy()
    env["BOT_NON_INTERACTIVE"] = "1"
    env["BOT_AUTO_START"] = "1"
    env["BOT_TRADER_ID"] = trader_id

    result = subprocess.run(
        [sys.executable, "main.py"],
        env=env,
        cwd=Path(__file__).parent,
    )
    print(f"[{time.strftime('%H:%M:%S')}] Bot exited with code {result.returncode}")
    return result.returncode == 0


def main():
    print("=" * 55)
    print("  SMC Trading Bot — Docker Runner")
    print("  Waiting for dashboard configuration...")
    print("=" * 55)

    while True:
        config = _current_trader_config()
        if config is not None:
            print(f"[{time.strftime('%H:%M:%S')}] Config found: {config.name}")
            _start_bot(config)
            print(f"[{time.strftime('%H:%M:%S')}] Restarting in {POLL_SECONDS}s...")
        else:
            sys.stdout.write(f"\r[{time.strftime('%H:%M:%S')}] No config yet — waiting...")
            sys.stdout.flush()
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
