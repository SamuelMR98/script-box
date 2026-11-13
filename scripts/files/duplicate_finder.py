#!/usr/bin/env python3

"""
Duplicate Finder

Finds duplicate files using hashes and optionally deletes them.
Use only on files you own or are authorized to modify.
"""

from pathlib import Path
import hashlib
import argparse

def compute_hash(file_path, hash_algorithm):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = getattr(hashlib, hash_algorithm)()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def find_duplicates(directory, hash_algorithm):
    """Find duplicate files in the specified directory."""
    hash_map = {}
    duplicates = []

    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            file_hash = compute_hash(file_path, hash_algorithm)
            if file_hash in hash_map:
                duplicates.append((file_path, hash_map[file_hash]))
            else:
                hash_map[file_hash] = file_path

    return duplicates

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", type=str, help="Directory to search for duplicates.")
    parser.add_argument("--hash", type=str, default="md5", choices=hashlib.algorithms_available,
                        help="Hash algorithm to use (default: md5).")
    args = parser.parse_args()

    duplicates = find_duplicates(args.directory, args.hash)

    if duplicates:
        print("Duplicate files found:")
        for dup in duplicates:
            print(f"{dup[0]} and {dup[1]}")
    else:
        print("No duplicate files found.")

if __name__ == "__main__":
    main()
