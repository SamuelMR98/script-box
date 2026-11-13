#!/usr/bin/env python3

"""IPv4 maintenance menu. Python 3.9+, standard library only."""
import argparse
import ctypes
import json
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys
import uuid


AUTHOR = 'SMR (Sam)'
VERSION = '1.1.0'


def about():
    """Display links without opening a browser from an elevated process."""
    print(f'\n SMR | IPv4 Network Manager v{VERSION}')
    print(f'Created by {AUTHOR} | Software Engineer | Mexico')
    print('From a Windows batch utility to cross-platform network maintenance.')
    config = Path(__file__).with_name('socials.json')
    try:
        links = json.loads(config.read_text(encoding='utf-8'))
        if not isinstance(links, dict):
            raise ValueError('Expected an object mapping social names to URLs.')
        print('\nSocial links (copy a configured URL into your browser):')
        for name, url in links.items():
            if not isinstance(url, str):
                raise ValueError('Social URLs must be strings.')
            if url and not url.startswith('https://'):
                raise ValueError('Social URLs must start with https://.')
            print(f'  {name}: {url or "Not configured"}')
        print('Edit socials.json beside this script to add your actual links.')
    except (OSError, ValueError) as exc:
        print(f'Cannot load socials.json: {exc}')


def help_text():
    print('\nQUICK HELP')
    print('Start with List to identify your adapter, macOS service, or Linux profile UUID.')
    print('Use --dry-run to preview commands. Changes need Administrator privileges or sudo.')
    print('DHCP/reset replaces static IPv4 and manual DNS. Record current settings first.')
    print('Use a local terminal; release/reconnect may disconnect remote sessions.')
    print('macOS release is unsupported. Linux requires NetworkManager; DNS flush needs systemd-resolved.')
    print('See README.md for setup, examples, platform differences, and recovery limitations.')


def plan(system, action, target=''):
    if system not in ('Windows', 'Darwin', 'Linux'):
        raise ValueError('Supported systems: Windows, macOS, Linux with NetworkManager.')
    if action not in ('list', 'dhcp', 'release', 'renew', 'flush', 'reset'):
        raise ValueError('Unknown action.')
    if action not in ('list', 'flush'):
        if not target.strip() or target.startswith('-') or any(c in target for c in '\r\n\x00*?'):
            raise ValueError('Supply one exact target; wildcards and option-like names are not allowed.')
        if system == 'Linux':
            target = str(uuid.UUID(target))
    if system == 'Windows':
        dhcp = [['netsh', 'interface', 'ipv4', 'set', 'address', 'name=' + target, 'source=dhcp'],
                ['netsh', 'interface', 'ipv4', 'set', 'dnsservers', 'name=' + target, 'source=dhcp']]
        release = [['ipconfig', '/release', target]]
        renew = [['ipconfig', '/renew', target]]
        flush = [['ipconfig', '/flushdns']]
        listing = [['ipconfig', '/all']]
    elif system == 'Darwin':
        dhcp = [['networksetup', '-setdhcp', target], ['networksetup', '-setdnsservers', target, 'Empty']]
        release = []
        renew = [['networksetup', '-setdhcp', target]]
        flush = [['dscacheutil', '-flushcache'], ['killall', '-HUP', 'mDNSResponder']]
        listing = [['networksetup', '-listallhardwareports'], ['networksetup', '-listallnetworkservices'], ['ifconfig']]
        if action == 'release':
            raise ValueError('macOS: standalone DHCP release is not implemented. Use DHCP/reapply or reset.')
    else:
        base = ['nmcli', 'connection']
        dhcp = [base + ['modify', 'uuid', target, 'ipv4.method', 'auto',
                        'ipv4.addresses', '', 'ipv4.gateway', '', 'ipv4.dns', '',
                        'ipv4.ignore-auto-dns', 'no'], base + ['up', 'uuid', target]]
        release = [base + ['down', 'uuid', target]]
        renew = [base + ['up', 'uuid', target]]
        flush = [['resolvectl', 'flush-caches']]
        listing = [['nmcli', 'device', 'status'], ['nmcli', '-f', 'NAME,UUID,TYPE,DEVICE', 'connection', 'show'], ['nmcli', 'device', 'show']]
    # Linux activation reapplies the profile; macOS reapplies DHCP without a separate release.
    reset = dhcp + (release + renew if system == 'Windows' else []) + flush
    return {'list': listing, 'dhcp': dhcp, 'release': release, 'renew': renew,
            'flush': flush, 'reset': reset}[action]


