#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP to DBF Standalone Converter
اسکریپت یکپارچه برای تبدیل فایل‌های XLS از SAP به DBF با Iran System encoding

این اسکریپت همه چیز رو داخل خودش داره و نیازی به فایل‌های اضافی نداره!

Usage:
    python3 sap_to_dbf_standalone.py DSKKAR00.XLS DSKWOR00.XLS /output/dir/
"""

import sys
import struct
import csv
import re
from pathlib import Path
import logging

# فقط pandas و openpyxl نیاز داره (که با pip نصب شدن)
try:
    import pandas as pd
except ImportError:
    print("❌ خطا: pandas نصب نیست!")
    print("لطفاً با دستور زیر نصب کنید:")
    print("  pip3 install 'pandas<2.0' 'openpyxl<3.1' 'xlrd<2.0'")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Iran System Encoding (کپی شده از iran_system_encoding.py)
# ============================================================================

class IranSystemEncoder:
    """تبدیل متن فارسی به Iran System encoding"""

    def __init__(self):
        # جدول تبدیل حروف فارسی به Iran System encoding
        self.persian_map = {
            # حروف اصلی
            'ا': {'isolated': 0x80, 'final': 0x81},
            'آ': {'isolated': 0x82, 'final': 0x83},
            'ب': {'isolated': 0x84, 'final': 0x85, 'initial': 0x86, 'medial': 0x87},
            'پ': {'isolated': 0x88, 'final': 0x89, 'initial': 0x8A, 'medial': 0x8B},
            'ت': {'isolated': 0x8C, 'final': 0x8D, 'initial': 0x8E, 'medial': 0x8F},
            'ث': {'isolated': 0x90, 'final': 0x91, 'initial': 0x92, 'medial': 0x93},
            'ج': {'isolated': 0x94, 'final': 0x95, 'initial': 0x96, 'medial': 0x97},
            'چ': {'isolated': 0x98, 'final': 0x99, 'initial': 0x9A, 'medial': 0x9B},
            'ح': {'isolated': 0x9C, 'final': 0x9D, 'initial': 0x9E, 'medial': 0x9F},
            'خ': {'isolated': 0xA0, 'final': 0xA1, 'initial': 0xA2, 'medial': 0xA3},
            'د': {'isolated': 0xA4, 'final': 0xA5},
            'ذ': {'isolated': 0xA6, 'final': 0xA7},
            'ر': {'isolated': 0xA8, 'final': 0xA9},
            'ز': {'isolated': 0xAA, 'final': 0xAB},
            'ژ': {'isolated': 0xAC, 'final': 0xAD},
            'س': {'isolated': 0xAE, 'final': 0xAF, 'initial': 0xB0, 'medial': 0xB1},
            'ش': {'isolated': 0xB2, 'final': 0xB3, 'initial': 0xB4, 'medial': 0xB5},
            'ص': {'isolated': 0xB6, 'final': 0xB7, 'initial': 0xB8, 'medial': 0xB9},
            'ض': {'isolated': 0xBA, 'final': 0xBB, 'initial': 0xBC, 'medial': 0xBD},
            'ط': {'isolated': 0xBE, 'final': 0xBF, 'initial': 0xC0, 'medial': 0xC1},
            'ظ': {'isolated': 0xC2, 'final': 0xC3, 'initial': 0xC4, 'medial': 0xC5},
            'ع': {'isolated': 0xC6, 'final': 0xC7, 'initial': 0xC8, 'medial': 0xC9},
            'غ': {'isolated': 0xCA, 'final': 0xCB, 'initial': 0xCC, 'medial': 0xCD},
            'ف': {'isolated': 0xCE, 'final': 0xCF, 'initial': 0xD0, 'medial': 0xD1},
            'ق': {'isolated': 0xD2, 'final': 0xD3, 'initial': 0xD4, 'medial': 0xD5},
            'ک': {'isolated': 0xD6, 'final': 0xD7, 'initial': 0xD8, 'medial': 0xD9},
            'گ': {'isolated': 0xDA, 'final': 0xDB, 'initial': 0xDC, 'medial': 0xDD},
            'ل': {'isolated': 0xDE, 'final': 0xDF, 'initial': 0xE0, 'medial': 0xE1},
            'م': {'isolated': 0xE2, 'final': 0xE3, 'initial': 0xE4, 'medial': 0xE5},
            'ن': {'isolated': 0xE6, 'final': 0xE7, 'initial': 0xE8, 'medial': 0xE9},
            'و': {'isolated': 0xEA, 'final': 0xEB},
            'ه': {'isolated': 0xEC, 'final': 0xED, 'initial': 0xEE, 'medial': 0xEF},
            'ی': {'isolated': 0xF0, 'final': 0xF1, 'initial': 0xF2, 'medial': 0xF3},
            'ئ': {'isolated': 0xF4, 'final': 0xF5, 'initial': 0xF6, 'medial': 0xF7},
        }

        # حروفی که به بعدی وصل می‌شوند
        self.joining_chars = set(self.persian_map.keys()) - {'ا', 'آ', 'د', 'ذ', 'ر', 'ز', 'ژ', 'و'}

    def normalize_digits(self, text):
        """تبدیل اعداد فارسی به انگلیسی"""
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        trans_table = str.maketrans(persian_digits, english_digits)
        return text.translate(trans_table)

    def get_char_form(self, char, prev_char, next_char):
        """تشخیص فرم حرف (isolated, initial, medial, final)"""
        if char not in self.persian_map:
            return 'isolated'

        can_join_prev = prev_char in self.joining_chars if prev_char else False
        can_join_next = next_char in self.joining_chars if next_char else False

        if can_join_prev and can_join_next:
            return 'medial'
        elif can_join_prev:
            return 'final'
        elif can_join_next:
            return 'initial'
        else:
            return 'isolated'

    def encode(self, text):
        """تبدیل متن فارسی به Iran System encoding"""
        if not text:
            return b''

        # تبدیل اعداد فارسی
        text = self.normalize_digits(str(text))

        # معکوس کردن ترتیب کاراکترها (visual order)
        text = text[::-1]

        result = bytearray()

        for i, char in enumerate(text):
            if char in self.persian_map:
                prev_char = text[i-1] if i > 0 else None
                next_char = text[i+1] if i < len(text)-1 else None

                form = self.get_char_form(char, prev_char, next_char)
                char_map = self.persian_map[char]

                # اگر فرم مورد نظر وجود نداره، از isolated استفاده کن
                byte_value = char_map.get(form, char_map.get('isolated', 0x20))
                result.append(byte_value)
            else:
                # کاراکترهای غیر فارسی (اعداد، فضا، علائم)
                result.append(ord(char) if ord(char) < 128 else 0x20)

        return bytes(result)

# ============================================================================
# DBF Creator (کپی شده از csv_to_dbf_complete.py)
# ============================================================================

class DBFCreator:
    """ایجاد فایل DBF با Iran System encoding"""

    def __init__(self):
        self.encoder = IranSystemEncoder()

    def create_header_file(self, output_file, header_data, workers_data, year, month):
        """ایجاد فایل header (DSKKAR00.DBF)"""
        logger.info(f"Creating header file: {output_file}")

        # SSO 2024 structure: 25 fields
        fields = [
            ('DSK_ID', 'C', 10, 0),       # Workshop ID
            ('DSK_NAME', 'C', 30, 0),     # Workshop name (Persian) - Changed: 60→30
            ('DSK_FARM', 'C', 30, 0),     # Employer name (Persian) - Changed: 60→30
            ('DSK_ADRS', 'C', 40, 0),     # Address (Persian) - Changed: 100→40
            ('DSK_KIND', 'N', 1, 0),      # Kind
            ('DSK_YY', 'N', 2, 0),        # Year - Changed: C→N
            ('DSK_MM', 'N', 2, 0),        # Month - Changed: C→N
            ('DSK_LISTNO', 'C', 12, 0),   # List number - Changed: 11→12
            ('DSK_DISC', 'C', 30, 0),     # Description (Persian) - Changed: 11→30
            ('DSK_NUM', 'N', 5, 0),       # Number of workers
            ('DSK_TDD', 'N', 6, 0),       # Total days - Changed: 5→6
            ('DSK_TROOZ', 'N', 12, 0),    # Total daily wage - Changed: 13→12
            ('DSK_TMAH', 'N', 12, 0),     # Total monthly wage - Changed: 13→12
            ('DSK_TMAZ', 'N', 12, 0),     # Total benefits - Changed: 13→12
            ('DSK_TMASH', 'N', 12, 0),    # Total insurable - Changed: 13→12
            ('DSK_TTOTL', 'N', 12, 0),    # Total amount - Changed: 13→12
            ('DSK_TBIME', 'N', 12, 0),    # Total insurance - Changed: 13→12
            ('DSK_TKOSO', 'N', 12, 0),    # Total deductions - Changed: 13→12
            ('DSK_BIC', 'N', 12, 0),      # BIC code - Changed: 13→12
            ('DSK_RATE', 'N', 5, 0),      # Rate - Changed: 2→5
            ('DSK_PRATE', 'N', 2, 0),     # Rate percentage
            ('DSK_BIMH', 'N', 12, 0),     # Insurance premium - Changed: 13→12
            ('MON_PYM', 'C', 3, 0),       # Payment month - Changed: N→C, 2→3
            ('DSK_INC', 'N', 12, 0),      # Total INC (جمع پایه سنواتی) - Excel: DSK_TINC
            ('DSK_SPOUSE', 'N', 12, 0),   # Total SPOUS (جمع حق تاهل) - Excel: DSK_TSPOUS
        ]

        # Map Excel field names to SSO field names
        mapped_header = dict(header_data)
        if 'DSK_TINC' in mapped_header:
            mapped_header['DSK_INC'] = mapped_header['DSK_TINC']
        if 'DSK_TSPOUS' in mapped_header:
            mapped_header['DSK_SPOUSE'] = mapped_header['DSK_TSPOUS']

        self._write_dbf(output_file, fields, [mapped_header])
        logger.info(f"✅ Header file created: {output_file}")

    def create_workers_file(self, output_file, workers_data, workshop_id, year, month, list_no):
        """ایجاد فایل workers (DSKWOR00.DBF)"""
        logger.info(f"Creating workers file: {output_file}")
        logger.info(f"  Workers count: {len(workers_data)}")

        # SSO 2024 structure: 29 fields
        fields = [
            ('DSW_ID', 'C', 10, 0),
            ('DSW_YY', 'C', 2, 0),
            ('DSW_MM', 'C', 2, 0),
            ('DSW_LISTNO', 'C', 11, 0),
            ('DSW_ID1', 'C', 10, 0),
            ('DSW_FNAME', 'C', 30, 0),
            ('DSW_LNAME', 'C', 40, 0),
            ('DSW_DNAME', 'C', 30, 0),
            ('DSW_IDNO', 'C', 20, 0),
            ('DSW_IDPLC', 'C', 30, 0),
            ('DSW_IDATE', 'C', 8, 0),
            ('DSW_BDATE', 'C', 8, 0),
            ('DSW_SEX', 'C', 6, 0),
            ('DSW_NAT', 'C', 12, 0),
            ('DSW_OCP', 'C', 40, 0),
            ('DSW_SDATE', 'C', 8, 0),
            ('DSW_EDATE', 'C', 8, 0),
            ('DSW_DD', 'N', 2, 0),
            ('DSW_ROOZ', 'N', 13, 0),
            ('DSW_MAH', 'N', 13, 0),
            ('DSW_MAZ', 'N', 13, 0),
            ('DSW_MASH', 'N', 13, 0),
            ('DSW_TOTL', 'N', 13, 0),
            ('DSW_BIME', 'N', 13, 0),
            ('DSW_PRATE', 'C', 2, 0),
            ('DSW_JOB', 'C', 6, 0),
            ('PER_NATCOD', 'C', 10, 0),
            ('DSW_INC', 'N', 13, 0),
            ('DSW_SPOUSE', 'N', 13, 0),
        ]

        self._write_dbf(output_file, fields, workers_data)
        logger.info(f"✅ Workers file created: {output_file}")

    def _write_dbf(self, filename, fields, data):
        """نوشتن فایل DBF"""
        with open(filename, 'wb') as f:
            # DBF Header
            num_records = len(data)
            header_size = 32 + (len(fields) * 32) + 1
            record_size = sum(field[2] for field in fields) + 1

            # Version byte + last update date
            f.write(struct.pack('<B', 0x03))
            f.write(struct.pack('<BBB', 25, 11, 28))

            # Number of records + header size + record size
            f.write(struct.pack('<I', num_records))
            f.write(struct.pack('<H', header_size))
            f.write(struct.pack('<H', record_size))

            # Reserved bytes
            f.write(b'\x00' * 16)

            # Language driver ID (0x7E for Iran System)
            f.write(b'\x7E')

            # Reserved bytes
            f.write(b'\x00' * 3)

            # Field descriptors
            for field_name, field_type, field_length, field_decimal in fields:
                f.write(field_name.ljust(11, '\x00').encode('ascii'))
                f.write(field_type.encode('ascii'))
                f.write(b'\x00' * 4)
                f.write(struct.pack('<B', field_length))
                f.write(struct.pack('<B', field_decimal))
                f.write(b'\x00' * 14)

            # Header terminator
            f.write(b'\x0D')

            # Records
            for record in data:
                f.write(b' ')  # Deletion flag
                for field_name, field_type, field_length, field_decimal in fields:
                    value = record.get(field_name, '')

                    if field_type == 'C':
                        # Text field با Iran System encoding
                        # Special handling for MON_PYM: keep it empty if value is 0 or empty
                        if field_name == 'MON_PYM' and (not value or value == 0 or str(value).strip() == '0'):
                            f.write(b' ' * field_length)
                        elif value and str(value).strip():
                            encoded = self.encoder.encode(str(value))
                            if len(encoded) > field_length:
                                encoded = encoded[:field_length]
                            elif len(encoded) < field_length:
                                encoded = encoded + (b' ' * (field_length - len(encoded)))
                            f.write(encoded)
                        else:
                            f.write(b' ' * field_length)
                    elif field_type == 'N':
                        # Numeric field
                        try:
                            if field_decimal > 0:
                                num_str = f"{float(value):{field_length}.{field_decimal}f}"
                            else:
                                num_str = f"{int(float(value) if value else 0):>{field_length}d}"
                        except:
                            num_str = ' ' * field_length
                        f.write(num_str[:field_length].rjust(field_length).encode('ascii'))

            # End of file marker
            f.write(b'\x1A')

# ============================================================================
# Main Converter
# ============================================================================

def evaluate_excel_formula(value):
    """ارزیابی فرمول‌های Excel"""
    if not isinstance(value, str):
        return value

    value = str(value).strip()
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
            if not text_value:
                return '0' * width
            return ('0' * width) + text_value

        # Pattern 3: =REPT(0,N)
        match3 = re.match(r'=REPT\(0,(\d+)\)', value)
        if match3:
            width = int(match3.group(1))
            return '0' * width

        return value
    except:
        return value

def read_sap_xls(file_path):
    """خواندن فایل XLS از SAP (UTF-16LE با BOM)"""
    logger.info(f"Reading: {file_path}")
    df = pd.read_csv(file_path, sep='\t', encoding='utf-16')

    # ارزیابی فرمول‌های Excel
    for col in df.columns:
        df[col] = df[col].apply(evaluate_excel_formula)

    df.columns = df.columns.str.strip()
    logger.info(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
    return df

def main():
    """تابع اصلی"""
    logger.info("=" * 80)
    logger.info("SAP to DBF Standalone Converter")
    logger.info("=" * 80)

    if len(sys.argv) != 4:
        logger.error("Usage: python3 sap_to_dbf_standalone.py <kar_xls> <wor_xls> <output_dir>")
        sys.exit(1)

    kar_xls = Path(sys.argv[1])
    wor_xls = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    # بررسی فایل‌ها
    if not kar_xls.exists():
        logger.error(f"File not found: {kar_xls}")
        sys.exit(2)
    if not wor_xls.exists():
        logger.error(f"File not found: {wor_xls}")
        sys.exit(2)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # خواندن فایل‌ها
        logger.info("Step 1: Reading XLS files...")
        kar_df = read_sap_xls(kar_xls)
        wor_df = read_sap_xls(wor_xls)

        # آماده‌سازی داده‌ها
        logger.info("Step 2: Preparing data...")
        header_data = kar_df.to_dict('records')[0]
        workers_data = wor_df.to_dict('records')

        # استخراج پارامترها
        year = int(header_data.get('DSK_YY', '0'))
        month = int(header_data.get('DSK_MM', '0'))
        workshop_id = header_data.get('DSK_ID', '').zfill(10)
        list_no = header_data.get('DSK_LISTNO', '').zfill(11)

        logger.info(f"  Workshop: {workshop_id}, Year: {year}, Month: {month}")
        logger.info(f"  Workers: {len(workers_data)}")

        # ایجاد DBF
        logger.info("Step 3: Creating DBF files...")
        creator = DBFCreator()

        creator.create_header_file(
            str(output_dir / 'DSKKAR00.DBF'),
            header_data,
            workers_data,
            year,
            month
        )

        creator.create_workers_file(
            str(output_dir / 'DSKWOR00.DBF'),
            workers_data,
            workshop_id,
            year,
            month,
            list_no
        )

        # بررسی نهایی
        kar_dbf = output_dir / 'DSKKAR00.DBF'
        wor_dbf = output_dir / 'DSKWOR00.DBF'

        if kar_dbf.exists() and wor_dbf.exists():
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SUCCESS!")
            logger.info("=" * 80)
            logger.info(f"  DSKKAR00.DBF: {kar_dbf.stat().st_size:,} bytes")
            logger.info(f"  DSKWOR00.DBF: {wor_dbf.stat().st_size:,} bytes")
            logger.info("=" * 80)
            sys.exit(0)
        else:
            logger.error("DBF files not created!")
            sys.exit(3)

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == '__main__':
    main()
