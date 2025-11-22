#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF File Inspector
بررسی‌کننده ساختار فایل DBF

This script analyzes a DBF file and shows its complete structure.
"""

import sys
import os
from pathlib import Path

try:
    from dbfpy3 import dbf
except ImportError:
    print("Error: dbfpy3 is not installed.")
    print("Install it using: pip install dbfpy3")
    sys.exit(1)


def inspect_dbf(dbf_file_path: str):
    """
    Inspect and display DBF file structure and data

    Args:
        dbf_file_path: Path to DBF file
    """
    if not os.path.exists(dbf_file_path):
        print(f"❌ Error: File not found: {dbf_file_path}")
        return

    print("=" * 80)
    print(f"📁 DBF File Inspector")
    print("=" * 80)
    print(f"File: {dbf_file_path}")
    print(f"Size: {os.path.getsize(dbf_file_path):,} bytes")
    print()

    try:
        # Open DBF file
        db = dbf.Dbf(dbf_file_path, readOnly=True)

        # File information
        print("📊 File Information:")
        print("-" * 80)
        print(f"Total Records: {len(db)}")
        print(f"Total Fields: {len(db.header.fields)}")
        print(f"Last Update: {db.header.year}/{db.header.month:02d}/{db.header.day:02d}")
        print()

        # Field structure
        print("📋 Field Structure:")
        print("-" * 80)
        print(f"{'#':<4} {'Field Name':<15} {'Type':<6} {'Length':<8} {'Decimals':<9} {'Description'}")
        print("-" * 80)

        for i, field in enumerate(db.header.fields, 1):
            field_type_map = {
                'C': 'Char',
                'N': 'Number',
                'D': 'Date',
                'L': 'Logical',
                'M': 'Memo',
                'F': 'Float'
            }
            field_type = field_type_map.get(field.type, field.type)

            print(f"{i:<4} {field.name:<15} {field_type:<6} {field.length:<8} "
                  f"{field.decimalCount if hasattr(field, 'decimalCount') else 0:<9}")

        print()

        # Sample data (first 5 records)
        print("📝 Sample Data (First 5 Records):")
        print("-" * 80)

        sample_size = min(5, len(db))
        for i, record in enumerate(db):
            if i >= sample_size:
                break

            print(f"\nRecord #{i+1}:")
            print("-" * 40)
            for field in db.header.fields:
                value = record[field.name]

                # Handle different types
                if isinstance(value, bytes):
                    try:
                        # Try Windows-1256 (Persian)
                        value = value.decode('windows-1256').strip()
                    except:
                        try:
                            # Try UTF-8
                            value = value.decode('utf-8').strip()
                        except:
                            value = str(value)
                elif isinstance(value, str):
                    value = value.strip()

                print(f"  {field.name:<15}: {value}")

        print()

        # Statistics
        print("📈 Field Statistics:")
        print("-" * 80)

        # Check for empty/null values
        for field in db.header.fields:
            empty_count = 0
            non_empty_count = 0

            for record in db:
                value = record[field.name]
                if value is None or (isinstance(value, str) and not value.strip()):
                    empty_count += 1
                else:
                    non_empty_count += 1

            fill_rate = (non_empty_count / len(db) * 100) if len(db) > 0 else 0
            print(f"  {field.name:<15}: {non_empty_count:>4} filled, {empty_count:>4} empty ({fill_rate:.1f}% fill rate)")

        print()

        # Generate Python code for field structure
        print("🐍 Python Field Definition:")
        print("-" * 80)
        print("DBF_STRUCTURE = [")
        for field in db.header.fields:
            decimals = field.decimalCount if hasattr(field, 'decimalCount') else 0
            if decimals > 0:
                print(f"    ('{field.name}', '{field.type}', {field.length}, {decimals}),")
            else:
                print(f"    ('{field.name}', '{field.type}', {field.length}),")
        print("]")
        print()

        # Generate JSON mapping
        print("📄 JSON Field Mapping Template:")
        print("-" * 80)
        print("{")
        for i, field in enumerate(db.header.fields):
            comma = "," if i < len(db.header.fields) - 1 else ""
            print(f'  "{field.name}": ""  # {field.type}({field.length}){comma}')
        print("}")
        print()

        # Close database
        db.close()

        print("✅ Inspection completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error reading DBF file: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python inspect_dbf.py <dbf_file_path>")
        print("\nExample:")
        print("  python inspect_dbf.py sample.dbf")
        sys.exit(1)

    dbf_file = sys.argv[1]
    inspect_dbf(dbf_file)


if __name__ == '__main__':
    main()
