#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iran System Encoding Converter
تبدیل‌کننده کدگذاری سیستم ایران

This module converts Persian text from Windows-1256 to the custom Iran System encoding
used in DBF files for Iranian Social Security Organization.

Based on the C# implementation from:
https://github.com/amirfahmideh/InsuranceToDbf/blob/master/InsuranceToDbf/Convertor/ConvertWindowsPersianToDos.cs
"""

from typing import Dict, List


class IranSystemEncoder:
    """
    Converter for Persian text to Iran System encoding used in Social Security DBF files

    This implements a context-sensitive Persian character mapping where each character
    can have up to 4 different representations depending on its position:
    - Group 1: Isolated (both sides have space or final letters)
    - Group 2: Final form (left has space, right has connecting letter)
    - Group 3: Initial form (left has connecting letter, right has space)
    - Group 4: Medial form (both sides have connecting letters)
    """

    # Group 1: Isolated form (both neighbors are space or final letters)
    MAPPER_GROUP1 = {
        48: 128,   # 0
        49: 129,   # 1
        50: 130,   # 2
        51: 131,   # 3
        52: 132,   # 4
        53: 133,   # 5
        54: 134,   # 6
        55: 135,   # 7
        56: 136,   # 8
        57: 137,   # 9
        161: 138,  # ،
        191: 140,  # ؟
        193: 143,  # ء
        194: 141,  # آ
        195: 144,  # أ
        196: 248,  # ؤ
        197: 144,  # إ
        200: 146,  # ب
        201: 249,  # ة
        202: 150,  # ت
        203: 152,  # ث
        204: 154,  # ج
        205: 158,  # ح
        206: 160,  # خ
        207: 162,  # د
        208: 163,  # ذ
        209: 164,  # ر
        210: 165,  # ز
        211: 167,  # س
        212: 169,  # ش
        213: 171,  # ص
        214: 173,  # ض
        216: 175,  # ط
        217: 224,  # ظ
        218: 225,  # ع
        219: 229,  # غ
        220: 139,  # -
        221: 233,  # ف
        222: 235,  # ق
        223: 237,  # ك
        225: 241,  # ل
        227: 244,  # م
        228: 246,  # ن
        229: 249,  # ه
        230: 248,  # و
        236: 253,  # ى
        237: 253,  # ي
        129: 148,  # پ
        141: 156,  # چ
        142: 166,  # ژ
        152: 237,  # ک
        144: 239,  # گ
    }

    # Group 2: Final form
    MAPPER_GROUP2 = {
        48: 128, 49: 129, 50: 130, 51: 131, 52: 132,
        53: 133, 54: 134, 55: 135, 56: 136, 57: 137,
        161: 138, 191: 140, 193: 143, 194: 141, 195: 144,
        196: 248, 197: 144, 198: 254, 199: 144, 200: 147,
        201: 251, 202: 151, 203: 153, 204: 155, 205: 159,
        206: 161, 207: 162, 208: 163, 209: 164, 210: 165,
        211: 168, 212: 170, 213: 172, 214: 174, 216: 175,
        217: 224, 218: 228, 219: 232, 220: 139, 221: 234,
        222: 236, 223: 238, 225: 243, 227: 245, 228: 247,
        229: 251, 230: 248, 236: 254, 237: 254, 129: 149,
        141: 157, 142: 166, 152: 238, 144: 240,
    }

    # Group 3: Initial form
    MAPPER_GROUP3 = {
        48: 128, 49: 129, 50: 130, 51: 131, 52: 132,
        53: 133, 54: 134, 55: 135, 56: 136, 57: 137,
        161: 138, 191: 140, 193: 143, 194: 141, 195: 145,
        196: 248, 197: 145, 198: 252, 199: 145, 200: 146,
        201: 249, 202: 150, 203: 152, 204: 154, 205: 158,
        206: 160, 207: 162, 208: 163, 209: 164, 210: 165,
        211: 167, 212: 169, 213: 171, 214: 173, 216: 175,
        217: 224, 218: 226, 219: 230, 220: 139, 221: 233,
        222: 235, 223: 237, 225: 241, 227: 244, 228: 246,
        229: 249, 230: 248, 236: 252, 237: 252, 129: 148,
        141: 156, 142: 166, 152: 237, 144: 239,
    }

    # Group 4: Medial form
    MAPPER_GROUP4 = {
        48: 128, 49: 129, 50: 130, 51: 131, 52: 132,
        53: 133, 54: 134, 55: 135, 56: 136, 57: 137,
        161: 138, 191: 140, 193: 143, 194: 141, 195: 145,
        196: 248, 197: 145, 198: 142, 199: 145, 200: 147,
        201: 250, 202: 151, 203: 153, 204: 155, 205: 159,
        206: 161, 207: 162, 208: 163, 209: 164, 210: 165,
        211: 168, 212: 170, 213: 172, 214: 174, 216: 175,
        217: 224, 218: 227, 219: 231, 220: 139, 221: 234,
        222: 236, 223: 238, 225: 243, 227: 245, 228: 247,
        229: 250, 230: 248, 236: 254, 237: 254, 129: 149,
        141: 157, 142: 166, 152: 238, 144: 240,
    }

    # Final letters that don't connect to the left
    FINAL_LETTERS = "ءآأؤإادذرزژو"

    @staticmethod
    def is_latin_letter(c: int) -> bool:
        """Check if byte is a Latin letter"""
        return 31 < c < 128

    @staticmethod
    def is_number(text: str) -> bool:
        """Check if text contains only numbers"""
        return text.strip().replace(' ', '').isdigit()

    @staticmethod
    def get_latin_letter(c: int) -> int:
        """Convert Latin numbers and symbols"""
        char = chr(c)
        if char in "0123456789":
            return c + 80

        # Farsi exceptions (mirror brackets)
        mirror_map = {
            ord('('): ord(')'),
            ord('{'): ord('}'),
            ord('['): ord(']'),
            ord(')'): ord('('),
            ord('}'): ord('{'),
            ord(']'): ord('['),
        }
        return mirror_map.get(c, c)

    @staticmethod
    def is_final_letter(c: int) -> bool:
        """Check if character is a final letter (doesn't connect to left)"""
        try:
            char = chr(c)
            return char in IranSystemEncoder.FINAL_LETTERS
        except:
            return False

    @staticmethod
    def is_white_letter(c: int) -> bool:
        """Check if character is whitespace"""
        return c in (8, 9, 10, 13, 27, 32, 0)

    @staticmethod
    def char_cond(c: int) -> bool:
        """Check character condition for grouping"""
        return (IranSystemEncoder.is_white_letter(c) or
                IranSystemEncoder.is_latin_letter(c) or
                c == 191)

    @staticmethod
    def normalize_persian(text: str) -> str:
        """Normalize Persian characters to Windows-1256 compatible ones"""
        # Map Persian-specific chars to Arabic equivalents in Windows-1256
        replacements = {
            '\u06CC': '\u064A',  # ی Persian -> ي Arabic
            '\u06A9': '\u0643',  # ک Persian -> ك Arabic
            '\u06AF': '\u06AF',  # گ (keep as is, handled in mapper)
            '\u067E': '\u067E',  # پ (keep as is, handled in mapper)
            '\u0686': '\u0686',  # چ (keep as is, handled in mapper)
            '\u0698': '\u0698',  # ژ (keep as is, handled in mapper)
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result

    @staticmethod
    def unicode_to_iran_system(text: str) -> bytes:
        """
        Convert Unicode Persian text to Iran System encoding

        Args:
            text: Persian text in Unicode

        Returns:
            Bytes in Iran System encoding
        """
        # Normalize Persian characters
        normalized = IranSystemEncoder.normalize_persian(text)

        # Add spaces at beginning and end
        padded_text = " " + normalized + " "

        # Convert to Windows-1256
        try:
            win1256_bytes = padded_text.encode('windows-1256', errors='replace')
        except:
            # Fallback to cp1256
            win1256_bytes = padded_text.encode('cp1256', errors='replace')

        result = []
        prev_char = 0

        for i in range(len(win1256_bytes)):
            byte_val = win1256_bytes[i]

            if IranSystemEncoder.is_latin_letter(byte_val):
                cur = IranSystemEncoder.get_latin_letter(byte_val)
                result.append(cur)
                prev_char = cur
            elif i > 0 and i < len(win1256_bytes) - 1:
                prev_byte = win1256_bytes[i - 1]
                next_byte = win1256_bytes[i + 1]

                cur = IranSystemEncoder.get_iran_system_char(
                    prev_byte, byte_val, next_byte
                )

                # Special handling for لا (LA)
                if cur == 145 and prev_char == 243:
                    result[-1] = 242
                else:
                    result.append(cur)

                prev_char = cur

        # Remove padding
        if len(result) > 2:
            result = result[1:-1]

        # Reverse for RTL (unless it's a number)
        if not IranSystemEncoder.is_number(text):
            result.reverse()

        return bytes(result)

    @staticmethod
    def get_iran_system_char(prev_char: int, cur_char: int, next_char: int) -> int:
        """
        Get Iran System encoding for character based on context

        Args:
            prev_char: Previous character byte
            cur_char: Current character byte
            next_char: Next character byte

        Returns:
            Iran System byte value
        """
        prev_flag = (IranSystemEncoder.char_cond(prev_char) or
                     IranSystemEncoder.is_final_letter(prev_char))
        next_flag = IranSystemEncoder.char_cond(next_char)

        if prev_flag and next_flag:
            # Isolated
            return IranSystemEncoder.MAPPER_GROUP1.get(cur_char, cur_char)
        elif prev_flag:
            # Final
            return IranSystemEncoder.MAPPER_GROUP2.get(cur_char, cur_char)
        elif next_flag:
            # Initial
            return IranSystemEncoder.MAPPER_GROUP3.get(cur_char, cur_char)
        else:
            # Medial
            return IranSystemEncoder.MAPPER_GROUP4.get(cur_char, cur_char)


def test_encoder():
    """Test the encoder with some examples"""
    encoder = IranSystemEncoder()

    test_cases = [
        "علی",
        "احمدی",
        "محمد",
        "فاطمه",
    ]

    print("=" * 80)
    print("🧪 تست Iran System Encoder")
    print("=" * 80)
    print()

    for text in test_cases:
        result = encoder.unicode_to_iran_system(text)
        print(f"Input:  {text}")
        print(f"Output: {result.hex()}")
        print(f"Bytes:  {list(result)}")
        print()


if __name__ == '__main__':
    test_encoder()
