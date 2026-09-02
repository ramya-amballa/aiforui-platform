#!/usr/bin/env python3
"""Entry point: python main.py <command> [options]

Run `python main.py --help` for the full command list.
"""
from src.cli.main import cli

if __name__ == "__main__":
    cli()