def execute(commands, system, modifying, dry_run=False):
    for cmd in commands:
        print('  ' + repr(cmd), flush=True)
    if dry_run:
        print('Preview only: no commands executed.')
        return
    # Preflight every executable before any changes.
    resolved = []
    for cmd in commands:
        executable = shutil.which(cmd[0])
        if not executable:
            raise RuntimeError('Required command missing: ' + cmd[0] + '. No commands executed.')
        resolved.append([executable] + cmd[1:])
    if modifying:
        admin = ctypes.windll.shell32.IsUserAnAdmin() if system == 'Windows' else os.geteuid() == 0
        if not admin:
            raise RuntimeError('Run in an Administrator terminal (Windows) or with sudo (macOS/Linux).')
        print('This may disconnect you. DHCP/reset replaces static IPv4 and manual IPv4 DNS settings.')
        print('No automatic rollback. Record existing settings first; use a local terminal.')
        if input('Type YES to execute: ').strip() != 'YES':
            print('Canceled.')
            return
    for cmd in resolved:
        subprocess.run(cmd, check=True, shell=False)
    print('Commands completed successfully; this does not guarantee Internet connectivity.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', nargs='?', choices=['list', 'dhcp', 'release', 'renew', 'flush', 'reset', 'about', 'help'])
    p.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    p.add_argument('--target', help='Windows adapter name; macOS network service name; Linux connection UUID')
    p.add_argument('--dry-run', action='store_true', help='Print commands without running anything')
    args = p.parse_args()
    if args.action in ('about', 'help'):
        (about if args.action == 'about' else help_text)()
        return 0
    system = platform.system()
    names = {'Windows': 'adapter name (e.g. Wi-Fi)', 'Darwin': 'network service name (e.g. Wi-Fi)', 'Linux': 'connection UUID (from List)'}
    actions = dict(zip('123456', ['list', 'dhcp', 'release', 'renew', 'flush', 'reset']))
    while True:
        action = args.action
        if not action:
            print('\n SMR | IPv4 Network Manager | ' + system)
            print(f'Created by {AUTHOR} | v{VERSION}')
            print('1. List adapters/settings\n2. Enable DHCP + automatic DNS\n3. Release (Windows) / deactivate profile (Linux)\n4. Renew (Windows) / reapply DHCP (macOS) / activate profile (Linux)\n5. Flush system DNS cache\n6. Enable DHCP + refresh + flush DNS\n7. About & Social Links\n8. Quick Help\n9. Exit')
            selection = input('Select 1-9: ').strip()
            if selection == '9':
                return 0
            if selection in ('7', '8'):
                (about if selection == '7' else help_text)()
                input('Press Enter to return to the menu...')
                continue
            action = actions.get(selection)
            if not action:
                print('Invalid selection.')
                continue
        try:
            target = args.target or ''
            if action not in ('list', 'flush') and not target:
                target = input('Enter ' + names.get(system, 'target') + ': ').strip()
            execute(plan(system, action, target), system, action != 'list', args.dry_run)
        except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            print('Error: ' + str(exc), file=sys.stderr)
            print('Stopped. Earlier successful changes may remain; no automatic rollback.', file=sys.stderr)
            if args.action:
                return 1
        if args.action:
            return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nCanceled. If commands already ran, inspect network settings before retrying.')
        sys.exit(130)
