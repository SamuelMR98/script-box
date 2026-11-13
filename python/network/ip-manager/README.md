# IP Network Manager

A command-line utility for inspecting IPv4 and IPv6 settings, enabling automatic addressing, managing Windows DHCP leases, and flushing the system DNS cache.

**Version:** 2.0.0  
**Platforms:** Windows, macOS, and Linux with NetworkManager  
**Python:** 3.9 or newer, standard library only

Two standalone implementations are available:

| Script                | Platforms             | Interface                                   |
| --------------------- | --------------------- | ------------------------------------------- |
| `network_manager.py`  | Windows, macOS, Linux | Interactive menu and command-line arguments |
| `network_manager.bat` | Windows               | Interactive menu                            |

Each script runs independently. No configuration files, Python packages, or companion scripts are required. The Windows batch version does not require Python.

## Features

- Display adapter and connection information for both IPv4 and IPv6.
- Select IPv4 or IPv6 explicitly before changing addressing settings.
- Enable automatic IPv4 addressing or IPv6 autoconfiguration.
- Release and renew DHCP or DHCPv6 leases on Windows.
- Flush the shared system DNS cache.
- Preview commands without executing them using the Python `--dry-run` option.
- Check required executables and administrator privileges before executing changes.
- Confirm modifications and stop an action when a command fails.

## Requirements

| Platform         | Required tools                                                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Windows — Python | Python 3.9+, `ipconfig`, and `netsh`                                                                                                                                      |
| Windows — batch  | Windows PowerShell, `ipconfig`, and `netsh`                                                                                                                               |
| macOS            | Python 3.9+, `networksetup`, `ifconfig`, `dscacheutil`, and `killall`                                                                                                     |
| Linux            | Python 3.9+, `nmcli`, and a running NetworkManager service for listing and addressing operations; `resolvectl` and a running systemd-resolved service for DNS flush/reset |

Listing settings, viewing help, and previewing commands do not require elevated privileges. Actual changes require an **Administrator terminal** on Windows or **`sudo`** on macOS/Linux. Neither script elevates itself automatically.

## Getting started

### From a cloned repository

```sh
git clone https://github.com/SamuelMR98/script-box.git
cd script-box/networking/ip-manager
```

On macOS or Linux, open the menu in preview mode:

```sh
python3 network_manager.py --dry-run
```

On Windows:

```powershell
py -3 network_manager.py --dry-run
```

Preview mode displays the commands that would run without changing network settings. Remove `--dry-run` to execute an operation.

### From a single downloaded script

Download either `network_manager.py` or `network_manager.bat` using GitHub's **Raw** download option, then open a terminal in the directory containing the file.

For the Python script:

```sh
python3 network_manager.py --dry-run
```

On Windows, use `py -3` instead of `python3`:

```powershell
py -3 network_manager.py --dry-run
```

For the Windows batch script, double-click `network_manager.bat` to open the menu. To modify settings, right-click the file and select **Run as administrator**, or run it from an Administrator terminal:

```powershell
.\network_manager.bat
```

The batch script has no preview mode. Neither standalone script needs the README or tests to run.

## Interactive menu

Run either script without an action argument to open its menu.

| Option | Operation                                                                                              |
| ------ | ------------------------------------------------------------------------------------------------------ |
| 1      | List IPv4 and IPv6 settings                                                                            |
| 2      | Enable automatic addressing                                                                            |
| 3      | Release a DHCP lease — Windows only                                                                    |
| 4      | Renew a DHCP lease — Windows only                                                                      |
| 5      | Flush the shared DNS cache                                                                             |
| 6      | Enable automatic addressing and refresh the DNS cache; Windows IPv4 also releases and renews its lease |
| 7      | Show quick help                                                                                        |
| 8      | Exit                                                                                                   |

Addressing operations ask for an address family and a target. Enter `ipv4` or `ipv6` in Python, or select **4** or **6** in the batch menu. No family is selected by default.

Python requires typing `YES` before executing modifications. The batch script prompts for **Y/N**. In Python preview mode, no execution confirmation is needed because no commands run.

## Python command-line interface

```text
python3 network_manager.py [action] [--family ipv4|ipv6] [--target TARGET] [--dry-run]
```

