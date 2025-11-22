#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF File Generator for Iranian Social Security
تولید فایل DBF برای تامین اجتماعی ایران

This script converts JSON data exported from SAP to DBF format
required by Iranian Social Security Organization.
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
import argparse

try:
    from dbfpy3 import dbf
except ImportError:
    print("Error: dbfpy3 is not installed.")
    print("Install it using: pip install dbfpy3")
    sys.exit(1)


class SSODBFGenerator:
    """Generator for Iranian Social Security DBF files"""

    # DBF Field Definitions based on SSO specifications
    DBF_STRUCTURE = [
        ('SHOMARE_B', 'C', 20),   # Insurance Number
        ('KOD_MELI', 'C', 10),    # National ID
        ('NAM', 'C', 30),         # First Name
        ('NAM_KHANE', 'C', 40),   # Last Name
        ('NAM_PEDAR', 'C', 30),   # Father's Name
        ('TARIKH_TAV', 'C', 8),   # Birth Date
        ('ROOZ_KAR', 'N', 3, 0),  # Working Days
        ('HOGHOGH', 'N', 15, 0),  # Base Salary
        ('EZAFE_KAR', 'N', 15, 0),  # Overtime
        ('MAZAYA', 'N', 15, 0),   # Benefits
        ('JAM_MAZAYA', 'N', 15, 0),  # Total Benefits
        ('TAR_SHOROO', 'C', 8),   # Start Date
        ('TAR_KHATEME', 'C', 8),  # End Date
        ('NOE_GHARA', 'C', 2),    # Contract Type
        ('SABEGHE', 'N', 5, 2),   # Work History (years)
    ]

    def __init__(self, config_file: str = None):
        """
        Initialize the DBF generator

        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self._load_config(config_file) if config_file else {}
        self.errors = []
        self.warnings = []

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {}

    def validate_national_id(self, national_id: str) -> bool:
        """
        Validate Iranian National ID (کد ملی)

        Args:
            national_id: 10-digit national ID

        Returns:
            True if valid, False otherwise
        """
        if not national_id or len(national_id) != 10:
            return False

        # Check if all digits are the same
        if national_id == national_id[0] * 10:
            return False

        try:
            # Calculate checksum
            check_sum = 0
            for i in range(9):
                check_sum += int(national_id[i]) * (10 - i)

            remainder = check_sum % 11
            check_digit = int(national_id[9])

            if remainder < 2:
                return check_digit == remainder
            else:
                return check_digit == (11 - remainder)
        except (ValueError, IndexError):
            return False

    def validate_jalali_date(self, date_str: str) -> bool:
        """
        Validate Jalali (Persian) date in YYYYMMDD format

        Args:
            date_str: Date string in YYYYMMDD format

        Returns:
            True if valid, False otherwise
        """
        if not date_str or len(date_str) != 8:
            return False

        try:
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])

            # Basic validation
            if year < 1300 or year > 1500:
                return False
            if month < 1 or month > 12:
                return False

            # Days per month validation
            if month <= 6:
                max_days = 31
            elif month <= 11:
                max_days = 30
            else:  # month 12
                # Simple leap year check for Jalali calendar
                max_days = 30 if self._is_jalali_leap(year) else 29

            if day < 1 or day > max_days:
                return False

            return True
        except (ValueError, IndexError):
            return False

    def _is_jalali_leap(self, year: int) -> bool:
        """
        Check if a Jalali year is leap year

        Args:
            year: Jalali year

        Returns:
            True if leap year
        """
        # 33-year cycle algorithm
        breaks = [1, 5, 9, 13, 17, 22, 26, 30]
        cycle = year % 33
        return cycle in breaks

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a single record

        Args:
            record: Dictionary containing record data

        Returns:
            True if valid, False otherwise
        """
        valid = True
        record_id = record.get('national_id', 'Unknown')

        # Required fields check
        required_fields = ['ins_number', 'national_id', 'first_name',
                          'last_name', 'father_name', 'birth_date',
                          'work_days', 'base_salary', 'total']

        for field in required_fields:
            if field not in record or not record[field]:
                self.errors.append(f"Record {record_id}: Missing required field '{field}'")
                valid = False

        # Validate National ID
        if 'national_id' in record:
            if not self.validate_national_id(str(record['national_id']).zfill(10)):
                self.errors.append(f"Record {record_id}: Invalid national ID")
                valid = False

        # Validate Birth Date
        if 'birth_date' in record:
            if not self.validate_jalali_date(str(record['birth_date'])):
                self.errors.append(f"Record {record_id}: Invalid birth date")
                valid = False

        # Validate Working Days
        if 'work_days' in record:
            try:
                days = int(record['work_days'])
                if days < 1 or days > 31:
                    self.errors.append(f"Record {record_id}: Working days must be between 1-31")
                    valid = False
            except (ValueError, TypeError):
                self.errors.append(f"Record {record_id}: Invalid working days value")
                valid = False

        # Validate amounts
        amount_fields = ['base_salary', 'overtime', 'benefits', 'total']
        for field in amount_fields:
            if field in record:
                try:
                    amount = float(record.get(field, 0))
                    if amount < 0:
                        self.errors.append(f"Record {record_id}: {field} cannot be negative")
                        valid = False
                except (ValueError, TypeError):
                    self.errors.append(f"Record {record_id}: Invalid {field} value")
                    valid = False

        # Validate total calculation
        try:
            base = float(record.get('base_salary', 0))
            overtime = float(record.get('overtime', 0))
            benefits = float(record.get('benefits', 0))
            total = float(record.get('total', 0))

            calculated_total = base + overtime + benefits
            if abs(calculated_total - total) > 1:  # Allow 1 Rial difference for rounding
                self.warnings.append(
                    f"Record {record_id}: Total mismatch "
                    f"(calculated: {calculated_total}, provided: {total})"
                )
        except (ValueError, TypeError):
            pass

        return valid

    def format_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a record for DBF output

        Args:
            record: Input record dictionary

        Returns:
            Formatted record dictionary
        """
        formatted = {
            'SHOMARE_B': str(record.get('ins_number', '')).ljust(20)[:20],
            'KOD_MELI': str(record.get('national_id', '')).zfill(10)[:10],
            'NAM': str(record.get('first_name', '')).ljust(30)[:30],
            'NAM_KHANE': str(record.get('last_name', '')).ljust(40)[:40],
            'NAM_PEDAR': str(record.get('father_name', '')).ljust(30)[:30],
            'TARIKH_TAV': str(record.get('birth_date', '')).zfill(8)[:8],
            'ROOZ_KAR': int(record.get('work_days', 0)),
            'HOGHOGH': int(float(record.get('base_salary', 0))),
            'EZAFE_KAR': int(float(record.get('overtime', 0))),
            'MAZAYA': int(float(record.get('benefits', 0))),
            'JAM_MAZAYA': int(float(record.get('total', 0))),
            'TAR_SHOROO': str(record.get('job_start', '')).zfill(8)[:8],
            'TAR_KHATEME': str(record.get('job_end', '')).ljust(8)[:8],
            'NOE_GHARA': str(record.get('contract_type', '01')).ljust(2)[:2],
            'SABEGHE': float(record.get('work_history', 0)),
        }

        return formatted

    def generate_dbf(self, input_file: str, output_file: str) -> bool:
        """
        Generate DBF file from JSON input

        Args:
            input_file: Path to input JSON file
            output_file: Path to output DBF file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load input data
            print(f"Loading data from {input_file}...")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract records
            if isinstance(data, dict) and 'payroll_data' in data:
                records = data['payroll_data']
            elif isinstance(data, list):
                records = data
            else:
                self.errors.append("Invalid JSON structure")
                return False

            print(f"Found {len(records)} records")

            # Validate records
            print("Validating records...")
            valid_records = []
            for i, record in enumerate(records):
                if self.validate_record(record):
                    valid_records.append(record)
                else:
                    print(f"  Skipping invalid record {i+1}")

            if not valid_records:
                self.errors.append("No valid records found")
                return False

            print(f"Validated {len(valid_records)} records")

            # Create DBF file
            print(f"Creating DBF file: {output_file}...")
            db = dbf.Dbf(output_file, new=True)

            # Define structure
            for field_def in self.DBF_STRUCTURE:
                db.add_field(*field_def)

            # Write records
            for i, record in enumerate(valid_records):
                formatted = self.format_record(record)
                rec = db.new_record()
                for field_name, value in formatted.items():
                    rec[field_name] = value
                rec.store()

                if (i + 1) % 100 == 0:
                    print(f"  Processed {i+1} records...")

            db.close()

            print(f"✓ Successfully created DBF file with {len(valid_records)} records")

            # Print warnings
            if self.warnings:
                print(f"\n⚠ Warnings ({len(self.warnings)}):")
                for warning in self.warnings[:10]:  # Show first 10 warnings
                    print(f"  - {warning}")
                if len(self.warnings) > 10:
                    print(f"  ... and {len(self.warnings) - 10} more warnings")

            return True

        except Exception as e:
            self.errors.append(f"Failed to generate DBF: {str(e)}")
            return False

    def print_errors(self):
        """Print all errors"""
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate DBF file for Iranian Social Security'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file from SAP'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output DBF file'
    )
    parser.add_argument(
        '--config', '-c',
        help='Configuration file (optional)'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Create generator
    generator = SSODBFGenerator(config_file=args.config)

    # Generate DBF
    success = generator.generate_dbf(args.input, args.output)

    # Print errors if any
    if not success:
        generator.print_errors()
        sys.exit(1)

    print(f"\n✓ DBF file created successfully: {args.output}")
    sys.exit(0)


if __name__ == '__main__':
    main()
