# 📦 Script Box

A curated collection of reusable scripts, utilities, and automation tools for developers, system administrators, cybersecurity enthusiasts, and power users.

The goal of this repository is to serve as a personal toolbox of scripts that solve common problems, automate repetitive tasks, and provide useful utilities across multiple programming languages and platforms.

> **Work smarter. Script it once. Reuse it forever.**

---

Each directory contains scripts grouped by language and purpose.

---

## Categories

### 🐍 Python

General-purpose scripts for:

* Excel automation
* File management
* Network utilities
* Automation
* OSINT
* Data processing
* Miscellaneous utilities

---

### 🐹 Go

CLI tools and high-performance utilities.

Examples:

* Network scanners
* API clients
* OSINT tools
* Log parsers

---

### 🐚 Bash

Linux/macOS shell scripts.

Examples:

* Server setup
* Docker helpers
* Backup scripts
* Git utilities

---

### 💙 PowerShell

Windows automation.

Examples:

* Active Directory
* Windows administration
* Office automation
* System maintenance

---

## Usage

Most scripts can be executed directly.

Example:

```bash
python python/excel/unprotect_excel.py workbook.xlsx
```

Some scripts may require dependencies.

Install them with:

```bash
pip install -r requirements.txt
```

or install the dependencies listed in the individual script documentation.

---

## Philosophy

Scripts in this repository should strive to be:

* Small and focused
* Well documented
* Cross-platform when possible
* Safe by default
* Easy to modify
* Easy to reuse

Each script should solve one problem well.

---

## Contributing

If you're contributing to this repository, please follow these guidelines:

* Keep scripts self-contained whenever possible.
* Include comments for non-obvious logic.
* Add usage examples.
* Document required dependencies.
* Follow consistent naming conventions.
* Update documentation when adding new scripts.

---

## Naming Convention

Use descriptive filenames.

Examples:

```text
unprotect_excel.py
bulk_rename.py
extract_metadata.py
network_scan.go
backup_home.sh
cleanup_logs.ps1
```

Avoid names like:

```text
script.py
test.py
temp.py
```

---

## License

This repository is licensed under the MIT License.

See the `LICENSE` file for details.

---

## Disclaimer

These scripts are provided as-is without warranty.

Some utilities may modify files or system settings. Always review the code before running it and test on backups when appropriate.

Use these scripts only on systems and data you own or are authorized to manage.
