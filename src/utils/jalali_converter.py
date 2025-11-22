#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jalali (Persian) Calendar Converter
تبدیل تاریخ میلادی به شمسی

This module provides utilities for converting between Gregorian and Jalali calendars.
"""

from datetime import datetime, date
from typing import Tuple, Optional

try:
    import jdatetime
    JDATETIME_AVAILABLE = True
except ImportError:
    JDATETIME_AVAILABLE = False
    print("Warning: jdatetime module not available. Using approximation.")


class JalaliConverter:
    """Converter between Gregorian and Jalali (Persian) calendars"""

    @staticmethod
    def gregorian_to_jalali(greg_date: date) -> Tuple[int, int, int]:
        """
        Convert Gregorian date to Jalali date

        Args:
            greg_date: Gregorian date object

        Returns:
            Tuple of (year, month, day) in Jalali calendar
        """
        if JDATETIME_AVAILABLE:
            j_date = jdatetime.date.fromgregorian(date=greg_date)
            return (j_date.year, j_date.month, j_date.day)
        else:
            # Fallback: Simple approximation (NOT ACCURATE)
            # This should be replaced with proper conversion
            return JalaliConverter._approximate_conversion(greg_date)

    @staticmethod
    def jalali_to_gregorian(year: int, month: int, day: int) -> date:
        """
        Convert Jalali date to Gregorian date

        Args:
            year: Jalali year
            month: Jalali month (1-12)
            day: Jalali day (1-31)

        Returns:
            Gregorian date object
        """
        if JDATETIME_AVAILABLE:
            j_date = jdatetime.date(year, month, day)
            return j_date.togregorian()
        else:
            raise NotImplementedError(
                "Jalali to Gregorian conversion requires jdatetime module"
            )

    @staticmethod
    def format_jalali_date(year: int, month: int, day: int) -> str:
        """
        Format Jalali date as YYYYMMDD string

        Args:
            year: Jalali year
            month: Jalali month
            day: Jalali day

        Returns:
            Formatted date string (YYYYMMDD)
        """
        return f"{year:04d}{month:02d}{day:02d}"

    @staticmethod
    def parse_jalali_date(date_str: str) -> Tuple[int, int, int]:
        """
        Parse Jalali date string in YYYYMMDD format

        Args:
            date_str: Date string in YYYYMMDD format

        Returns:
            Tuple of (year, month, day)
        """
        if len(date_str) != 8:
            raise ValueError("Date string must be 8 characters (YYYYMMDD)")

        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        return (year, month, day)

    @staticmethod
    def gregorian_to_jalali_string(greg_date: date) -> str:
        """
        Convert Gregorian date to Jalali string (YYYYMMDD)

        Args:
            greg_date: Gregorian date object

        Returns:
            Jalali date string (YYYYMMDD)
        """
        year, month, day = JalaliConverter.gregorian_to_jalali(greg_date)
        return JalaliConverter.format_jalali_date(year, month, day)

    @staticmethod
    def is_jalali_leap_year(year: int) -> bool:
        """
        Check if a Jalali year is a leap year

        The Jalali calendar uses a 33-year cycle with leap years
        at positions: 1, 5, 9, 13, 17, 22, 26, 30

        Args:
            year: Jalali year

        Returns:
            True if leap year, False otherwise
        """
        # 33-year cycle
        breaks = [1, 5, 9, 13, 17, 22, 26, 30]
        cycle = year % 33
        return cycle in breaks

    @staticmethod
    def jalali_month_days(year: int, month: int) -> int:
        """
        Get number of days in a Jalali month

        Args:
            year: Jalali year
            month: Jalali month (1-12)

        Returns:
            Number of days in the month
        """
        if month <= 6:
            return 31
        elif month <= 11:
            return 30
        else:  # month 12
            return 30 if JalaliConverter.is_jalali_leap_year(year) else 29

    @staticmethod
    def validate_jalali_date(year: int, month: int, day: int) -> bool:
        """
        Validate a Jalali date

        Args:
            year: Jalali year
            month: Jalali month
            day: Jalali day

        Returns:
            True if valid, False otherwise
        """
        if year < 1300 or year > 1500:
            return False
        if month < 1 or month > 12:
            return False

        max_days = JalaliConverter.jalali_month_days(year, month)
        if day < 1 or day > max_days:
            return False

        return True

    @staticmethod
    def jalali_month_name(month: int, language: str = 'fa') -> str:
        """
        Get Jalali month name

        Args:
            month: Month number (1-12)
            language: 'fa' for Farsi, 'en' for English

        Returns:
            Month name
        """
        if language == 'fa':
            month_names = [
                'فروردین', 'اردیبهشت', 'خرداد',
                'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر',
                'دی', 'بهمن', 'اسفند'
            ]
        else:  # English
            month_names = [
                'Farvardin', 'Ordibehesht', 'Khordad',
                'Tir', 'Mordad', 'Shahrivar',
                'Mehr', 'Aban', 'Azar',
                'Dey', 'Bahman', 'Esfand'
            ]

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        return month_names[month - 1]

    @staticmethod
    def _approximate_conversion(greg_date: date) -> Tuple[int, int, int]:
        """
        Approximate Gregorian to Jalali conversion (NOT ACCURATE)

        This is a fallback method when jdatetime is not available.
        DO NOT use in production - install jdatetime instead!

        Args:
            greg_date: Gregorian date

        Returns:
            Approximate Jalali date
        """
        # Very rough approximation
        # Jalali calendar is approximately 621 years behind Gregorian
        year = greg_date.year - 621

        # Adjust for the fact that Jalali year starts around March 21
        if greg_date.month < 3 or (greg_date.month == 3 and greg_date.day < 21):
            year -= 1

        # This is NOT accurate and should be replaced
        month = greg_date.month
        day = greg_date.day

        return (year, month, day)


def main():
    """Example usage"""
    print("Jalali Calendar Converter")
    print("=" * 50)

    # Test conversions
    test_dates = [
        date(2024, 1, 15),
        date(2024, 3, 20),
        date(2024, 12, 31),
    ]

    for greg_date in test_dates:
        year, month, day = JalaliConverter.gregorian_to_jalali(greg_date)
        jalali_str = JalaliConverter.format_jalali_date(year, month, day)
        month_name = JalaliConverter.jalali_month_name(month, 'fa')

        print(f"\nGregorian: {greg_date}")
        print(f"Jalali: {year}/{month:02d}/{day:02d}")
        print(f"Formatted: {jalali_str}")
        print(f"Month: {month_name}")
        print(f"Is leap year: {JalaliConverter.is_jalali_leap_year(year)}")

    # Test validation
    print("\n" + "=" * 50)
    print("Validation Tests:")
    test_jalali_dates = [
        (1402, 1, 1, "Valid"),
        (1402, 12, 30, "Valid (leap year)"),
        (1402, 12, 31, "Invalid (not leap)"),
        (1402, 7, 31, "Invalid (Mehr has 30 days)"),
    ]

    for year, month, day, expected in test_jalali_dates:
        is_valid = JalaliConverter.validate_jalali_date(year, month, day)
        status = "✓" if is_valid else "✗"
        print(f"{status} {year}/{month:02d}/{day:02d} - {expected}")


if __name__ == '__main__':
    main()
