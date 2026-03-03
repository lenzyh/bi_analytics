#!/usr/bin/env python3
"""
Web3 BI Dashboard - Demo Launcher
Simplified launcher script for the Streamlit dashboard application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import plotly
        import numpy
        import requests
        print("All required core packages are installed")
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please run: uv sync")
        return False

def main():
    """Main launcher function"""
    print("Web3 BI Dashboard - Demo Launcher")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("app.py not found. Please run this script from the bi_analytics directory")
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    print("\nStarting Web3 BI Dashboard...")
    print("The dashboard will open in your default web browser")
    print("Login credentials: admin / password")
    print("\n" + "=" * 50)

    try:
        subprocess.run([
            "uv", "run", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\nError starting dashboard: {e}")
        print("Make sure uv is installed: https://docs.astral.sh/uv/getting-started/installation/")
        sys.exit(1)

if __name__ == "__main__":
    main()
