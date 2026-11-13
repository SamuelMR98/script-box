#!/usr/bin/env python3

"""
Excel to CSV Converter

Convert .xlsx sheets into CSV files

Usage:
    python excel_to_csv.py <input_file.xlsx> <output_file.csv>
"""

import sys
import pandas as pd

def excel_to_csv(input_file, output_file):
    """
    Convert an Excel file to a CSV file.

    Parameters:
        input_file (str): The name of the input Excel file.
        output_file (str): The name of the output CSV file.
    """
    try:
        df = pd.read_excel(input_file)
        df.to_csv(output_file, index=False)
        print(f"Converted '{input_file}' to '{output_file}'.")
    except Exception as e:
        print(f"Error converting '{input_file}' to CSV: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python excel_to_csv.py <input_file.xlsx> <output_file.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    excel_to_csv(input_file, output_file)

if __name__ == "__main__":
    main()