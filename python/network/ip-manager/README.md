# IP Network Manager

IPv4 and IPv6 maintenance for Windows, macOS, and Linux with NetworkManager.
Python 3.9+; standard library only. Version **2.0.0**.

## Files and placement

Place this folder at `networking/ip-manager/` in your scripts collection. Keep
`network_manager.py`, `network_manager.bat`, `README.md`, and `tests/` together.
The batch script is a standalone Windows alternative; it does not require Python.
Use the collection's root license and contribution policy.

Suggested root README entry:

```markdown
| [IP Network Manager](networking/ip-manager/) | IPv4/IPv6 automatic addressing, DHCP leases, and DNS cache maintenance | Windows, macOS, Linux (NetworkManager) |
```

## Requirements

- Python version: Python 3.9 or newer; no pip packages required.
- Windows: ipconfig, netsh; batch also requires Windows PowerShell.
- macOS: networksetup, ifconfig, dscacheutil, killall.
- Linux: nmcli and running NetworkManager for addressing/listing; resolvectl and
  running systemd-resolved for flush/reset.
- Administrator terminal or sudo for real changes. Listing, help, and previews
  need no elevation. The scripts do not elevate themselves.

## Quick start

From the repository root:

```sh
cd networking/ip-manager
python3 network_manager.py --dry-run
```

The menu asks for `ipv4` or `ipv6` before addressing changes. No family is selected
implicitly. Menu: 1 List, 2 Auto, 3 Release, 4 Renew, 5 Flush, 6 Reset, 7 Help, 8 Exit.
Release/renew is implemented only for Windows DHCP leases.

Without an action argument, Python opens the menu. Omit `--dry-run` to execute.
Real changes require typing `YES`; declining a one-shot action exits with code 130.
Commands stop at the first failure. Earlier successful changes can remain.

On Windows, replace `python3` with `py -3`. Alternatively, run
`network_manager.bat` with **Run as administrator** for modifications. It asks you
to select 4 or 6 for each addressing action and confirm Y/N. Batch has no preview
mode; use Python for previews.

## Examples

Run from this directory. Replace adapter/service names and UUIDs with yours.

```sh
# Shared operations: no --family or --target accepted
python3 network_manager.py list
python3 network_manager.py flush --dry-run

# Windows, in an Administrator terminal for actual changes
py -3 network_manager.py auto --family ipv4 --target "Wi-Fi" --dry-run
py -3 network_manager.py auto --family ipv6 --target "Wi-Fi" --dry-run
py -3 network_manager.py renew --family ipv6 --target "Wi-Fi" --dry-run

# macOS: use service names such as Wi-Fi, not device names such as en0
sudo python3 network_manager.py auto --family ipv6 --target "Wi-Fi"

# Linux: replace CONNECTION-UUID with the UUID from list
sudo python3 network_manager.py auto --family ipv6 --target "CONNECTION-UUID"
python3 network_manager.py reset --family ipv4 --target "CONNECTION-UUID" --dry-run

python3 network_manager.py help
python3 network_manager.py --help
python3 network_manager.py --version
```

One-shot addressing actions require both `--family` and `--target` and fail before
prompting if either is absent. For the interactive menu, those flags optionally
preselect the family/target; they do not filter List or Flush.

## Addressing behavior

IPv6 automatic addressing is not simply DHCPv6. It can use router advertisements,
SLAAC and DHCPv6, depending on the network and OS. DHCPv6 lease operations do not
release or renew SLAAC addresses, nor do they disable IPv6 or remove link-local
addresses. No global IPv6 address is guaranteed without network support.

