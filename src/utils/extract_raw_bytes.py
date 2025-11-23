#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract raw bytes from DBF name fields
"""

import sys
from dbfread import DBF


def extract_raw_bytes(dbf_path):
    """Extract raw bytes from Persian name fields"""

    print("=" * 80)
    print("📂 استخراج Hex Bytes از فایل DBF")
    print("=" * 80)
    print(f"File: {dbf_path}")
    print()

    try:
        # Open with latin-1 encoding to preserve raw byte values
        db = DBF(dbf_path, encoding='latin-1', char_decode_errors='ignore')

        # dbfread returns an iterator
        records = list(db)
        print(f"Total records: {len(records)}")
        print()

        # Process first 3 records
        for i, record in enumerate(records[:3]):
            print(f"رکورد #{i+1}:")
            print("-" * 40)

            for field_name in ['DSW_FNAME', 'DSW_LNAME', 'DSW_DNAME']:
                try:
                    # Access raw field data
                    value = record.get(field_name, '')

                    # Convert to bytes
                    if isinstance(value, str):
                        # Use latin-1 to preserve byte values
                        raw_bytes = value.encode('latin-1').rstrip(b' \x00')
                    elif isinstance(value, bytes):
                        raw_bytes = value.rstrip(b' \x00')
                    else:
                        continue

                    if len(raw_bytes) > 0:
                        hex_str = ' '.join(f'{b:02x}' for b in raw_bytes)
                        print(f"{field_name}:")
                        print(f"  Hex:   {hex_str}")
                        print(f"  Bytes: {list(raw_bytes)}")
                except Exception as e:
                    print(f"{field_name}: error - {e}")

            print()

        print("✅ استخراج کامل شد")

    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    dbf_file = '/home/user/abap-mdf-sso/sample/dskwor00.dbf'
    extract_raw_bytes(dbf_file)