| Argument    | Description                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| `action`    | `list`, `auto`, `release`, `renew`, `flush`, `reset`, or `help`. Omit it to open the menu.                 |
| `--family`  | `ipv4` or `ipv6`. Required for one-shot addressing operations.                                             |
| `--target`  | Exact adapter name, network service name, or connection UUID. Required for one-shot addressing operations. |
| `--dry-run` | Print planned network commands without executing them.                                                     |
| `--help`    | Show command-line syntax and options.                                                                      |
| `--version` | Print the script version.                                                                                  |

`auto`, `release`, `renew`, and `reset` require both `--family` and `--target`. Missing arguments produce an error before prompting for execution.

`list` and `flush` are shared operations and reject `--family` and `--target` when invoked directly. In menu mode, these flags can preselect the target and family for addressing actions; they do not restrict listing or cache flushing.

### Choosing a target

Start with:

```sh
python3 network_manager.py list
```

| Platform | Target type                          | Example                                                             |
| -------- | ------------------------------------ | ------------------------------------------------------------------- |
| Windows  | Exact adapter name                   | `"Wi-Fi"` or `"Ethernet"`                                           |
| macOS    | Network service name                 | `"Wi-Fi"`, not a device identifier such as `en0`                    |
| Linux    | Saved NetworkManager connection UUID | The UUID shown in the connection list, not `eth0` or a profile name |

Quote names containing spaces. Wildcards are not accepted.

## Usage examples

### Inspect settings and preview changes

```sh
python3 network_manager.py list
python3 network_manager.py flush --dry-run
python3 network_manager.py help
```

### Windows

Preview automatic IPv4 or IPv6 configuration:

```powershell
py -3 network_manager.py auto --family ipv4 --target "Wi-Fi" --dry-run
py -3 network_manager.py auto --family ipv6 --target "Wi-Fi" --dry-run
```

From an Administrator terminal, renew a DHCP lease:

```powershell
py -3 network_manager.py renew --family ipv4 --target "Ethernet"
```

For an adapter using DHCPv6:

```powershell
py -3 network_manager.py renew --family ipv6 --target "Wi-Fi"
```

### macOS

Preview IPv6 automatic addressing, then apply it:

```sh
python3 network_manager.py auto --family ipv6 --target "Wi-Fi" --dry-run
sudo python3 network_manager.py auto --family ipv6 --target "Wi-Fi"
```

Enable IPv4 DHCP:

```sh
sudo python3 network_manager.py auto --family ipv4 --target "Wi-Fi"
```

### Linux with NetworkManager

Replace `CONNECTION-UUID` with the UUID shown by `list`:

```sh
python3 network_manager.py auto --family ipv6 --target "CONNECTION-UUID" --dry-run
sudo python3 network_manager.py auto --family ipv6 --target "CONNECTION-UUID"
```

Preview an IPv4 reset:

```sh
python3 network_manager.py reset --family ipv4 --target "CONNECTION-UUID" --dry-run
```

### Flush DNS

macOS/Linux:

```sh
sudo python3 network_manager.py flush
```

Windows, from an Administrator terminal:

```powershell
py -3 network_manager.py flush
```

## Platform behavior

IPv6 automatic addressing can use router advertisements, SLAAC, and DHCPv6 depending on the network and operating system. A DHCPv6 lease operation does not release or renew SLAAC addresses. Automatic configuration does not guarantee a globally routable IPv6 address.

