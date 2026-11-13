@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem IPv4/IPv6 maintenance utility. Version: 2.0.0
:menu
cls
echo ==================================
echo IP Management - Select an Option
echo ==================================
echo 1. View IPv4 and IPv6 Adapter Settings
echo 2. Enable Automatic Addressing and DNS
echo 3. Release DHCP Lease
echo 4. Renew DHCP Lease
echo 5. Flush DNS Cache
echo 6. Automatic Addressing and DNS Cache Refresh
echo 7. Quick Help
echo 8. Exit
echo ==================================
choice /c 12345678 /n /m "Select an option (1-8): "
set "option=%errorlevel%"
if "%option%"==8 exit /b 0
if "%option%"==7 goto help
if "%option%"==1 goto list
if "%option%"==0 goto menu
if "%option%"==255 goto menu
powershell -NoProfile -Command "if (([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {exit 0} else {exit 1}"
if errorlevel 1 goto admin
if "%option%"==5 goto confirm
choice /c 46 /n /m "Select address family: 4=IPv4, 6=IPv6: "
set "family_choice=%errorlevel%"
set "family="
set "lease_suffix="
if "%family_choice%"==1 set "family=ipv4"
if "%family_choice%"==2 set "family=ipv6"
if "%family_choice%"==2 set "lease_suffix=6"
if not defined family goto menu
netsh interface %family% show interfaces
set "adapter="
set /p "adapter=Enter the exact adapter name: "
rem Validate through the environment, not interpolated PowerShell source.
powershell -NoProfile -Command "if ([string]::IsNullOrWhiteSpace($env:adapter) -or $env:adapter -notmatch '^[\p{L}\p{N} _().-]+$') {exit 1}"
if errorlevel 1 goto invalid
:confirm
echo Network changes may disconnect this computer.
if "%option%"==5 goto confirm_prompt
echo Selected family: %family%
echo Auto/reset enables automatic addressing and selected-family DNS.
if "%family%"==ipv4 echo Static IPv4 configuration may be replaced.
if "%family%"==ipv6 echo IPv6 auto enables router discovery; manual IPv6 addresses/routes remain.
if "%family%"==ipv6 echo Release/renew applies to DHCPv6 leases only, not SLAAC addresses.
echo Reset also clears the shared system DNS cache. Record current settings first.
:confirm_prompt
choice /c YN /n /m "Continue? (Y/N): "
if not errorlevel 1 goto menu
if errorlevel 2 goto menu
if "%option%"==2 goto automatic
if "%option%"==3 goto release
if "%option%"==4 goto renew
if "%option%"==5 goto flush
if "%option%"==6 goto reset
goto menu
:list
ipconfig /all
pause
goto menu
:automatic
call :setauto
if errorlevel 1 goto failed
goto done
:setauto
if "%family%"==ipv6 goto setauto6
netsh interface ipv4 set address name="%adapter%" source=dhcp
if errorlevel 1 exit /b 1
netsh interface ipv4 set dnsservers name="%adapter%" source=dhcp
exit /b %errorlevel%
:setauto6
netsh interface ipv6 set interface interface="%adapter%" routerdiscovery=enabled store=persistent
if errorlevel 1 exit /b 1
netsh interface ipv6 set dnsservers name="%adapter%" source=dhcp
exit /b %errorlevel%
:release
ipconfig /release%lease_suffix% "%adapter%"
if errorlevel 1 goto failed
goto done
:renew
ipconfig /renew%lease_suffix% "%adapter%"
if errorlevel 1 goto failed
goto done
:flush
ipconfig /flushdns
if errorlevel 1 goto failed
goto done
:reset
call :setauto
if errorlevel 1 goto failed
rem IPv6 may use SLAAC without DHCPv6: skip the DHCP lease cycle.
if "%family%"==ipv6 goto flush
ipconfig /release%lease_suffix% "%adapter%"
if errorlevel 1 goto failed
ipconfig /renew%lease_suffix% "%adapter%"
if errorlevel 1 goto failed
ipconfig /flushdns
if errorlevel 1 goto failed
goto done
:help
echo Start with option 1 to find your exact adapter name.
echo Options 2-6 require Run as administrator.
echo Choose IPv4 or IPv6 explicitly for address changes.
echo IPv6 automatic addressing uses router discovery; existing manual IPv6 addresses remain.
echo IPv6 release/renew is for DHCPv6 only and does not refresh SLAAC addresses.
echo Record current settings first. Use a local terminal to avoid losing remote access.
echo Reset affects the selected adapter; DNS cache flush is system-wide.
echo For command previews, use the Python version with --dry-run.
echo See README.md for examples, platform differences, and limitations.
pause
goto menu
:admin
echo Reopen this script with Run as administrator to change settings.
pause
goto menu
:invalid
echo Invalid adapter name. Use the Python version for unusual characters.
pause
goto menu
:failed
echo A command failed. Stopped; earlier changes may remain. No rollback.
pause
goto menu
:done
echo Commands completed. Check your network connection.
pause
goto menu
