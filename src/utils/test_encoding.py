#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Iran System Encoding against real DBF data
"""

import sys
from pathlib import Path

# Add parent directory to path to import iran_system_encoding
sys.path.insert(0, str(Path(__file__).parent))

from iran_system_encoding import IranSystemEncoder


def test_known_samples():
    """Test encoder against known hex bytes from real DBF file"""

    print("=" * 80)
    print("🧪 تست Iran System Encoder با داده واقعی DBF")
    print("=" * 80)
    print()

    # Known samples from /tmp/encoding_analysis.md
    known_samples = [
        {
            'field': 'DSW_FNAME (نام)',
            'expected_hex': 'fc f3 e4',
            'expected_bytes': [252, 243, 228],
            'text': 'علی'  # Confirmed match
        },
        # We'll test more once we identify the other names
    ]

    print("📋 تست با نمونه‌های شناخته‌شده از فایل DBF واقعی:")
    print("-" * 80)

    for sample in known_samples:
        text = sample['text']
        expected_bytes = sample['expected_bytes']
        expected_hex = sample['expected_hex'].replace(' ', '')

        result_bytes = IranSystemEncoder.unicode_to_iran_system(text)
        result_hex = result_bytes.hex()

        match = "✅" if list(result_bytes) == expected_bytes else "❌"

        print(f"\n{sample['field']}")
        print(f"  Input:          {text}")
        print(f"  Expected hex:   {expected_hex}")
        print(f"  Actual hex:     {result_hex}")
        print(f"  Expected bytes: {expected_bytes}")
        print(f"  Actual bytes:   {list(result_bytes)}")
        print(f"  Match: {match}")

    print()


def test_common_names():
    """Test encoder with common Persian names"""

    print("=" * 80)
    print("🧪 تست با نام‌های رایج فارسی")
    print("=" * 80)
    print()

    common_names = [
        # First names
        "علی", "محمد", "حسن", "حسین", "رضا", "مهدی",
        "فاطمه", "زهرا", "مریم", "سارا", "نرگس",

        # Last names
        "احمدی", "محمدی", "رضایی", "حسینی", "کریمی",
        "موسوی", "صادقی", "اکبری", "جعفری", "علیپور"
    ]

    print(f"{'نام':<15} {'Hex Output':<30} {'Bytes'}")
    print("-" * 80)

    for name in common_names:
        result = IranSystemEncoder.unicode_to_iran_system(name)
        hex_output = result.hex()
        bytes_list = list(result)

        # Show first 6 bytes for readability
        bytes_str = str(bytes_list[:6])
        if len(bytes_list) > 6:
            bytes_str = bytes_str[:-1] + ", ...]"

        print(f"{name:<15} {hex_output:<30} {bytes_str}")

    print()


def test_mixed_content():
    """Test with mixed Persian and numbers"""

    print("=" * 80)
    print("🧪 تست با محتوای ترکیبی (فارسی + اعداد)")
    print("=" * 80)
    print()

    mixed_samples = [
        "علی123",
        "رضا 1400",
        "محمد (تهران)",
        "1234567890",  # Just numbers
    ]

    for text in mixed_samples:
        result = IranSystemEncoder.unicode_to_iran_system(text)
        print(f"Input:  {text}")
        print(f"Output: {result.hex()}")
        print(f"Bytes:  {list(result)}")
        print()


def extract_dbf_samples():
    """Extract samples from actual DBF file for comparison"""

    print("=" * 80)
    print("📂 استخراج نمونه‌ها از فایل DBF واقعی")
    print("=" * 80)
    print()

    dbf_file = Path("/home/user/abap-mdf-sso/sample/dskwor00.dbf")

    if not dbf_file.exists():
        print(f"❌ فایل DBF یافت نشد: {dbf_file}")
        return

    try:
        from dbfpy3 import dbf

        db = dbf.Dbf(str(dbf_file))

        print(f"✅ فایل باز شد: {dbf_file}")
        print(f"تعداد رکوردها: {len(db)}")
        print()

        # Extract first record's name fields
        if len(db) > 0:
            record = db[0]

            print("رکورد اول:")
            print("-" * 40)

            for field_name in ['DSW_FNAME', 'DSW_LNAME', 'DSW_DNAME']:
                try:
                    value = record[field_name]
                    # Get raw bytes
                    if isinstance(value, bytes):
                        raw_bytes = value
                    elif isinstance(value, str):
                        raw_bytes = value.encode('latin-1')  # Preserve byte values
                    else:
                        raw_bytes = str(value).encode('latin-1')

                    # Remove trailing spaces/nulls
                    raw_bytes = raw_bytes.rstrip(b' \x00')

                    hex_value = raw_bytes.hex()
                    bytes_list = list(raw_bytes)
                    print(f"\n{field_name}:")
                    print(f"  Hex:   {hex_value}")
                    print(f"  Bytes: {bytes_list}")
                except Exception as e:
                    print(f"\n{field_name}: (error: {e})")

        db.close()

    except Exception as e:
        print(f"❌ خطا در خواندن DBF: {e}")

    print()


if __name__ == '__main__':
    # Run all tests
    test_known_samples()
    test_common_names()
    test_mixed_content()
    extract_dbf_samples()

    print("=" * 80)
    print("✅ تست‌ها کامل شد!")
    print("=" * 80)
