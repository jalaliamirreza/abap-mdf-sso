#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Encoding Checker
بررسی‌کننده encoding و کاراکترهای مشکل‌ساز در CSV

This tool checks CSV files for problematic characters like Persian commas
that could cause issues when converting to DBF.
"""

import sys
import csv
from pathlib import Path


def check_csv_file(csv_file: str):
    """Check CSV file for encoding issues"""

    print("=" * 80)
    print(f"Checking: {csv_file}")
    print("=" * 80)

    # Read raw content
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Characters to check
    persian_comma = '\u060C'  # ،
    english_comma = ','
    arabic_semicolon = '\u061B'  # ؛

    # Count characters
    persian_comma_count = content.count(persian_comma)
    english_comma_count = content.count(english_comma)
    arabic_semicolon_count = content.count(arabic_semicolon)

    print(f"\n📊 Character counts:")
    print(f"  English comma (,):     {english_comma_count}")
    print(f"  Persian comma (،):     {persian_comma_count}")
    print(f"  Arabic semicolon (؛):  {arabic_semicolon_count}")

    # Check for issues
    issues = []

    if persian_comma_count > 0:
        issues.append(f"Found {persian_comma_count} Persian commas (،)")

    if arabic_semicolon_count > 0:
        issues.append(f"Found {arabic_semicolon_count} Arabic semicolons (؛)")

    # Check each line
    lines = content.split('\n')

    if persian_comma_count > 0 or arabic_semicolon_count > 0:
        print(f"\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")

        print(f"\n📝 Problematic lines:")
        for i, line in enumerate(lines, 1):
            if persian_comma in line or arabic_semicolon in line:
                print(f"  Line {i}:")
                print(f"    {line[:100]}")

                # Show character positions
                for j, char in enumerate(line):
                    if char == persian_comma:
                        print(f"      Position {j}: Persian comma (،) at column")
                    elif char == arabic_semicolon:
                        print(f"      Position {j}: Arabic semicolon (؛)")

                if i > 10:
                    print(f"  ... (showing first 10 lines only)")
                    break
    else:
        print(f"\n✅ No problematic characters found!")

    # Try to parse as CSV
    print(f"\n📋 CSV structure check:")
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)

            print(f"  Columns: {len(header)}")
            print(f"  Header fields:")
            for i, field in enumerate(header, 1):
                # Check if field name has Persian comma
                if persian_comma in field:
                    print(f"    {i:2d}. {field} ⚠️  (contains Persian comma!)")
                else:
                    print(f"    {i:2d}. {field}")

            # Check first data row
            try:
                first_row = next(reader)
                print(f"\n  First data row has {len(first_row)} fields")
                if len(first_row) != len(header):
                    print(f"  ⚠️  WARNING: Field count mismatch! Header has {len(header)}, row has {len(first_row)}")
            except StopIteration:
                print(f"  (No data rows)")

    except Exception as e:
        print(f"  ❌ Error parsing CSV: {e}")

    print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_csv_encoding.py <csv_file>")
        print("\nExample:")
        print("  python tools/check_csv_encoding.py header.csv")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        sys.exit(1)

    check_csv_file(csv_file)


if __name__ == '__main__':
    main()
