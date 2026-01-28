"""
Database Package for SMC Trading Bot

Contains database management and data persistence modules.
"""

from .db import DatabaseManager, get_db_manager

__all__ = ['DatabaseManager', 'get_db_manager']
