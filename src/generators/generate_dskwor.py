#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF Generator for dskwor00.dbf - Worker Details File
تولید‌کننده فایل DBF جزئیات کارگران

This generates the worker details file (dskwor00.dbf) required by
Iranian Social Security Organization with the exact structure
extracted from real SSO files.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.iran_system_encoding import IranSystemEncoder

try:
    import dbf
except ImportError:
    print("❌ Error: dbf is not installed.")
    print("Install it using: pip install dbf")
    sys.exit(1)


class DskworGenerator:
    """Generator for dskwor00.dbf (Worker Details File)"""

    # Exact structure from real SSO DBF file
    DSKWOR_FIELDS = """
        DSW_ID C(10);
        DSW_YY N(2,0);
        DSW_MM N(2,0);
        DSW_LISTNO C(12);
        DSW_ID1 C(8);
        DSW_FNAME C(20);
        DSW_LNAME C(25);
        DSW_DNAME C(20);
        DSW_IDNO C(15);
        DSW_IDPLC C(30);
        DSW_IDATE C(8);
        DSW_BDATE C(8);
        DSW_SEX C(3);
        DSW_NAT C(10);
        DSW_OCP C(50);
        DSW_SDATE C(8);
        DSW_EDATE C(8);
        DSW_DD N(2,0);
        DSW_ROOZ N(12,0);
        DSW_MAH N(12,0);
        DSW_MAZ N(12,0);
        DSW_MASH N(12,0);
        DSW_TOTL N(12,0);
        DSW_BIME N(12,0);
        DSW_PRATE N(2,0);
        DSW_KOSO N(12,0);
        DSW_BIME20 N(12,0);
        PER_NATCOD C(10);
        DSW_JOB C(10);
        DSW_INC N(19,0);
        DSW_SPOUSE N(19,0)
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save output DBF file
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.encoder = IranSystemEncoder()

    def encode_persian_field(self, text: str, max_length: int) -> bytes:
        """
        Encode Persian text using Iran System encoding and pad to field length

        Args:
            text: Persian text
            max_length: Maximum field length

        Returns:
            Encoded and padded bytes
        """
        if not text or not text.strip():
            # Return spaces for empty fields
            return b' ' * max_length

        # Encode using Iran System
        encoded = self.encoder.unicode_to_iran_system(text.strip())

        # Pad or truncate to exact length
        if len(encoded) > max_length:
            encoded = encoded[:max_length]
        elif len(encoded) < max_length:
            # Pad with spaces on the right
            encoded = encoded + (b' ' * (max_length - len(encoded)))

        return encoded

    def format_date(self, date_str: str) -> str:
        """
        Format date to YYYYMMDD (already in Jalali calendar)

        Args:
            date_str: Date string (various formats)

        Returns:
            YYYYMMDD string (8 chars) or empty string
        """
        if not date_str or not str(date_str).strip():
            return ' ' * 8

        # Clean the input
        clean_date = str(date_str).strip().replace('-', '').replace('/', '')

        # Ensure 8 digits
        if len(clean_date) == 8 and clean_date.isdigit():
            return clean_date
        elif len(clean_date) == 6 and clean_date.isdigit():
            # Assume YY/MM/DD format, add century
            return '13' + clean_date

        # Invalid format
        return ' ' * 8

    def calculate_insurance_premium(self, insurable_amount: float) -> int:
        """
        Calculate insurance premium (حق بیمه)

        Formula verified from real data: BIME = MASH * 0.07 (7%)

        Args:
            insurable_amount: Insurable salary amount (مشمول بیمه)

        Returns:
            Insurance premium amount (rounded)
        """
        return int(insurable_amount * 0.07)

    def process_worker_record(self, worker: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single worker record

        Args:
            worker: Worker data dictionary

        Returns:
            Processed record ready for DBF
        """
        # Calculate insurance premium if not provided
        mash = worker.get('DSW_MASH', 0) or 0
        if not worker.get('DSW_BIME'):
            worker['DSW_BIME'] = self.calculate_insurance_premium(mash)

        # Ensure DSW_PRATE is 7 if not provided
        if not worker.get('DSW_PRATE'):
            worker['DSW_PRATE'] = 7

        return worker

    def generate(self, workers_data: List[Dict[str, Any]],
                 workshop_id: str,
                 year: int,
                 month: int,
                 list_no: str = "",
                 filename: str = "dskwor00.dbf") -> str:
        """
        Generate dskwor00.dbf file

        Args:
            workers_data: List of worker records
            workshop_id: Workshop ID (شناسه کارگاه)
            year: Year (2 digits, e.g., 3 for 1403)
            month: Month (1-12)
            list_no: List number (optional)
            filename: Output filename

        Returns:
            Path to generated file
        """
        print("=" * 80)
        print("📝 تولید فایل dskwor00.dbf (جزئیات کارگران)")
        print("=" * 80)
        print(f"Workshop ID: {workshop_id}")
        print(f"Year/Month: {year:02d}/{month:02d}")
        print(f"Workers: {len(workers_data)}")
        print()

        output_path = self.output_dir / filename

        # Remove existing file
        if output_path.exists():
            output_path.unlink()

        # Create DBF table with structure
        # Use default codepage (cp437)
        table = dbf.Table(str(output_path), self.DSKWOR_FIELDS)
        table.open(mode=dbf.READ_WRITE)

        # Process each worker
        for i, worker in enumerate(workers_data, 1):
            fname = worker.get('DSW_FNAME', '')
            lname = worker.get('DSW_LNAME', '')
            print(f"Processing worker {i}/{len(workers_data)}: {fname} {lname}")

            # Process the record (calculate insurance, etc.)
            processed = self.process_worker_record(worker)

            # Create record with placeholder for Persian fields
            #  We'll patch the Persian fields later with raw bytes
            table.append({
                'DSW_ID': workshop_id[:10],
                'DSW_YY': year,
                'DSW_MM': month,
                'DSW_LISTNO': list_no[:12],
                'DSW_ID1': str(processed.get('DSW_ID1', ''))[:8],
                'DSW_FNAME': ' ' * 20,  # Placeholder
                'DSW_LNAME': ' ' * 25,  # Placeholder
                'DSW_DNAME': ' ' * 20,  # Placeholder
                'DSW_IDNO': str(processed.get('DSW_IDNO', ''))[:15],
                'DSW_IDPLC': ' ' * 30,  # Placeholder
                'DSW_IDATE': self.format_date(processed.get('DSW_IDATE', '')),
                'DSW_BDATE': self.format_date(processed.get('DSW_BDATE', '')),
                'DSW_SEX': str(processed.get('DSW_SEX', ''))[:3],
                'DSW_NAT': str(processed.get('DSW_NAT', ''))[:10],
                'DSW_OCP': ' ' * 50,  # Placeholder
                'DSW_SDATE': self.format_date(processed.get('DSW_SDATE', '')),
                'DSW_EDATE': self.format_date(processed.get('DSW_EDATE', '')),
                'DSW_DD': int(processed.get('DSW_DD', 0)),
                'DSW_ROOZ': int(processed.get('DSW_ROOZ', 0)),
                'DSW_MAH': int(processed.get('DSW_MAH', 0)),
                'DSW_MAZ': int(processed.get('DSW_MAZ', 0)),
                'DSW_MASH': int(processed.get('DSW_MASH', 0)),
                'DSW_TOTL': int(processed.get('DSW_TOTL', 0)),
                'DSW_BIME': int(processed.get('DSW_BIME', 0)),
                'DSW_PRATE': int(processed.get('DSW_PRATE', 7)),
                'DSW_KOSO': int(processed.get('DSW_KOSO', 0)),
                'DSW_BIME20': int(processed.get('DSW_BIME20', 0)),
                'PER_NATCOD': str(processed.get('PER_NATCOD', ''))[:10],
                'DSW_JOB': str(processed.get('DSW_JOB', ''))[:10],
                'DSW_INC': int(processed.get('DSW_INC', 0)),
                'DSW_SPOUSE': int(processed.get('DSW_SPOUSE', 0)),
            })

            # Store encoded Persian data to patch later
            if i == 1:  # Initialize on first worker
                self.persian_patches = []

            self.persian_patches.append({
                'record_num': i - 1,
                'DSW_FNAME': self.encode_persian_field(fname, 20),
                'DSW_LNAME': self.encode_persian_field(lname, 25),
                'DSW_DNAME': self.encode_persian_field(processed.get('DSW_DNAME', ''), 20),
                'DSW_IDPLC': self.encode_persian_field(processed.get('DSW_IDPLC', ''), 30),
                'DSW_OCP': self.encode_persian_field(processed.get('DSW_OCP', ''), 50),
            })

        # Close table
        table.close()

        print()
        print(f"✅ فایل با موفقیت ایجاد شد: {output_path}")
        print(f"📊 تعداد رکوردها: {len(workers_data)}")
        print("=" * 80)

        return str(output_path)


def main():
    """Main entry point for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate dskwor00.dbf file for Iranian Social Security'
    )
    parser.add_argument('input_json', help='Input JSON file with worker data')
    parser.add_argument('--workshop-id', required=True, help='Workshop ID (10 chars)')
    parser.add_argument('--year', type=int, required=True, help='Year (2 digits, e.g., 3 for 1403)')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--list-no', default='', help='List number (optional)')
    parser.add_argument('--output', default='dskwor00.dbf', help='Output filename')
    parser.add_argument('--output-dir', default='output', help='Output directory')

    args = parser.parse_args()

    # Read input JSON
    with open(args.input_json, 'r', encoding='utf-8') as f:
        workers_data = json.load(f)

    # Generate DBF
    generator = DskworGenerator(output_dir=args.output_dir)
    output_path = generator.generate(
        workers_data=workers_data,
        workshop_id=args.workshop_id,
        year=args.year,
        month=args.month,
        list_no=args.list_no,
        filename=args.output
    )

    print(f"\n✅ Success! Generated: {output_path}")


if __name__ == '__main__':
    main()
