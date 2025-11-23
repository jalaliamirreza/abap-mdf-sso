#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV to DBF Converter
تبدیل فایل CSV به DBF برای سازمان تامین اجتماعی

Usage:
    python csv_to_dbf.py workers.csv --workshop-id 1234567890 --year 3 --month 9

CSV Format:
    - First row: column headers
    - Columns must match DBF field names
    - Persian text will be automatically encoded
"""

import csv
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.iran_system_encoding import IranSystemEncoder
import struct


class CSVtoDBFConverter:
    """Convert CSV files to DBF format for Iranian Social Security"""

    def __init__(self):
        self.encoder = IranSystemEncoder()

    def read_csv(self, csv_file: str) -> list:
        """Read CSV file and return list of dictionaries"""
        print(f"📂 Reading CSV: {csv_file}")

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        print(f"✅ Loaded {len(data)} records")
        return data

    def create_dbf_binary(self, output_file: str, records: list,
                          workshop_id: str, year: int, month: int):
        """
        Create DBF file using binary writing with Iran System encoding

        This creates a dBase III format file with raw byte writing
        to support custom Iran System encoding for Persian text.
        """

        print("=" * 80)
        print("🔨 Creating DBF file with binary writing")
        print("=" * 80)

        # DBF structure - dskwor00.dbf (31 fields)
        fields = [
            ('DSW_ID', 'C', 10, 0),
            ('DSW_YY', 'N', 2, 0),
            ('DSW_MM', 'N', 2, 0),
            ('DSW_LISTNO', 'C', 12, 0),
            ('DSW_ID1', 'C', 8, 0),
            ('DSW_FNAME', 'C', 20, 0),
            ('DSW_LNAME', 'C', 25, 0),
            ('DSW_DNAME', 'C', 20, 0),
            ('DSW_IDNO', 'C', 15, 0),
            ('DSW_IDPLC', 'C', 30, 0),
            ('DSW_IDATE', 'C', 8, 0),
            ('DSW_BDATE', 'C', 8, 0),
            ('DSW_SEX', 'C', 3, 0),
            ('DSW_NAT', 'C', 10, 0),
            ('DSW_OCP', 'C', 50, 0),
            ('DSW_SDATE', 'C', 8, 0),
            ('DSW_EDATE', 'C', 8, 0),
            ('DSW_DD', 'N', 2, 0),
            ('DSW_ROOZ', 'N', 12, 0),
            ('DSW_MAH', 'N', 12, 0),
            ('DSW_MAZ', 'N', 12, 0),
            ('DSW_MASH', 'N', 12, 0),
            ('DSW_TOTL', 'N', 12, 0),
            ('DSW_BIME', 'N', 12, 0),
            ('DSW_PRATE', 'N', 2, 0),
            ('DSW_KOSO', 'N', 12, 0),
            ('DSW_BIME20', 'N', 12, 0),
            ('PER_NATCOD', 'C', 10, 0),
            ('DSW_JOB', 'C', 10, 0),
            ('DSW_INC', 'N', 19, 0),
            ('DSW_SPOUSE', 'N', 19, 0),
        ]

        # Calculate record length
        record_length = 1  # Deletion flag
        for field in fields:
            record_length += field[2]

        print(f"Record length: {record_length} bytes")
        print(f"Number of records: {len(records)}")
        print()

        with open(output_file, 'wb') as f:
            # Write DBF header
            self._write_header(f, len(records), record_length, fields)

            # Write records
            for i, record in enumerate(records, 1):
                print(f"Writing record {i}/{len(records)}: {record.get('DSW_FNAME', '')} {record.get('DSW_LNAME', '')}")
                self._write_record(f, record, fields, workshop_id, year, month)

            # Write end-of-file marker
            f.write(b'\x1A')

        print()
        print(f"✅ DBF file created: {output_file}")
        print("=" * 80)

    def _write_header(self, f, num_records: int, record_length: int, fields: list):
        """Write DBF header"""
        from datetime import datetime

        now = datetime.now()

        # Header (32 bytes)
        header = struct.pack('<B', 0x03)  # dBase III
        header += struct.pack('<BBB', now.year % 100, now.month, now.day)
        header += struct.pack('<I', num_records)
        header += struct.pack('<H', 32 + len(fields) * 32 + 1)  # Header size
        header += struct.pack('<H', record_length)
        header += bytes(20)  # Reserved

        f.write(header)

        # Field descriptors (32 bytes each)
        for field_name, field_type, field_length, field_decimal in fields:
            field_desc = field_name.ljust(11, '\x00').encode('ascii')
            field_desc += field_type.encode('ascii')
            field_desc += bytes(4)  # Reserved
            field_desc += struct.pack('<B', field_length)
            field_desc += struct.pack('<B', field_decimal)
            field_desc += bytes(14)  # Reserved
            f.write(field_desc)

        # Header terminator
        f.write(b'\x0D')

    def _write_record(self, f, record: dict, fields: list,
                     workshop_id: str, year: int, month: int):
        """Write a single DBF record"""

        # Deletion flag
        f.write(b' ')

        # Persian field names that need Iran System encoding
        persian_fields = {'DSW_FNAME', 'DSW_LNAME', 'DSW_DNAME', 'DSW_IDPLC', 'DSW_OCP'}

        for field_name, field_type, field_length, field_decimal in fields:
            # Get value from record or use default
            if field_name == 'DSW_ID':
                value = workshop_id
            elif field_name == 'DSW_YY':
                value = year
            elif field_name == 'DSW_MM':
                value = month
            else:
                value = record.get(field_name, '')

            # Format based on type
            if field_type == 'C':
                # Character field
                if field_name in persian_fields and value and str(value).strip():
                    # Use Iran System encoding for Persian text
                    encoded = self.encoder.unicode_to_iran_system(str(value).strip())
                    # Pad or truncate to field length
                    if len(encoded) > field_length:
                        encoded = encoded[:field_length]
                    else:
                        encoded = encoded + (b' ' * (field_length - len(encoded)))
                    f.write(encoded)
                else:
                    # Regular ASCII/Latin text
                    text = str(value)[:field_length].ljust(field_length)
                    f.write(text.encode('ascii', errors='replace'))

            elif field_type == 'N':
                # Numeric field
                try:
                    if field_decimal > 0:
                        num_str = f"{float(value):{field_length}.{field_decimal}f}"
                    else:
                        num_str = f"{int(float(value) if value else 0):>{field_length}d}"
                except:
                    num_str = ' ' * field_length

                f.write(num_str[:field_length].rjust(field_length).encode('ascii'))


def main():
    parser = argparse.ArgumentParser(
        description='Convert CSV to DBF format for Iranian Social Security'
    )
    parser.add_argument('workers_csv', help='Workers CSV file')
    parser.add_argument('--workshop-id', required=True, help='Workshop ID (10 chars)')
    parser.add_argument('--year', type=int, required=True, help='Year (2 digits, e.g., 3 for 1403)')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--output', default='dskwor00.dbf', help='Output DBF filename')

    args = parser.parse_args()

    # Create converter
    converter = CSVtoDBFConverter()

    # Read CSV
    records = converter.read_csv(args.workers_csv)

    # Convert to DBF
    converter.create_dbf_binary(
        args.output,
        records,
        args.workshop_id,
        args.year,
        args.month
    )

    print(f"\n✅ Conversion complete!")
    print(f"📄 Output: {args.output}")


if __name__ == '__main__':
    main()
