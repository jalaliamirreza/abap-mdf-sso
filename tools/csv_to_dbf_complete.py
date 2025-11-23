#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete CSV to DBF Converter
تبدیل کامل CSV به DBF (هر دو فایل header و workers)

Usage:
    python csv_to_dbf_complete.py header.csv workers.csv \
        --workshop-id "1234567890" --year 3 --month 9 \
        --output-dir output
"""

import csv
import sys
import argparse
from pathlib import Path
import struct

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.iran_system_encoding import IranSystemEncoder


class CompleteDBFConverter:
    """Convert CSV files to complete DBF set (header + workers)"""

    def __init__(self):
        self.encoder = IranSystemEncoder()

    def read_csv(self, csv_file: str) -> list:
        """Read CSV file and return list of dictionaries"""
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def create_header_file(self, output_file: str, header_data: dict,
                          workers_data: list, year: int, month: int):
        """
        Create dskkar00.dbf (header file with summary data)

        Args:
            output_file: Output DBF filename
            header_data: Dictionary with header information
            workers_data: List of worker records (for calculating totals)
            year: Year (2 digits)
            month: Month (1-12)
        """
        print("=" * 80)
        print("🔨 Creating Header File (dskkar00.dbf)")
        print("=" * 80)

        # Header file structure - NEW SSO 2024 FORMAT (25 fields)
        # ⚠️  DSK_TBIM20 REMOVED in new structure!
        fields = [
            ('DSK_ID', 'C', 10, 0),       # Workshop ID
            ('DSK_NAME', 'C', 30, 0),     # Workshop name (Persian) - Changed: 100→30
            ('DSK_FARM', 'C', 30, 0),     # Employer name (Persian) - Changed: 100→30
            ('DSK_ADRS', 'C', 40, 0),     # Address (Persian) - Changed: 100→40
            ('DSK_KIND', 'N', 1, 0),      # Kind
            ('DSK_YY', 'N', 2, 0),        # Year
            ('DSK_MM', 'N', 2, 0),        # Month
            ('DSK_LISTNO', 'C', 12, 0),   # List number
            ('DSK_DISC', 'C', 30, 0),     # Description (Persian) - Changed: 100→30
            ('DSK_NUM', 'N', 5, 0),       # Number of workers
            ('DSK_TDD', 'N', 6, 0),       # Total days
            ('DSK_TROOZ', 'N', 12, 0),    # Total daily wage
            ('DSK_TMAH', 'N', 12, 0),     # Total monthly wage - Changed: 13→12
            ('DSK_TMAZ', 'N', 12, 0),     # Total benefits
            ('DSK_TMASH', 'N', 12, 0),    # Total insurable
            ('DSK_TTOTL', 'N', 12, 0),    # Total amount - Changed: 13→12
            ('DSK_TBIME', 'N', 12, 0),    # Total insurance
            ('DSK_TKOSO', 'N', 12, 0),    # Total deductions
            ('DSK_BIC', 'N', 12, 0),      # Unknown
            ('DSK_RATE', 'N', 5, 0),      # Rate
            ('DSK_PRATE', 'N', 2, 0),     # Rate percentage
            # DSK_TBIM20 DELETED in new structure!
            ('DSK_BIMH', 'N', 12, 0),     # Insurance premium
            ('MON_PYM', 'C', 3, 0),       # Payment month
            ('DSK_INC', 'N', 12, 0),      # Income - Changed: 19→12
            ('DSK_SPOUSE', 'N', 12, 0),   # Spouse income - Changed: 19→12
        ]

        # Calculate totals from workers data
        totals = self._calculate_totals(workers_data)

        # Calculate record length
        record_length = 1  # Deletion flag
        for field in fields:
            record_length += field[2]

        print(f"Record length: {record_length} bytes")
        print(f"Number of workers: {totals['num_workers']}")
        print()

        with open(output_file, 'wb') as f:
            # Write header
            self._write_dbf_header(f, 1, record_length, fields)  # Only 1 record in header file

            # Write single record
            self._write_header_record(f, header_data, totals, fields, year, month)

            # End of file marker
            f.write(b'\x1A')

        print(f"✅ Header file created: {output_file}")
        print("=" * 80)
        print()

    def create_workers_file(self, output_file: str, workers_data: list,
                           workshop_id: str, year: int, month: int, list_no: str = ""):
        """
        Create dskwor00.dbf (workers file)

        Args:
            output_file: Output DBF filename
            workers_data: List of worker records
            workshop_id: Workshop ID
            year: Year (2 digits)
            month: Month (1-12)
            list_no: List number (optional)
        """
        print("=" * 80)
        print("🔨 Creating Workers File (dskwor00.dbf)")
        print("=" * 80)

        # Workers file structure - NEW SSO 2024 FORMAT (29 fields)
        # ⚠️  DSW_KOSO and DSW_BIME20 REMOVED in new structure!
        # ⚠️  Field order changed: DSW_JOB and PER_NATCOD positions swapped
        # ⚠️  DSW_SPOUSE type changed: N→C (Number to Character!)
        fields = [
            ('DSW_ID', 'C', 10, 0),
            ('DSW_YY', 'N', 2, 0),
            ('DSW_MM', 'N', 2, 0),
            ('DSW_LISTNO', 'C', 12, 0),
            ('DSW_ID1', 'C', 8, 0),
            ('DSW_FNAME', 'C', 60, 0),    # Changed: 20→60 (3x larger!)
            ('DSW_LNAME', 'C', 60, 0),    # Changed: 25→60
            ('DSW_DNAME', 'C', 60, 0),    # Changed: 20→60
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
            # DSW_KOSO DELETED in new structure!
            # DSW_BIME20 DELETED in new structure!
            ('DSW_JOB', 'C', 6, 0),       # Changed: position 29→26, length 10→6
            ('PER_NATCOD', 'C', 10, 0),   # Changed: position 28→27
            ('DSW_INC', 'N', 12, 0),      # Changed: 19→12
            ('DSW_SPOUSE', 'C', 10, 0),   # Changed: N19→C10 (type and length!)
        ]

        # Calculate record length
        record_length = 1
        for field in fields:
            record_length += field[2]

        print(f"Record length: {record_length} bytes")
        print(f"Number of records: {len(workers_data)}")
        print()

        with open(output_file, 'wb') as f:
            # Write header
            self._write_dbf_header(f, len(workers_data), record_length, fields)

            # Write records
            for i, record in enumerate(workers_data, 1):
                print(f"Writing worker {i}/{len(workers_data)}: {record.get('DSW_FNAME', '')} {record.get('DSW_LNAME', '')}")
                self._write_worker_record(f, record, fields, workshop_id, year, month, list_no)

            # End of file marker
            f.write(b'\x1A')

        print()
        print(f"✅ Workers file created: {output_file}")
        print("=" * 80)

    def _calculate_totals(self, workers_data: list) -> dict:
        """Calculate totals from workers data"""
        totals = {
            'num_workers': len(workers_data),
            'total_days': 0,
            'total_rooz': 0,
            'total_mah': 0,
            'total_maz': 0,
            'total_mash': 0,
            'total_totl': 0,
            'total_bime': 0,
            'total_koso': 0,  # Note: DSW_KOSO removed in new structure, but kept for backward compat
        }

        for worker in workers_data:
            totals['total_days'] += int(worker.get('DSW_DD', 0) or 0)
            totals['total_rooz'] += int(worker.get('DSW_ROOZ', 0) or 0)
            totals['total_mah'] += int(worker.get('DSW_MAH', 0) or 0)
            totals['total_maz'] += int(worker.get('DSW_MAZ', 0) or 0)
            totals['total_mash'] += int(worker.get('DSW_MASH', 0) or 0)
            totals['total_totl'] += int(worker.get('DSW_TOTL', 0) or 0)
            totals['total_bime'] += int(worker.get('DSW_BIME', 0) or 0)
            # DSW_KOSO removed in new SSO structure, but calculate if present for backward compat
            totals['total_koso'] += int(worker.get('DSW_KOSO', 0) or 0)

        return totals

    def _write_dbf_header(self, f, num_records: int, record_length: int, fields: list):
        """Write DBF file header"""
        from datetime import datetime
        now = datetime.now()

        # Header (32 bytes)
        header = struct.pack('<B', 0x03)  # dBase III (byte 0)
        header += struct.pack('<BBB', now.year % 100, now.month, now.day)  # bytes 1-3
        header += struct.pack('<I', num_records)  # bytes 4-7
        header += struct.pack('<H', 32 + len(fields) * 32 + 1)  # bytes 8-9: header length
        header += struct.pack('<H', record_length)  # bytes 10-11: record length
        header += bytes(16)  # bytes 12-27: reserved
        header += b'\x00'    # byte 28: MDX flag
        header += b'\x7E'    # byte 29: Language driver ID (0x7E for Iran System encoding)
        header += bytes(2)   # bytes 30-31: reserved

        f.write(header)

        # Field descriptors
        for field_name, field_type, field_length, field_decimal in fields:
            field_desc = field_name.ljust(11, '\x00').encode('ascii')
            field_desc += field_type.encode('ascii')
            field_desc += bytes(4)
            field_desc += struct.pack('<B', field_length)
            field_desc += struct.pack('<B', field_decimal)
            field_desc += bytes(14)
            f.write(field_desc)

        # Header terminator
        f.write(b'\x0D')

    def _write_header_record(self, f, header_data: dict, totals: dict,
                             fields: list, year: int, month: int):
        """Write header file record"""
        f.write(b' ')  # Deletion flag

        persian_fields = {'DSK_NAME', 'DSK_FARM', 'DSK_ADRS', 'DSK_DISC'}

        for field_name, field_type, field_length, field_decimal in fields:
            # Get value
            if field_name == 'DSK_YY':
                value = year
            elif field_name == 'DSK_MM':
                value = month
            elif field_name == 'DSK_NUM':
                value = totals['num_workers']
            elif field_name == 'DSK_TDD':
                value = totals['total_days']
            elif field_name == 'DSK_TROOZ':
                value = totals['total_rooz']
            elif field_name == 'DSK_TMAH':
                value = totals['total_mah']
            elif field_name == 'DSK_TMAZ':
                value = totals['total_maz']
            elif field_name == 'DSK_TMASH':
                value = totals['total_mash']
            elif field_name == 'DSK_TTOTL':
                value = totals['total_totl']
            elif field_name == 'DSK_TBIME':
                value = totals['total_bime']
            elif field_name == 'DSK_TKOSO':
                value = totals['total_koso']
            elif field_name == 'DSK_PRATE':
                value = 7  # Default 7%
            else:
                value = header_data.get(field_name, '')

            # Write field
            if field_type == 'C':
                if field_name in persian_fields and value and str(value).strip():
                    # Persian field - use Iran System encoding
                    # Don't strip! Spaces are important for Iran System visual order
                    text_value = str(value)
                    encoded = self.encoder.unicode_to_iran_system(text_value)
                    if len(encoded) > field_length:
                        encoded = encoded[:field_length]
                    else:
                        encoded = encoded + (b' ' * (field_length - len(encoded)))
                    f.write(encoded)
                else:
                    # Regular text
                    text = str(value)[:field_length].ljust(field_length)
                    f.write(text.encode('ascii', errors='replace'))
            elif field_type == 'N':
                try:
                    if field_decimal > 0:
                        num_str = f"{float(value):{field_length}.{field_decimal}f}"
                    else:
                        num_str = f"{int(float(value) if value else 0):>{field_length}d}"
                except:
                    num_str = ' ' * field_length
                f.write(num_str[:field_length].rjust(field_length).encode('ascii'))

    def _write_worker_record(self, f, record: dict, fields: list,
                            workshop_id: str, year: int, month: int, list_no: str):
        """Write worker record"""
        f.write(b' ')  # Deletion flag

        # Persian fields that use Iran System encoding
        persian_fields = {
            'DSW_FNAME',   # First name
            'DSW_LNAME',   # Last name
            'DSW_DNAME',   # Father's name
            'DSW_IDPLC',   # ID issue place
            'DSW_OCP',     # Occupation
            'DSW_SEX',     # Sex (مرد/زن)
            'DSW_NAT',     # Nationality (ایرانی)
            # Note: DSW_JOB is a numeric job code, not Persian text
        }

        for field_name, field_type, field_length, field_decimal in fields:
            # Get value
            if field_name == 'DSW_ID':
                value = workshop_id
            elif field_name == 'DSW_YY':
                value = year
            elif field_name == 'DSW_MM':
                value = month
            elif field_name == 'DSW_LISTNO':
                value = list_no
            else:
                value = record.get(field_name, '')

            # Write field
            if field_type == 'C':
                if field_name in persian_fields and value and str(value).strip():
                    # Persian field - use Iran System encoding
                    # Don't strip! Spaces are important for Iran System visual order
                    text_value = str(value)
                    encoded = self.encoder.unicode_to_iran_system(text_value)
                    if len(encoded) > field_length:
                        encoded = encoded[:field_length]
                    else:
                        encoded = encoded + (b' ' * (field_length - len(encoded)))
                    f.write(encoded)
                else:
                    # Regular text
                    text = str(value)[:field_length].ljust(field_length)
                    f.write(text.encode('ascii', errors='replace'))
            elif field_type == 'N':
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
        description='Convert CSV files to complete DBF set (header + workers)'
    )
    parser.add_argument('header_csv', help='Header CSV file')
    parser.add_argument('workers_csv', help='Workers CSV file')
    parser.add_argument('--workshop-id', required=True, help='Workshop ID (10 chars)')
    parser.add_argument('--year', type=int, required=True, help='Year (2 digits)')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--list-no', default='', help='List number')
    parser.add_argument('--output-dir', default='.', help='Output directory')

    args = parser.parse_args()

    # Create converter
    converter = CompleteDBFConverter()

    # Read CSVs
    print("📂 Reading CSV files...")
    header_data = converter.read_csv(args.header_csv)[0]  # First row only
    workers_data = converter.read_csv(args.workers_csv)
    print(f"✅ Loaded header + {len(workers_data)} workers")
    print()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create DBF files
    converter.create_header_file(
        str(output_dir / 'dskkar00.dbf'),
        header_data,
        workers_data,
        args.year,
        args.month
    )

    converter.create_workers_file(
        str(output_dir / 'dskwor00.dbf'),
        workers_data,
        args.workshop_id,
        args.year,
        args.month,
        args.list_no
    )

    print()
    print("=" * 80)
    print("✅ COMPLETE! Both files created successfully!")
    print("=" * 80)
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Header file: dskkar00.dbf")
    print(f"📄 Workers file: dskwor00.dbf")
    print()


if __name__ == '__main__':
    main()
