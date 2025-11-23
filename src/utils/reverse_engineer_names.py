#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reverse engineer Persian names from hex bytes
"""

from iran_system_encoding import IranSystemEncoder


def find_matching_name(target_hex, candidates):
    """Find which name produces the target hex"""

    target_bytes = bytes.fromhex(target_hex.replace(' ', ''))

    for name in candidates:
        result = IranSystemEncoder.unicode_to_iran_system(name)
        if result == target_bytes:
            return name, True
        # Check if it's a prefix match
        if result[:len(target_bytes)] == target_bytes or target_bytes[:len(result)] == result:
            return name, False

    return None, False


def main():
    print("=" * 80)
    print("🔍 Reverse Engineering نام‌های فارسی از Hex Bytes")
    print("=" * 80)
    print()

    # Extracted hex bytes from DBF
    dbf_samples = [
        {
            'record': 1,
            'DSW_FNAME': 'fc f3 e4',
            'DSW_LNAME': 'fd a5 f8 a4 fe 95 20 fc f7 91 93 a4 ec',
            'DSW_DNAME': 'fc f3 e4 93 fe a4 ec',
        },
        {
            'record': 2,
            'DSW_FNAME': 'f6 fe a8 9f a2 f5 9f f5',
            'DSW_LNAME': 'a4 f8 95 20 f4 e0 91 ee',
            'DSW_DNAME': 'a4 93 ee 90 20 fc f3 e4',
        },
        {
            'record': 3,
            'DSW_FNAME': 'f6 a8 9f',
            'DSW_LNAME': 'fc 93 9b a4',
            'DSW_DNAME': 'fc f3 e4 20 96 93 9f f5',
        },
    ]

    # Common Persian first names
    first_names = [
        "علی", "محمد", "حسن", "حسین", "رضا", "مهدی", "احمد",
        "حمید", "امیر", "مجید", "سعید", "جواد", "ابراهیم",
        "فاطمه", "زهرا", "مریم", "سارا", "نرگس", "لیلا",
    ]

    # Common Persian last names
    last_names = [
        "احمدی", "محمدی", "رضایی", "حسینی", "کریمی",
        "موسوی", "صادقی", "اکبری", "جعفری", "علیپور",
        "علوی", "رحمانی", "کاظمی", "نوری", "امینی",
    ]

    # Father names (usually same as first names)
    father_names = first_names + ["علیرضا", "محمدرضا", "غلامرضا", "امیرعلی"]

    print("جستجوی نام‌های مطابق:")
    print("-" * 80)

    for sample in dbf_samples:
        print(f"\n📝 رکورد #{sample['record']}:")
        print("-" * 40)

        # Find first name
        fname_hex = sample['DSW_FNAME']
        match, exact = find_matching_name(fname_hex, first_names)
        print(f"DSW_FNAME ({fname_hex})")
        if match:
            print(f"  → {match} {'✅' if exact else '⚠️ (partial)'}")
            # Verify
            result = IranSystemEncoder.unicode_to_iran_system(match)
            print(f"  Verification: {result.hex()}")
        else:
            print(f"  → نام پیدا نشد")

        # Find last name
        lname_hex = sample['DSW_LNAME']
        match, exact = find_matching_name(lname_hex, last_names)
        print(f"DSW_LNAME ({lname_hex})")
        if match:
            print(f"  → {match} {'✅' if exact else '⚠️ (partial)'}")
            result = IranSystemEncoder.unicode_to_iran_system(match)
            print(f"  Verification: {result.hex()}")
        else:
            print(f"  → نام خانوادگی پیدا نشد")

        # Find father name
        dname_hex = sample['DSW_DNAME']
        match, exact = find_matching_name(dname_hex, father_names)
        print(f"DSW_DNAME ({dname_hex})")
        if match:
            print(f"  → {match} {'✅' if exact else '⚠️ (partial)'}")
            result = IranSystemEncoder.unicode_to_iran_system(match)
            print(f"  Verification: {result.hex()}")
        else:
            print(f"  → نام پدر پیدا نشد")

    print()
    print("=" * 80)
    print("تحلیل نام‌های پیدا نشده:")
    print("=" * 80)
    print()

    # Analyze unknown patterns
    print("برای نام‌های پیدا نشده، بررسی pattern:")
    print()

    # Record 2 analysis
    print("رکورد #2:")
    print("  DSW_FNAME: f6 fe a8 9f a2 f5 9f f5")
    print("  Test: 'حسین' + 'محمد' = 'حسینمحمد' or 'حسین محمد'")
    test_name = "حسین محمد"
    result = IranSystemEncoder.unicode_to_iran_system(test_name)
    print(f"  Result: {result.hex()}")
    if result.hex() == 'f6fea89fa2f59ff5':
        print("  ✅ Match: حسین محمد (بدون فاصله)")

    test_name2 = "حسینمحمد"
    result2 = IranSystemEncoder.unicode_to_iran_system(test_name2)
    print(f"  Result2: {result2.hex()}")

    print()


if __name__ == '__main__':
    main()
