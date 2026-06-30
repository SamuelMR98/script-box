#!/usr/bin/env python3

"""
Environment Auditor

Validates `.env` files against required variables and checks for missing or extra variables.
Required variables can be specified in a separate configuration file (txt, JSON, or YAML format) or hardcoded as a list in the script.
"""

from dotenv import dotenv_values
import os
import sys
import json
import yaml

def load_required_variables(config_file):
    """
    Load required environment variables from a configuration file.
    Supports JSON and YAML formats.
    """
    if not os.path.exists(config_file):
        print(f"Configuration file '{config_file}' does not exist.")
        sys.exit(1)

    with open(config_file, 'r') as f:
        if config_file.endswith('.json'):
            return json.load(f)
        elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            print("Unsupported configuration file format. Use JSON or YAML.")
            sys.exit(1)

def validate_env_file(env_file, required_vars):
    """
    Validate the .env file against the required variables.
    """
    if not os.path.exists(env_file):
        print(f".env file '{env_file}' does not exist.")
        sys.exit(1)

    env_vars = dotenv_values(env_file)
    missing_vars = [var for var in required_vars if var not in env_vars]
    extra_vars = [var for var in env_vars if var not in required_vars]

    return missing_vars, extra_vars

def main():
    if len(sys.argv) != 3:
        print("Usage: python env_auditor.py <.env file> <config file>")
        sys.exit(1)

    env_file = sys.argv[1]
    config_file = sys.argv[2]

    required_vars = load_required_variables(config_file)
    missing_vars, extra_vars = validate_env_file(env_file, required_vars)

    if missing_vars:
        print("Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
    else:
        print("No missing environment variables.")

    if extra_vars:
        print("Extra environment variables:")
        for var in extra_vars:
            print(f"  - {var}")
    else:
        print("No extra environment variables.")

if __name__ == "__main__":
    main()
