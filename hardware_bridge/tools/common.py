"""Shared paths and validation. No third-party dependencies."""
from pathlib import Path
import json
import os
import socket
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime'
CONFIG = RUNTIME / 'local_config.json'

def private_python():
    for p in (ROOT/'.venv/Scripts/python.exe', ROOT/'.venv/bin/python.exe', ROOT/'.venv/bin/python'):
        if p.is_file():
            return p
    raise RuntimeError('Run 01_Setup.bat first: the private Python environment is missing.')

def load_config():
    if not CONFIG.is_file():
        raise RuntimeError('Run 01_Setup.bat first.')
    return json.loads(CONFIG.read_text(encoding='utf-8'))

def properties():
    p = RUNTIME / 'server.properties'
    result = {}
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith(('#','!')) and '=' in line:
            key, value = line.split('=', 1)
            result[key.strip()] = value.strip()
    return result

def port_open(port):
    try:
        with socket.create_connection(('127.0.0.1', int(port)), timeout=0.3):
            return True
    except OSError:
        return False

def java_major(java):
    result = subprocess.run([str(java), '-version'], capture_output=True, text=True, timeout=15)
    output = result.stdout + result.stderr
    match = re.search(r'(?:openjdk|java) version "(\d+)(?:\.(\d+))?', output)
    if result.returncode or not match:
        raise RuntimeError('Could not read Java version. Check the selected java.exe path.')
    return int(match.group(2)) if match.group(1) == '1' else int(match.group(1))

def require_java(java):
    version = java_major(java)
    if version < 25:
        raise RuntimeError(f'Java {version} was selected. Install Java 25, then rerun setup and select its java.exe.')

def bridge_environment(config):
    props = properties()
    if props.get('enable-rcon') != 'true' or props.get('rcon.port') != '25575':
        raise RuntimeError('This starter expects enabled local RCON on port 25575.')
    password = props.get('rcon.password', '')
    if not password:
        raise RuntimeError('The local RCON password is missing. Run setup again.')
    env = dict(os.environ)
    env['DE10_SERIAL_PORT'] = config['serial_port']
    env['DE10_RCON_PASSWORD'] = password
    return env
