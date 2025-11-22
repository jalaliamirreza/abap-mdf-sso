#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for DBF generation
تست تولید فایل DBF

This script tests the DBF generation functionality with sample data.
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'utils'))

try:
    from generate_dbf import SSODBFGenerator
except ImportError:
    print("Error: Cannot import generate_dbf module")
    print("Make sure you're running this from the tests directory")
    sys.exit(1)


class TestSSODBFGenerator(unittest.TestCase):
    """Test cases for SSO DBF Generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = SSODBFGenerator()
        self.test_data_path = Path(__file__).parent / 'sample_data.json'
        self.output_path = Path(__file__).parent / 'output'
        self.output_path.mkdir(exist_ok=True)

    def test_validate_national_id_valid(self):
        """Test validation of valid national IDs"""
        valid_ids = [
            '0123456789',
            '1234567890',
            '0013542419',
        ]

        for national_id in valid_ids:
            result = self.generator.validate_national_id(national_id)
            self.assertTrue(
                result,
                f"Valid national ID {national_id} failed validation"
            )

    def test_validate_national_id_invalid(self):
        """Test validation of invalid national IDs"""
        invalid_ids = [
            '1111111111',  # All same digits
            '123',         # Too short
            '12345678901', # Too long
            '',            # Empty
            'abcd123456',  # Non-numeric
        ]

        for national_id in invalid_ids:
            result = self.generator.validate_national_id(national_id)
            self.assertFalse(
                result,
                f"Invalid national ID {national_id} passed validation"
            )

    def test_validate_jalali_date_valid(self):
        """Test validation of valid Jalali dates"""
        valid_dates = [
            '14020101',  # 1 Farvardin 1402
            '14020631',  # 31 Shahrivar 1402
            '14021229',  # 29 Esfand 1402
        ]

        for date_str in valid_dates:
            result = self.generator.validate_jalali_date(date_str)
            self.assertTrue(
                result,
                f"Valid date {date_str} failed validation"
            )

    def test_validate_jalali_date_invalid(self):
        """Test validation of invalid Jalali dates"""
        invalid_dates = [
            '14021232',  # Invalid day in Esfand
            '14021332',  # Invalid month
            '14020732',  # Invalid day in Mehr
            '1402010',   # Too short
            '',          # Empty
        ]

        for date_str in invalid_dates:
            result = self.generator.validate_jalali_date(date_str)
            self.assertFalse(
                result,
                f"Invalid date {date_str} passed validation"
            )

    def test_validate_record_valid(self):
        """Test validation of valid records"""
        valid_record = {
            'ins_number': '00001234567890123456',
            'national_id': '0123456789',
            'first_name': 'علی',
            'last_name': 'احمدی',
            'father_name': 'حسین',
            'birth_date': '13650523',
            'work_days': 30,
            'base_salary': 50000000,
            'overtime': 5000000,
            'benefits': 10000000,
            'total': 65000000,
        }

        result = self.generator.validate_record(valid_record)
        self.assertTrue(result, "Valid record failed validation")

    def test_validate_record_invalid(self):
        """Test validation of invalid records"""
        invalid_record = {
            'ins_number': '00001234567890123456',
            'national_id': '1111111111',  # Invalid
            'first_name': 'علی',
            'last_name': 'احمدی',
            'father_name': 'حسین',
            'birth_date': '14021332',     # Invalid date
            'work_days': 35,              # Too many days
            'base_salary': -5000000,      # Negative
            'total': 0,
        }

        result = self.generator.validate_record(invalid_record)
        self.assertFalse(result, "Invalid record passed validation")

    def test_format_record(self):
        """Test record formatting"""
        input_record = {
            'ins_number': '123',
            'national_id': '1234567890',
            'first_name': 'علی',
            'last_name': 'احمدی',
            'father_name': 'حسین',
            'birth_date': '13650523',
            'work_days': 30,
            'base_salary': 50000000,
            'overtime': 5000000,
            'benefits': 10000000,
            'total': 65000000,
        }

        formatted = self.generator.format_record(input_record)

        # Check field lengths
        self.assertEqual(len(formatted['SHOMARE_B']), 20)
        self.assertEqual(len(formatted['KOD_MELI']), 10)
        self.assertEqual(len(formatted['TARIKH_TAV']), 8)

        # Check numeric conversions
        self.assertEqual(formatted['ROOZ_KAR'], 30)
        self.assertEqual(formatted['HOGHOGH'], 50000000)
        self.assertEqual(formatted['JAM_MAZAYA'], 65000000)

    def test_generate_dbf_with_sample_data(self):
        """Test DBF generation with sample data"""
        if not self.test_data_path.exists():
            self.skipTest("Sample data file not found")

        output_file = self.output_path / 'test_output.dbf'

        result = self.generator.generate_dbf(
            str(self.test_data_path),
            str(output_file)
        )

        self.assertTrue(result, "DBF generation failed")
        self.assertTrue(output_file.exists(), "Output file was not created")

        # Check file size is reasonable
        file_size = output_file.stat().st_size
        self.assertGreater(file_size, 0, "Output file is empty")

    def tearDown(self):
        """Clean up after tests"""
        # Optionally clean up generated test files
        pass


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_end_to_end_workflow(self):
        """Test complete workflow from JSON to DBF"""
        test_data_path = Path(__file__).parent / 'sample_data.json'
        output_path = Path(__file__).parent / 'output'
        output_path.mkdir(exist_ok=True)
        output_file = output_path / 'integration_test.dbf'

        if not test_data_path.exists():
            self.skipTest("Sample data file not found")

        # Create generator
        generator = SSODBFGenerator()

        # Generate DBF
        result = generator.generate_dbf(
            str(test_data_path),
            str(output_file)
        )

        # Verify results
        self.assertTrue(result, "End-to-end workflow failed")
        self.assertTrue(output_file.exists(), "Output file not created")
        self.assertEqual(len(generator.errors), 0, f"Errors occurred: {generator.errors}")

        print(f"\n✓ Integration test passed")
        print(f"  Output file: {output_file}")
        print(f"  File size: {output_file.stat().st_size} bytes")
        if generator.warnings:
            print(f"  Warnings: {len(generator.warnings)}")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestSSODBFGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
