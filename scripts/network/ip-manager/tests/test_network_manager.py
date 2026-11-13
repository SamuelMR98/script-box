import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch
import network_manager as nm

UUID = '12345678-1234-1234-1234-123456789abc'


class Tests(unittest.TestCase):
    def test_requires_explicit_family(self):
        for system in nm.BUILDERS:
            for action in ('auto', 'reset', 'release', 'renew'):
                with self.assertRaises(ValueError):
                    nm.plan(system, action, UUID)

    def test_shared_operations_reject_scope(self):
        for action in ('list', 'flush'):
            for family in nm.FAMILIES:
                with self.assertRaises(ValueError):
                    nm.plan('Windows', action, family=family)
            with self.assertRaises(ValueError):
                nm.plan('Windows', action, 'Wi-Fi')

    def test_windows_leases_scoped_to_adapter_and_family(self):
        for family, suffix in [('ipv4', ''), ('ipv6', '6')]:
            for action in ('release', 'renew'):
                self.assertEqual(nm.plan('Windows', action, 'Wi-Fi', family),
                                 [['ipconfig', '/' + action + suffix, 'Wi-Fi']])

    def test_windows_ipv6_reset_avoids_dhcpv6_dependency(self):
        commands = nm.plan('Windows', 'reset', 'Wi-Fi', 'ipv6')
        self.assertIn('routerdiscovery=enabled', commands[0])
        self.assertEqual(commands[-1], ['ipconfig', '/flushdns'])
        self.assertFalse(any('/release6' in c or '/renew6' in c for c in commands))
        self.assertFalse(any('ipv4' in c for c in commands))

    def test_windows_ipv4_reset_keeps_lease_cycle(self):
        cmds = nm.plan('Windows', 'reset', 'Ethernet 2', 'ipv4')
        self.assertIn(['ipconfig', '/release', 'Ethernet 2'], cmds)
        self.assertIn(['ipconfig', '/renew', 'Ethernet 2'], cmds)

    def test_mac_auto_preserves_shared_dns(self):
        for family, flag in [('ipv4', '-setdhcp'), ('ipv6', '-setv6automatic')]:
            self.assertEqual(nm.plan('Darwin', 'auto', 'Wi-Fi', family),
                             [['networksetup', flag, 'Wi-Fi']])

    def test_linux_changes_only_selected_family_settings(self):
        for family, other in [('ipv4', 'ipv6'), ('ipv6', 'ipv4')]:
            cmds = nm.plan('Linux', 'auto', UUID, family)
            self.assertIn(family + '.method', cmds[0])
            self.assertIn(family + '.addresses', cmds[0])
            self.assertFalse(any(arg.startswith(other + '.') for cmd in cmds for arg in cmd))
            self.assertEqual(cmds[1], ['nmcli', 'connection', 'up', 'uuid', UUID])

    def test_unsupported_lease_actions(self):
        for system, target in [('Darwin', 'Wi-Fi'), ('Linux', UUID)]:
            for family in nm.FAMILIES:
                for action in ('release', 'renew'):
                    with self.assertRaises(ValueError):
                        nm.plan(system, action, target, family)

    def test_invalid_targets(self):
        for target in ('', '*', 'Wi?Fi', '-all', ' Wi-Fi'):
            with self.assertRaises(ValueError):
                nm.plan('Windows', 'auto', target, 'ipv6')
        with self.assertRaises(ValueError):
            nm.plan('Linux', 'auto', 'eth0', 'ipv6')

    def test_preview_never_executes_or_prompts(self):
        with patch.object(nm.subprocess, 'run') as run, patch('builtins.input') as ask:
            nm.execute(nm.plan('Windows', 'reset', 'Wi-Fi', 'ipv6'), 'Windows', True, True)
            run.assert_not_called()
            ask.assert_not_called()

    def test_missing_tool_preflight(self):
        with patch.object(nm.shutil, 'which', side_effect=['/bin/one', None]), patch.object(nm.subprocess, 'run') as run:
            with self.assertRaises(RuntimeError):
                nm.execute([['one'], ['two']], 'Linux', False)
            run.assert_not_called()

    def test_stops_on_failure(self):
        with patch.object(nm.shutil, 'which', side_effect=lambda x: '/bin/' + x), patch.object(nm.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'one')) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                nm.execute([['one'], ['two']], 'Linux', False)
            self.assertEqual(run.call_count, 1)
            self.assertFalse(run.call_args.kwargs['shell'])

    def test_cli_requires_scope_before_prompt(self):
        for args in [['auto'], ['reset', '--family', 'ipv6'], ['flush', '--family', 'ipv4']]:
            with patch('builtins.input') as ask, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    nm.main(args)
                self.assertEqual(exc.exception.code, 2)
                ask.assert_not_called()

    def test_interactive_family_and_exit(self):
        with patch.object(nm.platform, 'system', return_value='Windows'), patch('builtins.input', side_effect=['2', 'ipv6', 'Wi-Fi', '8']), patch.object(nm.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(nm.main(['--dry-run']), 0)
            self.assertIn('routerdiscovery=enabled', out.getvalue())
            run.assert_not_called()

    def test_cancel_does_not_execute(self):
        with patch.object(nm.shutil, 'which', return_value='/bin/tool'), patch.object(nm.os, 'geteuid', return_value=0), patch('builtins.input', return_value='NO'), patch.object(nm.subprocess, 'run') as run:
            self.assertFalse(nm.execute([['tool']], 'Linux', True))
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
