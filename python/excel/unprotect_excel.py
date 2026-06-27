#!/usr/bin/env python3
"""
Remove Excel workbook and/or worksheet protection from .xlsx/.xlsm files.

This does NOT remove "password to open" encryption.
Use only on files you own or are authorized to modify.
"""

import argparse
import re
import tempfile
import zipfile
from pathlib import Path

SHEET_PROTECTION_PATTERNS = [
    r"<sheetProtection\b[^>]*/>",
    r"<sheetProtection\b[^>]*>.*?</sheetProtection>",
]

WORKBOOK_PROTECTION_PATTERNS = [
    r"<workbookProtection\b[^>]*/>",
    r"<workbookProtection\b[^>]*>.*?</workbookProtection>",
]

def remove_patterns_from_file(file_path: Path, patterns: list[str]) -> bool:
    """
    Remove specified XML patterns from a file.

    Args:
        file_path (Path): Path to the XML file.
        patterns (list[str]): List of regex patterns to remove.

    Returns:
        bool: True if any patterns were removed, False otherwise.
    """
    original = file_path.read_text(encoding="utf-8")
    modified = original

    for pattern in patterns:
        modified = re.sub(pattern, "", modified, flags=re.DOTALL)
    
    if modified != original:
        file_path.write_text(modified, encoding="utf-8")
        return True
    return False

def rebuild_excel_file(source_dir: Path, output_file: Path) -> None:
    """
    Rebuild the Excel file from the modified XML files.

    Args:
        source_dir (Path): Directory containing the modified XML files.
        output_file (Path): Path to save the rebuilt Excel file.
    """
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                zout.write(file_path, file_path.relative_to(source_dir))

def unprotect_excel(
        input_path: str,
        output_path: str | None = None,
        mode: str = "both"
) -> Path:
    """
    Remove protection from an Excel file.

    Args:
        input_path (str): Path to the input Excel file.
        output_path (str | None): Path to save the unprotected Excel file. If None, overwrites the input file.
        mode (str): Protection removal mode: "sheet", "workbook", or "both".

    Returns:
        Path: Path to the unprotected Excel file.
    """

    src = Path(input_path)

    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Input file '{input_path}' does not exist or is not a file.")
    
    if src.suffix.lower() not in ['.xlsx', '.xlsm']:
        raise ValueError(f"Input file '{input_path}' is not a valid .xlsx or .xlsm file.")
    
    out = Path(output_path) if output_path else src.with_name(
        f"{src.stem}_unprotected{src.suffix}"
    )

    modified_files = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp = Path(temp_dir)

        with zipfile.ZipFile(src, 'r') as zin:
            zin.extractall(tmp)

        if mode in ["sheet", "both"]:
            worksheet_dir = tmp / "xl" / "worksheets"

            if worksheet_dir.exists():
                for sheet_file in worksheet_dir.glob("*.xml"):
                    if remove_patterns_from_file(sheet_file, SHEET_PROTECTION_PATTERNS):
                        modified_files += 1
        
        if mode in ["workbook", "both"]:
            workbook_file = tmp / "xl" / "workbook.xml"

            if workbook_file.exists():
                if remove_patterns_from_file(workbook_file, WORKBOOK_PROTECTION_PATTERNS):
                    modified_files += 1
        
        if modified_files == 0:
            raise RuntimeError("No protection patterns were found to remove. The file may not be protected.")
        
        rebuild_excel_file(tmp, out)

    print(f"Created: {out}")
    print(f"Removed protection from {modified_files} file(s).")

    return out

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove Excel workbook and/or worksheet protection from .xlsx/.xlsm files."
    )
    parser.add_argument("input", help="Path to the input Excel file (.xlsx or .xlsm).")
    parser.add_argument(
        "-o", "--output", help="Path to save the unprotected Excel file. If not provided, overwrites the input file."
    )
    parser.add_argument(
        "-m", "--mode", choices=["sheet", "workbook", "both"], default="both",
        help="Protection removal mode: 'sheet' for worksheet protection, 'workbook' for workbook protection, or 'both' (default)."
    )

    args = parser.parse_args()

    try:
        unprotect_excel(args.input, args.output, args.mode)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()