| Operation     | Windows                                                                                   | macOS                                                    | Linux / NetworkManager                                                                                    |
| ------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| List          | Displays both families with `ipconfig`                                                    | Displays ports, services, and addresses                  | Displays profiles, devices, and both families                                                             |
| Auto IPv4     | Enables DHCP and automatic IPv4 DNS                                                       | Reapplies DHCP; preserves service DNS                    | Clears manual IPv4 addresses, gateway, and DNS; enables automatic configuration and activates the profile |
| Auto IPv6     | Enables router discovery and automatic IPv6 DNS; retains manual IPv6 addresses and routes | Enables automatic IPv6 addressing; preserves service DNS | Clears manual IPv6 addresses, gateway, and DNS; enables automatic configuration and activates the profile |
| Release/renew | Selected adapter's DHCP lease for IPv4 or DHCPv6 lease for IPv6                           | Unsupported                                              | Unsupported                                                                                               |
| Flush         | Clears the shared system DNS cache                                                        | Clears the shared system DNS cache                       | Clears systemd-resolved's cache                                                                           |
| Reset IPv4    | Auto, release, renew, and DNS flush                                                       | Auto and DNS flush                                       | Auto/profile activation and DNS flush                                                                     |
| Reset IPv6    | Auto and DNS flush; no forced DHCPv6 lease cycle                                          | Auto and DNS flush                                       | Auto/profile activation and DNS flush                                                                     |

## Scope and limitations

- **Connection interruptions:** Addressing changes may disconnect SSH, remote desktop, or other sessions. Use a local console and record existing settings before applying changes. There is no automatic backup or rollback.
- **Static settings:** Auto/reset may replace selected-family static configuration. Windows IPv6 retains manual addresses and routes, so it is not a full conversion of a static IPv6 setup. It also does not re-enable IPv6 when disabled at the OS or adapter-binding level.
- **macOS DNS:** DNS server settings are shared by the network service. Auto/reset preserves them; flushing removes cached answers without changing configured servers.
- **Linux profile activation:** Only the selected family's profile settings are edited, but activating the profile may interrupt both families. If activation fails, the saved profile can still contain the new settings.
- **Lease operations:** Release/renew is supported only on Windows. The scripts do not substitute whole-profile disconnect/reconnect operations on Linux or macOS.
- **DNS scope:** Flushing is system-wide and covers both address families. DNS servers reached over either family can resolve both A and AAAA records. Browser, upstream, dnsmasq, and nscd caches are not flushed.
- **Reset scope:** Reset is not a full network-stack or router reset. Custom routes, search domains, client IDs, and advanced policy are not reset.
- **Failure handling:** Python checks for required executables before running commands. Service failures can still occur after earlier commands have succeeded, and those earlier changes may remain.
- **Results:** Successful commands do not guarantee Internet connectivity or a different IP address. Router, VPN, and organization policies can affect results.
- **Adapter names:** Batch uses conservative name validation. The Python version supports additional characters and passes arguments without shell expansion.

## Troubleshooting

| Message or situation              | What it means                                                                                                                           |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Administrator privileges required | Reopen the Windows terminal as Administrator, or use `sudo` on macOS/Linux.                                                             |
| Required command missing          | A platform dependency is unavailable. Python stops before executing the planned commands.                                               |
| Linux target must be a UUID       | Run `list` and use the saved connection's UUID.                                                                                         |
| Release/renew unsupported         | This action is available only for Windows DHCP leases. `auto` reapplies addressing configuration but is not a lease-renewal equivalent. |
| IPv6 renewal fails                | The adapter may not have a DHCPv6 configuration. SLAAC addresses are not renewed through DHCPv6 commands.                               |
| Linux DNS flush fails             | Check that `resolvectl` is installed and systemd-resolved is running. Other DNS caches are unsupported.                                 |

## Tests and validation

The repository includes mocked tests. From the utility directory, run:

```sh
python3 -m unittest discover -s tests -v
```

Tests cover explicit family selection, command scope, macOS DNS preservation, Windows DHCPv6 command selection, unsupported actions, CLI validation, menu navigation, cancellation, previews, and execution failures.

The test suite does not modify network settings. Syntax and preview checks were performed on Linux. The Windows batch script was inspected but not executed, and live network operations have not been validated across all supported platforms.

## References

- [Microsoft ipconfig](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)
- [Microsoft netsh interface](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-interface)
- [Apple networksetup](https://support.apple.com/en-ng/guide/remote-desktop/apdd0c5a2d5/mac)
- [NetworkManager IPv6 settings](https://networkmanager.dev/docs/api/latest/settings-ipv6.html)
- [NetworkManager nmcli](https://networkmanager.dev/docs/api/latest/nmcli.html)
- [systemd resolvectl](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html)

On macOS, `networksetup -help` and `man networksetup` describe the installed command options.
