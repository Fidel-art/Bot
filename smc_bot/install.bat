@echo off
echo ========================================
echo SMC Trading Bot - Installation Script
echo ========================================
echo.

echo Installing required Python packages...
echo.

pip install --upgrade pip
pip install MetaTrader5>=5.0.45
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install colorama>=0.4.6

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure MetaTrader 5 is installed
echo 2. Run the bot: python main.py
echo.
echo For help, see:
echo - README.md (complete documentation)
echo - QUICKSTART.md (getting started guide)
echo.
pause
