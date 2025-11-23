#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iran System to Unicode Decoder
تبدیل‌کننده Iran System به یونیکد

Based on the official Iran System to Unicode mapping table
Reference: http://sina.sharif.ac.ir/~roozbeh/farsiweb/iransystem.txt
Author: Roozbeh Pournader <roozbeh@sina.sharif.ac.ir>
Date: 21 January 2000
"""


class IranSystemDecoder:
    """
    Decoder for converting Iran System encoded bytes to Unicode text

    Iran System is a corporate character set used in Iranian computing,
    particularly for legacy DOS applications and some governmental systems.

    Note: Iran System stores text in VISUAL order, not logical order.
    This means the text is already laid out as it appears on screen.
    """

    # Zero Width Joiner and Non-Joiner
    ZWJ = '\u200D'   # Zero Width Joiner
    ZWNJ = '\u200C'  # Zero Width Non-Joiner

    # Complete Iran System to Unicode mapping table
    # Based on official specification
    IRAN_SYSTEM_TO_UNICODE = {
        # ASCII control characters (0x00-0x1F)
        **{i: chr(i) for i in range(0x20)},

        # ASCII printable characters (0x20-0x7E)
        **{i: chr(i) for i in range(0x20, 0x7F)},

        # Persian/Arabic digits (0x80-0x89)
        0x80: '\u06F0',  # ۰ EXTENDED ARABIC-INDIC DIGIT ZERO
        0x81: '\u06F1',  # ۱ EXTENDED ARABIC-INDIC DIGIT ONE
        0x82: '\u06F2',  # ۲ EXTENDED ARABIC-INDIC DIGIT TWO
        0x83: '\u06F3',  # ۳ EXTENDED ARABIC-INDIC DIGIT THREE
        0x84: '\u06F4',  # ۴ EXTENDED ARABIC-INDIC DIGIT FOUR
        0x85: '\u06F5',  # ۵ EXTENDED ARABIC-INDIC DIGIT FIVE
        0x86: '\u06F6',  # ۶ EXTENDED ARABIC-INDIC DIGIT SIX
        0x87: '\u06F7',  # ۷ EXTENDED ARABIC-INDIC DIGIT SEVEN
        0x88: '\u06F8',  # ۸ EXTENDED ARABIC-INDIC DIGIT EIGHT
        0x89: '\u06F9',  # ۹ EXTENDED ARABIC-INDIC DIGIT NINE

        # Arabic punctuation
        0x8A: '\u060C',  # ، ARABIC COMMA
        0x8B: '\u0640',  # ـ ARABIC TATWEEL
        0x8C: '\u061F',  # ؟ ARABIC QUESTION MARK

        # Arabic letters with context
        0x8D: '\u0622',  # آ ALEF WITH MADDA ABOVE (isolated)
        0x8E: '\u0626',  # ئ YEH WITH HAMZA ABOVE (initial-medial)
        0x8F: '\u0621',  # ء HAMZA
        0x90: '\u0627',  # ا ALEF (isolated)
        0x91: '\u0627',  # ا ALEF (final)

        0x92: '\u0628',  # ب BEH (final-isolated)
        0x93: '\u0628',  # ب BEH (initial-medial)
        0x94: '\u067E',  # پ PEH (final-isolated)
        0x95: '\u067E',  # پ PEH (initial-medial)
        0x96: '\u062A',  # ت TEH (final-isolated)
        0x97: '\u062A',  # ت TEH (initial-medial)
        0x98: '\u062B',  # ث THEH (final-isolated)
        0x99: '\u062B',  # ث THEH (initial-medial)
        0x9A: '\u062C',  # ج JEEM (final-isolated)
        0x9B: '\u062C',  # ج JEEM (initial-medial)
        0x9C: '\u0686',  # چ TCHEH (final-isolated)
        0x9D: '\u0686',  # چ TCHEH (initial-medial)
        0x9E: '\u062D',  # ح HAH (final-isolated)
        0x9F: '\u062D',  # ح HAH (initial-medial)
        0xA0: '\u062E',  # خ KHAH (final-isolated)
        0xA1: '\u062E',  # خ KHAH (initial-medial)

        0xA2: '\u062F',  # د DAL
        0xA3: '\u0630',  # ذ THAL
        0xA4: '\u0631',  # ر REH
        0xA5: '\u0632',  # ز ZAIN
        0xA6: '\u0698',  # ژ JEH

        0xA7: '\u0633',  # س SEEN (final-isolated)
        0xA8: '\u0633',  # س SEEN (initial-medial)
        0xA9: '\u0634',  # ش SHEEN (final-isolated)
        0xAA: '\u0634',  # ش SHEEN (initial-medial)
        0xAB: '\u0635',  # ص SAD (final-isolated)
        0xAC: '\u0635',  # ص SAD (initial-medial)
        0xAD: '\u0636',  # ض DAD (final-isolated)
        0xAE: '\u0636',  # ض DAD (initial-medial)
        0xAF: '\u0637',  # ط TAH

        # Box drawing characters (0xB0-0xDF)
        0xB0: '\u2591',  # ░ LIGHT SHADE
        0xB1: '\u2592',  # ▒ MEDIUM SHADE
        0xB2: '\u2593',  # ▓ DARK SHADE
        0xB3: '\u2502',  # │ BOX DRAWINGS LIGHT VERTICAL
        0xB4: '\u2524',  # ┤ BOX DRAWINGS LIGHT VERTICAL AND LEFT
        0xB5: '\u2561',  # ╡ BOX DRAWINGS VERTICAL SINGLE AND LEFT DOUBLE
        0xB6: '\u2562',  # ╢ BOX DRAWINGS VERTICAL DOUBLE AND LEFT SINGLE
        0xB7: '\u2556',  # ╖ BOX DRAWINGS DOWN DOUBLE AND LEFT SINGLE
        0xB8: '\u2555',  # ╕ BOX DRAWINGS DOWN SINGLE AND LEFT DOUBLE
        0xB9: '\u2563',  # ╣ BOX DRAWINGS DOUBLE VERTICAL AND LEFT
        0xBA: '\u2551',  # ║ BOX DRAWINGS DOUBLE VERTICAL
        0xBB: '\u2557',  # ╗ BOX DRAWINGS DOUBLE DOWN AND LEFT
        0xBC: '\u255D',  # ╝ BOX DRAWINGS DOUBLE UP AND LEFT
        0xBD: '\u255C',  # ╜ BOX DRAWINGS UP DOUBLE AND LEFT SINGLE
        0xBE: '\u255B',  # ╛ BOX DRAWINGS UP SINGLE AND LEFT DOUBLE
        0xBF: '\u2510',  # ┐ BOX DRAWINGS LIGHT DOWN AND LEFT
        0xC0: '\u2514',  # └ BOX DRAWINGS LIGHT UP AND RIGHT
        0xC1: '\u2534',  # ┴ BOX DRAWINGS LIGHT UP AND HORIZONTAL
        0xC2: '\u252C',  # ┬ BOX DRAWINGS LIGHT DOWN AND HORIZONTAL
        0xC3: '\u251C',  # ├ BOX DRAWINGS LIGHT VERTICAL AND RIGHT
        0xC4: '\u2500',  # ─ BOX DRAWINGS LIGHT HORIZONTAL
        0xC5: '\u253C',  # ┼ BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL
        0xC6: '\u255E',  # ╞ BOX DRAWINGS VERTICAL SINGLE AND RIGHT DOUBLE
        0xC7: '\u255F',  # ╟ BOX DRAWINGS VERTICAL DOUBLE AND RIGHT SINGLE
        0xC8: '\u255A',  # ╚ BOX DRAWINGS DOUBLE UP AND RIGHT
        0xC9: '\u2554',  # ╔ BOX DRAWINGS DOUBLE DOWN AND RIGHT
        0xCA: '\u2569',  # ╩ BOX DRAWINGS DOUBLE UP AND HORIZONTAL
        0xCB: '\u2566',  # ╦ BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL
        0xCC: '\u2560',  # ╠ BOX DRAWINGS DOUBLE VERTICAL AND RIGHT
        0xCD: '\u2550',  # ═ BOX DRAWINGS DOUBLE HORIZONTAL
        0xCE: '\u256C',  # ╬ BOX DRAWINGS DOUBLE VERTICAL AND HORIZONTAL
        0xCF: '\u2567',  # ╧ BOX DRAWINGS UP SINGLE AND HORIZONTAL DOUBLE
        0xD0: '\u2568',  # ╨ BOX DRAWINGS UP DOUBLE AND HORIZONTAL SINGLE
        0xD1: '\u2564',  # ╤ BOX DRAWINGS DOWN SINGLE AND HORIZONTAL DOUBLE
        0xD2: '\u2565',  # ╥ BOX DRAWINGS DOWN DOUBLE AND HORIZONTAL SINGLE
        0xD3: '\u2559',  # ╙ BOX DRAWINGS UP DOUBLE AND RIGHT SINGLE
        0xD4: '\u2558',  # ╘ BOX DRAWINGS UP SINGLE AND RIGHT DOUBLE
        0xD5: '\u2552',  # ╒ BOX DRAWINGS DOWN SINGLE AND RIGHT DOUBLE
        0xD6: '\u2553',  # ╓ BOX DRAWINGS DOWN DOUBLE AND RIGHT SINGLE
        0xD7: '\u256B',  # ╫ BOX DRAWINGS VERTICAL DOUBLE AND HORIZONTAL SINGLE
        0xD8: '\u256A',  # ╪ BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE
        0xD9: '\u2518',  # ┘ BOX DRAWINGS LIGHT UP AND LEFT
        0xDA: '\u250C',  # ┌ BOX DRAWINGS LIGHT DOWN AND RIGHT
        0xDB: '\u2588',  # █ FULL BLOCK
        0xDC: '\u2584',  # ▄ LOWER HALF BLOCK
        0xDD: '\u258C',  # ▌ LEFT HALF BLOCK
        0xDE: '\u2590',  # ▐ RIGHT HALF BLOCK
        0xDF: '\u2580',  # ▀ UPPER HALF BLOCK

        # More Arabic letters (0xE0-0xFF)
        0xE0: '\u0638',  # ظ ZAH
        0xE1: '\u0639',  # ع AIN (isolated)
        0xE2: '\u0639',  # ع AIN (final)
        0xE3: '\u0639',  # ع AIN (medial)
        0xE4: '\u0639',  # ع AIN (initial)
        0xE5: '\u063A',  # غ GHAIN (isolated)
        0xE6: '\u063A',  # غ GHAIN (final)
        0xE7: '\u063A',  # غ GHAIN (medial)
        0xE8: '\u063A',  # غ GHAIN (initial)

        0xE9: '\u0641',  # ف FEH (final-isolated)
        0xEA: '\u0641',  # ف FEH (initial-medial)
        0xEB: '\u0642',  # ق QAF (final-isolated)
        0xEC: '\u0642',  # ق QAF (initial-medial)
        0xED: '\u06A9',  # ک KEHEH (final-isolated)
        0xEE: '\u06A9',  # ک KEHEH (initial-medial)
        0xEF: '\u06AF',  # گ GAF (final-isolated)
        0xF0: '\u06AF',  # گ GAF (initial-medial)

        0xF1: '\u0644',  # ل LAM (final-isolated)
        0xF2: '\u0644\u0627',  # لا LAM-ALEF LIGATURE
        0xF3: '\u0644',  # ل LAM (initial-medial)

        0xF4: '\u0645',  # م MEEM (final-isolated)
        0xF5: '\u0645',  # م MEEM (initial-medial)
        0xF6: '\u0646',  # ن NOON (final-isolated)
        0xF7: '\u0646',  # ن NOON (initial-medial)
        0xF8: '\u0648',  # و WAW

        0xF9: '\u0647',  # ه HEH (final-isolated)
        0xFA: '\u0647',  # ه HEH (medial)
        0xFB: '\u0647',  # ه HEH (initial)

        0xFC: '\u06CC',  # ی FARSI YEH (final)
        0xFD: '\u06CC',  # ی FARSI YEH (isolated)
        0xFE: '\u06CC',  # ی FARSI YEH (initial-medial)

        0xFF: '\u00A0',  # NO-BREAK SPACE
    }

    @staticmethod
    def decode(iran_system_bytes: bytes, reverse: bool = True) -> str:
        """
        Decode Iran System bytes to Unicode string

        Args:
            iran_system_bytes: Raw bytes in Iran System encoding
            reverse: Whether to reverse the output (default: True)
                    Iran System stores text in visual order (left-to-right),
                    so we need to reverse it to get logical order for RTL text

        Returns:
            Unicode string

        Example:
            >>> decoder = IranSystemDecoder()
            >>> result = decoder.decode(b'\\xfc\\xf3\\xe4')
            >>> print(result)  # Should print: علی
        """
        result = []

        for byte in iran_system_bytes:
            if byte in IranSystemDecoder.IRAN_SYSTEM_TO_UNICODE:
                char = IranSystemDecoder.IRAN_SYSTEM_TO_UNICODE[byte]
                result.append(char)
            else:
                # Unknown byte - use replacement character
                result.append('\uFFFD')  # � REPLACEMENT CHARACTER

        text = ''.join(result)

        # Iran System stores text in visual (display) order
        # For Persian/Arabic RTL text, we need to reverse it to logical order
        if reverse:
            text = text[::-1]

        return text

    @staticmethod
    def decode_field(field_value: str, encoding: str = 'latin-1') -> str:
        """
        Decode a DBF field value from Iran System to Unicode

        Args:
            field_value: Field value as string (from DBF reader)
            encoding: Encoding used to read the DBF (default: 'latin-1')

        Returns:
            Decoded Unicode string
        """
        if not field_value:
            return ''

        # Convert string to bytes (preserving raw bytes)
        if isinstance(field_value, str):
            iran_bytes = field_value.encode(encoding)
        else:
            iran_bytes = field_value

        # Strip trailing spaces and nulls
        iran_bytes = iran_bytes.rstrip(b' \x00')

        # Decode to Unicode
        return IranSystemDecoder.decode(iran_bytes)


# Convenience function
def decode_iran_system(iran_system_bytes: bytes) -> str:
    """
    Convenience function to decode Iran System bytes to Unicode

    Args:
        iran_system_bytes: Raw bytes in Iran System encoding

    Returns:
        Unicode string
    """
    return IranSystemDecoder.decode(iran_system_bytes)


if __name__ == '__main__':
    # Test the decoder
    decoder = IranSystemDecoder()

    # Test cases from real DBF files
    test_cases = [
        (b'\xfc\xf3\xe4', 'علی'),  # Ali
        (b'\xf6\xfe\xa8\x9f\xa2\xf5\x9f\xf5', 'محمدحسین'),  # MohammadHossein
        (b'\xf6\xa8\x9f', 'حسن'),  # Hassan
    ]

    print("Testing Iran System Decoder:")
    print("=" * 80)

    for iran_bytes, expected in test_cases:
        result = decoder.decode(iran_bytes)
        hex_str = ' '.join(f'{b:02x}' for b in iran_bytes)
        match = '✅' if result == expected else '❌'

        print(f"{match} Input:    {hex_str}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        print()
