#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP XLS to DBF Converter
تبدیل مستقیم فایل‌های XLS خروجی SAP به DBF با Iran System encoding

Usage:
    python sap_xls_to_dbf.py <kar_xls> <wor_xls> <output_dir>

Arguments:
    kar_xls    : فایل DSKKAR00.XLS از SAP
    wor_xls    : فایل DSKWOR00.XLS از SAP
    output_dir : مسیر خروجی فایل‌های DBF

Output:
    output_dir/DSKKAR00.DBF
    output_dir/DSKWOR00.DBF

Exit Codes:
    0 - Success
    1 - Missing arguments
    2 - File not found
    3 - Conversion error
"""

import sys
import os
from pathlib import Path
import logging
import csv
import re
import pandas as pd

# Setup logging
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


def decode_unicode_escape(value):
    """
    تبدیل Unicode escape sequences به کاراکترهای فارسی
    مثال: "\\u0645\\u062d\\u0645\\u062f" → "محمد"
    """
    if not isinstance(value, str):
        return value

    if '\\u' not in value:
        return value

    try:
        # Replace \uXXXX patterns with actual Unicode characters
        # Pattern: \u followed by hex digits (either 2 or 4 digits)
        def replace_unicode_escape(match):
            hex_str = match.group(1)
            # Convert hex string to integer, then to character
            code_point = int(hex_str, 16)
            return chr(code_point)

        # Match \u followed by hex digits
        decoded = re.sub(r'\\u([0-9A-Fa-f]+)', replace_unicode_escape, value)
        return decoded

    except Exception as e:
        logger.warning(f"Error decoding unicode escape '{value}': {e}")
        return value


def evaluate_excel_formula(value):
    """
    ارزیابی فرمول‌های Excel مانند:
    =REPT(0,10-LEN("0853900011"))&"0853900011" → "0853900011"
    =REPT(0,2-LEN("04"))&"04" → "04"
    =REPT(0,11)&"1" → "00000000001"
    """
    if not isinstance(value, str):
        return value

    value = str(value).strip()

    # اگر فرمول Excel نیست، همان را برگردان
    if not value.startswith('=REPT'):
        return value

    try:
        # Pattern 1: =REPT(0,N-LEN("VALUE"))&"VALUE"
        match1 = re.match(r'=REPT\(0,(\d+)-LEN\("([^"]+)"\)\)&"([^"]+)"', value)
        if match1:
            width = int(match1.group(1))
            text_value = match1.group(3)
            return text_value.zfill(width)

        # Pattern 2: =REPT(0,N)&"VALUE"
        match2 = re.match(r'=REPT\(0,(\d+)\)&"([^"]*)"', value)
        if match2:
            width = int(match2.group(1))
            text_value = match2.group(2) if match2.group(2) else ''
            # اگر مقدار خالی است، فقط صفرها را برگردان
            if not text_value:
                return '0' * width
            return ('0' * width) + text_value

        # Pattern 3: =REPT(0,N)
        match3 = re.match(r'=REPT\(0,(\d+)\)', value)
        if match3:
            width = int(match3.group(1))
            return '0' * width

        logger.warning(f"Unknown formula pattern: {value}")
        return value

    except Exception as e:
        logger.warning(f"Error evaluating formula '{value}': {e}")
        return value


def read_sap_xls(file_path):
    """
    خواندن فایل XLS خروجی SAP (که در واقع tab-delimited است)
    و تبدیل فرمول‌های Excel به مقادیر واقعی
    """
    logger.info(f"Reading SAP XLS file: {file_path}")

    try:
        # Try different encodings to find the right one
        encodings_to_try = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
        df = None

        for enc in encodings_to_try:
            try:
                df = pd.read_csv(file_path, sep='\t', encoding=enc)
                logger.info(f"Successfully read with encoding: {enc}")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if df is None:
            raise Exception("Could not read file with any known encoding")

        logger.info(f"  Rows: {len(df)}, Columns: {len(df.columns)}")

        # ارزیابی فرمول‌های Excel در تمام ستون‌ها
        for col in df.columns:
            df[col] = df[col].apply(evaluate_excel_formula)

        # حذف فضاهای اضافی از نام ستون‌ها
        df.columns = df.columns.str.strip()

        return df

    except Exception as e:
        logger.error(f"Error reading XLS file: {e}")
        raise


def convert_df_to_csv(df, output_csv):
    """تبدیل DataFrame به CSV برای استفاده در csv_to_dbf_complete.py"""
    logger.info(f"Writing temporary CSV: {output_csv}")

    # نوشتن به CSV با UTF-8
    df.to_csv(output_csv, index=False, encoding='utf-8')

    logger.info(f"  Written {len(df)} rows")


def import_converter():
    """Import ماژول تبدیل DBF"""
    try:
        # تلاش برای پیدا کردن مسیر صحیح
        script_dir = Path(__file__).resolve().parent

        # مسیرهای احتمالی
        possible_paths = [
            script_dir.parent,  # اگر در sap_integration/ باشیم
            script_dir,  # اگر در root باشیم
            Path.cwd(),  # مسیر فعلی
        ]

        # افزودن مسیرها به sys.path
        tools_found = False
        for path in possible_paths:
            tools_path = path / 'tools'
            if tools_path.exists():
                sys.path.insert(0, str(path))
                sys.path.insert(0, str(tools_path))
                logger.info(f"Found tools directory: {tools_path}")
                tools_found = True
                break

        if not tools_found:
            raise ImportError("tools/ directory not found in any expected location")

        from csv_to_dbf_complete import CompleteDBFConverter
        logger.info("Successfully imported conversion modules")
        return CompleteDBFConverter

    except ImportError as e:
        logger.error(f"Failed to import conversion modules: {e}")
        logger.error(f"Script location: {Path(__file__).resolve()}")
        logger.error(f"Current directory: {Path.cwd()}")
        logger.error(f"sys.path: {sys.path}")
        logger.error("")
        logger.error("=" * 80)
        logger.error("خطا: فایل‌های مورد نیاز یافت نشدند!")
        logger.error("=" * 80)
        logger.error("")
        logger.error("لطفاً مطمئن شوید که ساختار زیر وجود دارد:")
        logger.error("")
        logger.error("  <directory>/")
        logger.error("    ├── tools/")
        logger.error("    │   └── csv_to_dbf_complete.py")
        logger.error("    ├── src/")
        logger.error("    │   └── utils/")
        logger.error("    │       └── iran_system_encoding.py")
        logger.error("    └── sap_xls_to_dbf.py")
        logger.error("")
        logger.error("برای راهنمای نصب، فایل OFFLINE_INSTALLATION.md را مطالعه کنید.")
        logger.error("=" * 80)
        return None


def main():
    """تابع اصلی"""
    logger.info("=" * 80)
    logger.info("SAP XLS to DBF Converter Started")
    logger.info(f"Arguments: {sys.argv[1:]}")
    logger.info("=" * 80)

    # بررسی آرگومان‌ها
    if len(sys.argv) != 4:
        logger.error("Expected 3 arguments")
        logger.error("Usage: sap_xls_to_dbf.py <kar_xls> <wor_xls> <output_dir>")
        sys.exit(1)

    kar_xls = Path(sys.argv[1])
    wor_xls = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    # بررسی وجود فایل‌ها
    if not kar_xls.exists():
        logger.error(f"KAR XLS not found: {kar_xls}")
        sys.exit(2)

    if not wor_xls.exists():
        logger.error(f"WOR XLS not found: {wor_xls}")
        sys.exit(2)

    # ایجاد دایرکتوری خروجی
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # خواندن فایل‌های XLS
        logger.info("Step 1: Reading SAP XLS files...")
        kar_df = read_sap_xls(kar_xls)
        wor_df = read_sap_xls(wor_xls)

        # ایجاد فایل‌های CSV موقت
        temp_kar_csv = output_dir / 'temp_kar.csv'
        temp_wor_csv = output_dir / 'temp_wor.csv'

        logger.info("Step 2: Converting to temporary CSV...")
        convert_df_to_csv(kar_df, temp_kar_csv)
        convert_df_to_csv(wor_df, temp_wor_csv)

        # Import ماژول تبدیل
        CompleteDBFConverter = import_converter()
        if CompleteDBFConverter is None:
            logger.error("Cannot proceed without converter modules")
            sys.exit(3)

        # تبدیل CSV به DBF
        logger.info("Step 3: Converting CSV to DBF with Iran System encoding...")

        # ایجاد converter instance
        converter = CompleteDBFConverter()

        # خواندن CSV ها
        header_data = converter.read_csv(str(temp_kar_csv))[0]  # فقط ردیف اول
        workers_data = converter.read_csv(str(temp_wor_csv))

        logger.info(f"  Loaded header + {len(workers_data)} workers")

        # استخراج year, month, workshop_id از داده‌ها
        year = int(header_data.get('DSK_YY', '0'))
        month = int(header_data.get('DSK_MM', '0'))
        workshop_id = header_data.get('DSK_ID', '').zfill(10)
        list_no = header_data.get('DSK_LISTNO', '').zfill(11)

        logger.info(f"  Workshop: {workshop_id}, Year: {year}, Month: {month}")

        # ایجاد فایل‌های DBF
        converter.create_header_file(
            str(output_dir / 'DSKKAR00.DBF'),
            header_data,
            workers_data,
            year,
            month
        )

        converter.create_workers_file(
            str(output_dir / 'DSKWOR00.DBF'),
            workers_data,
            workshop_id,
            year,
            month,
            list_no
        )

        result = True
        if result:
            kar_dbf = output_dir / 'DSKKAR00.DBF'
            wor_dbf = output_dir / 'DSKWOR00.DBF'

            logger.info("✅ Conversion successful!")
            logger.info(f"  Created: {kar_dbf} ({kar_dbf.stat().st_size} bytes)")
            logger.info(f"  Created: {wor_dbf} ({wor_dbf.stat().st_size} bytes)")

            # پاکسازی فایل‌های موقت
            logger.info("Step 4: Cleaning up temporary files...")
            temp_kar_csv.unlink()
            temp_wor_csv.unlink()
            logger.info("  Temporary files removed")

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
