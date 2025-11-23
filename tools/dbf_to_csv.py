#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF to CSV Converter with Iran System Decoder
تبدیل فایل DBF به CSV با دیکدر Iran System

Usage:
    # Convert DBF to CSV with Persian text decoded
    python dbf_to_csv.py dskwor00.dbf --output workers.csv

    # Include hex representation alongside decoded text
    python dbf_to_csv.py dskwor00.dbf --output workers.csv --include-hex

    # Only show hex (no decoding)
    python dbf_to_csv.py dskwor00.dbf --output workers.csv --include-hex --no-decode

Features:
    - Decodes Iran System encoded Persian text to Unicode
    - Supports all Persian letters with context-sensitive forms
    - Optional hex output for verification
"""

import csv
import argparse
import sys
from pathlib import Path
from dbfread import DBF

# Add parent directory to path to import local modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.iran_system_decoder import IranSystemDecoder


class DBFtoCSVConverter:
    """Convert DBF files to CSV format with Iran System decoding"""

    def __init__(self, include_persian_hex: bool = False, decode_persian: bool = True):
        """
        Initialize converter

        Args:
            include_persian_hex: If True, include Persian fields as hex strings
            decode_persian: If True, decode Persian text using Iran System decoder
        """
        self.include_persian_hex = include_persian_hex
        self.decode_persian = decode_persian
        self.decoder = IranSystemDecoder()

    def convert(self, dbf_file: str, output_csv: str):
        """
        Convert DBF to CSV

        Args:
            dbf_file: Input DBF file path
            output_csv: Output CSV file path
        """
        print("=" * 80)
        print("📂 Converting DBF to CSV")
        print("=" * 80)
        print(f"Input:  {dbf_file}")
        print(f"Output: {output_csv}")
        print()

        # Persian field names (fields using Iran System encoding)
        persian_fields = {
            'DSW_FNAME',    # First name
            'DSW_LNAME',    # Last name
            'DSW_DNAME',    # Father's name
            'DSW_IDPLC',    # ID place
            'DSW_OCP',      # Occupation
            'DSW_SEX',      # Sex (مرد/زن)
            'DSW_NAT',      # Nationality (ایرانی)
            # Note: DSW_JOB is a numeric job code, not Persian text
            'DSK_NAME',     # Workshop name (in header file)
            'DSK_FARM',     # Manager name (in header file)
            'DSK_ADRS',     # Address (in header file)
            'DSK_DISC',     # Description (in header file)
        }

        # Open DBF with latin-1 to preserve raw bytes
        db = DBF(dbf_file, encoding='latin-1', char_decode_errors='ignore')
        records = list(db)

        print(f"Total records: {len(records)}")
        print()

        if len(records) == 0:
            print("⚠️  No records found in DBF file")
            return

        # Get field names from first record
        field_names = list(records[0].keys())

        # Prepare output records
        output_records = []

        for i, record in enumerate(records, 1):
            output_record = {}

            for field_name in field_names:
                value = record.get(field_name)

                if field_name in persian_fields:
                    # Persian field - decode using Iran System decoder
                    if value:
                        if isinstance(value, str):
                            raw_bytes = value.encode('latin-1').rstrip(b' \x00')
                        elif isinstance(value, bytes):
                            raw_bytes = value.rstrip(b' \x00')
                        else:
                            raw_bytes = b''

                        # Decode to Unicode if enabled
                        if self.decode_persian:
                            decoded_text = self.decoder.decode(raw_bytes)
                            output_record[field_name] = decoded_text
                        else:
                            output_record[field_name] = ''

                        # Include hex if requested
                        if self.include_persian_hex:
                            output_record[field_name + '_HEX'] = raw_bytes.hex()
                    else:
                        output_record[field_name] = ''
                        if self.include_persian_hex:
                            output_record[field_name + '_HEX'] = ''
                else:
                    # Non-Persian field - copy as-is
                    if isinstance(value, str):
                        output_record[field_name] = value.strip()
                    elif isinstance(value, (int, float)):
                        output_record[field_name] = value
                    else:
                        output_record[field_name] = str(value) if value else ''

            output_records.append(output_record)

        # Write CSV
        if output_records:
            with open(output_csv, 'w', encoding='utf-8', newline='') as f:
                # Get all field names (including _HEX fields if present)
                all_fields = []
                for field in field_names:
                    all_fields.append(field)
                    if self.include_persian_hex and field in persian_fields:
                        all_fields.append(field + '_HEX')

                writer = csv.DictWriter(f, fieldnames=all_fields)
                writer.writeheader()
                writer.writerows(output_records)

        print(f"✅ Converted {len(output_records)} records")
        print(f"📄 Output: {output_csv}")
        print("=" * 80)

        # Show sample
        if len(output_records) > 0:
            print()
            print("📋 Sample (first record):")
            print("-" * 80)
            for key, value in list(output_records[0].items())[:10]:
                print(f"  {key:<20}: {value}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Convert DBF to CSV format with Iran System decoding'
    )
    parser.add_argument('dbf_file', help='Input DBF file')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file')
    parser.add_argument('--include-hex', action='store_true',
                       help='Include Persian fields as hex strings (in addition to decoded text)')
    parser.add_argument('--no-decode', action='store_true',
                       help='Disable Persian text decoding (only show hex if --include-hex is used)')

    args = parser.parse_args()

    # Create converter
    converter = DBFtoCSVConverter(
        include_persian_hex=args.include_hex,
        decode_persian=not args.no_decode
    )

    # Convert
    converter.convert(args.dbf_file, args.output)

    print("✅ Conversion complete!")


if __name__ == '__main__':
    main()