| Action | Windows | macOS | Linux / NetworkManager |
|---|---|---|---|
| List | Shows both families via ipconfig | Shows ports/services and addresses via ifconfig | Shows profiles/devices and both families |
| Auto IPv4 | DHCP address + automatic IPv4 DNS | Reapplies DHCP; preserves service DNS | Clears manual IPv4 addresses/gateway/DNS, sets method auto, activates profile |
| Auto IPv6 | Enables router discovery + automatic IPv6 DNS; retains manual IPv6 addresses/routes | Sets IPv6 automatic; preserves service DNS | Clears manual IPv6 addresses/gateway/DNS, sets method auto, activates profile |
| Release/renew IPv4 | DHCP lease operation on selected adapter | Unsupported | Unsupported |
| Release/renew IPv6 | /release6 or /renew6: DHCPv6 only | Unsupported | Unsupported |
| Flush | Shared DNS cache | Shared DNS cache | systemd-resolved cache |
| Reset IPv4 | Auto + release + renew + shared DNS flush | Auto + shared DNS flush | Auto/profile activation + shared DNS flush |
| Reset IPv6 | Auto + shared DNS flush; no forced DHCPv6 lease cycle | Auto + shared DNS flush | Auto/profile activation + shared DNS flush |

### Scope and limitations

- Auto/reset may replace selected-family static settings. Record existing settings
  first. There is no automatic backup or rollback. Use a local console: changes
  can disconnect SSH or remote desktop.
- Windows IPv6 auto/reset enables router discovery, letting router advertisements
  guide automatic configuration. It deliberately retains manual IPv6 addresses
  and routes. It is not a complete conversion of a static IPv6 setup and does not
  re-enable IPv6 if disabled at the OS/adapter-binding level.
- macOS DNS servers are shared at the network-service level. Auto/reset preserves
  them to avoid clearing the other family's DNS configuration. Flush clears only
  cached answers, not configured servers.
- Linux edits only the chosen family's profile properties. Activation applies the
  entire profile and can interrupt both families. Existing settings for the other
  family are not edited. A failed activation can leave the saved profile changed.
- Linux down/up is no longer presented as release/renew because it affects both
  families. This tool intentionally rejects those actions on Linux and macOS.
- DNS cache flushing is system-wide. DNS servers reachable over IPv4 or IPv6 can
  answer both A and AAAA queries; address families are not separate DNS namespaces.
- No dnsmasq, nscd, browser, or upstream DNS caches are flushed. Linux systems
  using another network manager are unsupported for addressing operations.
- Custom routes, search domains, client IDs and advanced policy are not reset.
  Router/VPN/company policy can affect results. A successful command is not proof
  of Internet connectivity or of obtaining a new address.
- Python checks executables before running any commands. A running-service failure
  can still occur after preceding commands have changed settings.
- Targets must be exact names/UUIDs, without wildcards. Batch accepts a conservative
  set of name characters; Python supports additional characters without shell expansion.

## Changes from 1.x

- Folder renamed from `ipv4-manager` to `ip-manager`.
- `auto` replaces the IPv4-only `dhcp` action. Update calls to include an explicit
  `--family ipv4` or `--family ipv6` and target.
- List shows both families and Flush is shared. No `both` mutation mode exists.
- macOS no longer clears shared DNS or labels reapplying DHCP as lease renewal.
- Linux no longer labels whole-profile deactivation/activation as family-specific
  release/renew. Use Auto or Reset when you intend to reconfigure a family.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Tests use mocked execution and cover family selection, selected-family settings,
Windows DHCPv6 vs SLAAC behavior, macOS DNS preservation, unsupported lease actions,
CLI validation, menu navigation, cancellation, dry-run and failure boundaries.
Syntax and previews are checked on Linux. No actual network settings were changed.
Windows batch was inspected, not executed. Live Windows/macOS/Linux operations
still require validation on destination machines.

## References

- [Microsoft ipconfig](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)
- [Microsoft netsh interface](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-interface)
- [Apple networksetup](https://support.apple.com/en-ng/guide/remote-desktop/apdd0c5a2d5/mac)
- [NetworkManager IPv6 settings](https://networkmanager.dev/docs/api/latest/settings-ipv6.html)
- [NetworkManager nmcli](https://networkmanager.dev/docs/api/latest/nmcli.html)
- [systemd resolvectl](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html)

On a Mac, `networksetup -help` and `man networksetup` document the installed IPv6
options, including `-setv6automatic`.
