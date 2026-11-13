#!/usr/bin/env python3
"""IPv4/IPv6 maintenance. Python 3.9+, standard library only."""
import argparse
import ctypes
import os
import platform
import shutil
import subprocess
import sys
import uuid

VERSION = '2.0.0'
NETWORK_ACTIONS = ('list', 'auto', 'release', 'renew', 'flush', 'reset')
FAMILIES = ('ipv4', 'ipv6')


def help_text():
    print('''\nQUICK HELP
List shows both IPv4 and IPv6. Flush clears the shared system DNS cache.
Auto/reset requires an explicit IPv4 or IPv6 choice and may replace static settings.
IPv6 auto uses router advertisements/SLAAC and DHCPv6 as supported by the network.
Release/renew is implemented only on Windows and operates on DHCP leases.
DHCPv6 release/renew does not release or renew SLAAC addresses.
On macOS, auto/reset preserves shared DNS server settings.
On Linux, auto/reset edits one family but profile activation may interrupt both.
Windows IPv6 auto/reset enables router discovery and automatic DNS; existing manual
IPv6 addresses/routes remain. It does not enable an OS-disabled IPv6 stack.
Use --dry-run to preview commands, and a local console for actual changes.
Changes require Administrator privileges or sudo. There is no automatic rollback.
See README.md for platform behavior and requirements.''')


def windows_commands(action, target, family):
    if action == 'list':
        return [['ipconfig', '/all']]
    if action == 'flush':
        return [['ipconfig', '/flushdns']]
    suffix = '6' if family == 'ipv6' else ''
    if action in ('release', 'renew'):
        return [['ipconfig', '/' + action + suffix, target]]
    if family == 'ipv4':
        automatic = [['netsh', 'interface', 'ipv4', 'set', 'address',
                      'name=' + target, 'source=dhcp']]
    else:
        automatic = [['netsh', 'interface', 'ipv6', 'set', 'interface',
                      'interface=' + target, 'routerdiscovery=enabled', 'store=persistent']]
    automatic += [['netsh', 'interface', family, 'set', 'dnsservers',
                   'name=' + target, 'source=dhcp']]
    if action == 'reset':
        # DHCPv6 may not be deployed on a SLAAC network: never force a lease cycle.
        if family == 'ipv4':
            automatic += [['ipconfig', '/release', target], ['ipconfig', '/renew', target]]
        automatic += [['ipconfig', '/flushdns']]
    return automatic


def macos_commands(action, target, family):
    if action == 'list':
        return [['networksetup', '-listallhardwareports'],
                ['networksetup', '-listallnetworkservices'], ['ifconfig']]
    flush = [['dscacheutil', '-flushcache'], ['killall', '-HUP', 'mDNSResponder']]
    if action == 'flush':
        return flush
    if action in ('release', 'renew'):
        raise ValueError('macOS: family-specific lease release/renew is unsupported; use auto to reapply addressing.')
    # DNS settings belong to the service, not one address family. Preserve them.
    flag = '-setdhcp' if family == 'ipv4' else '-setv6automatic'
    return [['networksetup', flag, target]] + (flush if action == 'reset' else [])


def linux_commands(action, target, family):
    if action == 'list':
        return [['nmcli', 'device', 'status'],
                ['nmcli', '-f', 'NAME,UUID,TYPE,DEVICE', 'connection', 'show'],
                ['nmcli', 'device', 'show']]
    if action == 'flush':
        return [['resolvectl', 'flush-caches']]
    if action in ('release', 'renew'):
        raise ValueError('Linux: family-specific lease release/renew is unsupported; profile down/up affects both families.')
    commands = [['nmcli', 'connection', 'modify', 'uuid', target,
                 family + '.method', 'auto', family + '.addresses', '',
                 family + '.gateway', '', family + '.dns', '',
                 family + '.ignore-auto-dns', 'no'],
                ['nmcli', 'connection', 'up', 'uuid', target]]
    if action == 'reset':
        commands += [['resolvectl', 'flush-caches']]
    return commands


BUILDERS = {'Windows': windows_commands, 'Darwin': macos_commands, 'Linux': linux_commands}


def plan(system, action, target='', family=None):
    """Validate scope and return argument arrays; never execute commands here."""
    if system not in BUILDERS:
        raise ValueError('Supported systems: Windows, macOS, Linux with NetworkManager.')
    if action not in NETWORK_ACTIONS:
        raise ValueError('Unknown action.')
    if action in ('list', 'flush'):
        if family is not None or target:
            raise ValueError('List/flush are shared operations; omit --family and --target.')
    else:
        if family not in FAMILIES:
            raise ValueError('Choose --family ipv4 or --family ipv6 explicitly.')
        if (not target.strip() or target != target.strip() or target.startswith('-')
                or any(c in target for c in '\r\n\x00*?')):
            raise ValueError('Supply one exact target; wildcards and option-like names are not allowed.')
        if system == 'Linux':
            try:
                target = str(uuid.UUID(target))
            except ValueError:
                raise ValueError('Linux targets must be connection UUIDs from List.') from None
    return BUILDERS[system](action, target, family)


