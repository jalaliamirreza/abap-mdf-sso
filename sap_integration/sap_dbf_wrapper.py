#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP DBF Wrapper - Entry point for SAP ABAP External Command
استفاده در SAP: فراخوانی از طریق SM69 External Command

Usage:
    python sap_dbf_wrapper.py <kar_csv> <wor_csv> <output_dir> <workshop_code>

Arguments:
    kar_csv       : مسیر فایل CSV هدر (DSKKAR00)
    wor_csv       : مسیر فایل CSV کارگران (DSKWOR00)
    output_dir    : مسیر خروجی فایل‌های DBF
    workshop_code : کد کارگاه (10 رقمی)

Output:
    output_dir/DSKKAR00.DBF
    output_dir/DSKWOR00.DBF

Exit Codes:
    0  - Success
    1  - Missing arguments
    2  - File not found
    3  - Conversion error
    4  - Invalid workshop code
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Setup logging for SAP monitoring
log_file = Path('/tmp/sap_dbf_converter.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def validate_arguments(args):
    """اعتبارسنجی ورودی‌ها"""
    if len(args) != 5:
        logger.error(f"Expected 4 arguments, got {len(args)-1}")
        logger.error("Usage: sap_dbf_wrapper.py <kar_csv> <wor_csv> <output_dir> <workshop_code>")
        return False

    kar_csv = Path(args[1])
    wor_csv = Path(args[2])
    output_dir = Path(args[3])
    workshop_code = args[4]

    # بررسی وجود فایل‌های CSV
    if not kar_csv.exists():
        logger.error(f"KAR CSV not found: {kar_csv}")
        return False

    if not wor_csv.exists():
        logger.error(f"WOR CSV not found: {wor_csv}")
        return False

    # بررسی دایرکتوری خروجی
    if not output_dir.exists():
        logger.info(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # بررسی کد کارگاه (باید 10 رقم یا کمتر باشد)
    if not workshop_code.isdigit() or len(workshop_code) > 10:
        logger.error(f"Invalid workshop code: {workshop_code} (must be max 10 digits)")
        return False

    return True


def import_converter_modules():
    """Import ماژول‌های تبدیل DBF"""
    try:
        # افزودن مسیر پروژه به sys.path
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir))

        from tools.csv_to_dbf_complete import convert_csv_to_dbf
        logger.info("Successfully imported conversion modules")
        return convert_csv_to_dbf

    except ImportError as e:
        logger.error(f"Failed to import conversion modules: {e}")
        logger.error(f"Script dir: {Path(__file__).parent.parent}")
        logger.error(f"sys.path: {sys.path}")
        return None


def main():
    """تابع اصلی"""
    logger.info("=" * 80)
    logger.info("SAP DBF Wrapper Started")
    logger.info(f"Arguments: {sys.argv[1:]}")
    logger.info("=" * 80)

    # اعتبارسنجی ورودی‌ها
    if not validate_arguments(sys.argv):
        sys.exit(1)

    kar_csv = Path(sys.argv[1])
    wor_csv = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    workshop_code = sys.argv[4]

    # Import ماژول تبدیل
    convert_csv_to_dbf = import_converter_modules()
    if convert_csv_to_dbf is None:
        logger.error("Cannot proceed without converter modules")
        sys.exit(3)

    try:
        # تبدیل CSV به DBF
        logger.info(f"Converting CSV to DBF...")
        logger.info(f"  KAR CSV: {kar_csv}")
        logger.info(f"  WOR CSV: {wor_csv}")
        logger.info(f"  Output: {output_dir}")
        logger.info(f"  Workshop: {workshop_code}")

        result = convert_csv_to_dbf(
            kar_csv=str(kar_csv),
            wor_csv=str(wor_csv),
            output_dir=str(output_dir)
        )

        if result:
            kar_dbf = output_dir / 'DSKKAR00.DBF'
            wor_dbf = output_dir / 'DSKWOR00.DBF'

            logger.info("✅ Conversion successful!")
            logger.info(f"  Created: {kar_dbf} ({kar_dbf.stat().st_size} bytes)")
            logger.info(f"  Created: {wor_dbf} ({wor_dbf.stat().st_size} bytes)")

            # بررسی نهایی
            if kar_dbf.exists() and wor_dbf.exists():
                logger.info("✅ All DBF files verified")
                sys.exit(0)
            else:
                logger.error("❌ DBF files not found after conversion")
                sys.exit(3)
        else:
            logger.error("❌ Conversion failed")
            sys.exit(3)

    except Exception as e:
        logger.error(f"❌ Conversion error: {e}")
        logger.exception("Full traceback:")
        sys.exit(3)


if __name__ == '__main__':
    main()
