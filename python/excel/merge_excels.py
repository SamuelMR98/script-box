#!/usr/bin/env python3

"""
Merge Excels

Merge multiple Excel files into one workbook

Usage:
    python merge_excels.py <output_file.xlsx> <input_file1.xlsx> <input_file2.xlsx> ...
"""

import sys
import pandas as pd

def merge_excels(output_file, input_files):
    """
    Merge multiple Excel files into one workbook.

    Parameters:
        output_file (str): The name of the output Excel file.
        input_files (list): A list of input Excel file names to merge.
    """
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for input_file in input_files:
            try:
                df = pd.read_excel(input_file)
                sheet_name = input_file.split('/')[-1].split('.')[0]  # Use the file name as the sheet name
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Merged '{input_file}' into '{output_file}' as sheet '{sheet_name}'.")
            except Exception as e:
                print(f"Error processing '{input_file}': {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_excels.py <output_file.xlsx> <input_file1.xlsx> <input_file2.xlsx> ...")
        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    merge_excels(output_file, input_files)
    
if __name__ == "__main__":
    main()