def describe_effects(system, action, family):
    if action == 'list':
        return
    if action == 'flush':
        print('Scope: shared system DNS cache, both address families.')
        return
    print(f'Selected address family: {family}. Network changes may disconnect you.')
    if action in ('auto', 'reset'):
        if system == 'Windows' and family == 'ipv6':
            print('Enables router discovery and automatic IPv6 DNS; manual IPv6 addresses/routes remain.')
        else:
            print('Automatic addressing replaces selected-family static address configuration.')
        if system == 'Darwin':
            print('Shared macOS DNS server configuration is preserved.')
        elif system == 'Linux':
            print('Clears selected-family manual addresses/gateway/DNS. Profile activation can interrupt BOTH families.')
        else:
            print('Selected-family DNS server configuration becomes automatic.')
    if system == 'Windows' and family == 'ipv6' and action in ('release', 'renew'):
        print('DHCPv6 leases only; SLAAC addresses are not released/renewed. Requires DHCPv6 configuration.')
    if action == 'reset':
        print('Also flushes the shared system DNS cache.')


def execute(commands, system, modifying, dry_run=False):
    for cmd in commands:
        print('  ' + repr(cmd), flush=True)
    if dry_run:
        print('Preview only: no commands executed.')
        return True
    resolved = []
    for cmd in commands:
        executable = shutil.which(cmd[0])
        if not executable:
            raise RuntimeError(f'Required command missing: {cmd[0]}. No commands executed.')
        resolved.append([executable] + cmd[1:])
    if modifying:
        admin = ctypes.windll.shell32.IsUserAnAdmin() if system == 'Windows' else os.geteuid() == 0
        if not admin:
            raise RuntimeError('Run in an Administrator terminal (Windows) or with sudo (macOS/Linux).')
        print('Record existing settings first. Use a local console. No automatic rollback.')
        if input('Type YES to execute: ').strip() != 'YES':
            print('Canceled.')
            return False
    for cmd in resolved:
        subprocess.run(cmd, check=True, shell=False)
    print('Commands completed; this does not guarantee Internet connectivity.')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=(*NETWORK_ACTIONS, 'help'))
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('--family', choices=FAMILIES, help='Required for addressing actions; no implicit default')
    parser.add_argument('--target', help='Windows adapter name; macOS service name; Linux connection UUID')
    parser.add_argument('--dry-run', action='store_true', help='Print commands without running anything')
    args = parser.parse_args(argv)
    if args.action == 'help':
        help_text()
        return 0
    if args.action in ('auto', 'release', 'renew', 'reset'):
        if not args.family or not args.target:
            parser.error('Addressing actions require --family and --target. Omit the action for an interactive menu.')
    if args.action in ('list', 'flush') and (args.family or args.target):
        parser.error('List/flush are shared operations; omit --family and --target.')
    system = platform.system()
    names = {'Windows': 'adapter name', 'Darwin': 'network service name', 'Linux': 'connection UUID'}
    actions = dict(zip('123456', NETWORK_ACTIONS))
    while True:
        action = args.action
        if not action:
            print(f'\nIP Network Manager | {system} | v{VERSION}')
            print('1. List IPv4/IPv6 settings\n2. Enable automatic addressing\n3. Release DHCP lease (Windows only)\n4. Renew DHCP lease (Windows only)\n5. Flush shared DNS cache\n6. Automatic addressing + refresh/cache flush\n7. Quick Help\n8. Exit')
            selection = input('Select 1-8: ').strip()
            if selection == '8':
                return 0
            if selection == '7':
                help_text()
                continue
            action = actions.get(selection)
            if not action:
                print('Invalid selection.')
                continue
        try:
            target, family = '', None
            if action not in ('list', 'flush'):
                family = args.family or input('Address family (ipv4/ipv6): ').strip().lower()
                if family not in FAMILIES:
                    raise ValueError('Enter ipv4 or ipv6; neither is selected by default.')
                target = args.target or input('Enter ' + names.get(system, 'target') + ': ').strip()
            commands = plan(system, action, target, family)
            describe_effects(system, action, family)
            completed = execute(commands, system, action != 'list', args.dry_run)
            if args.action:
                return 0 if completed else 130
        except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            print('Error: ' + str(exc), file=sys.stderr)
            print('Stopped. If earlier commands succeeded, their changes may remain.', file=sys.stderr)
            if args.action:
                return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nCanceled. Inspect settings if commands already ran.')
        sys.exit(130)
