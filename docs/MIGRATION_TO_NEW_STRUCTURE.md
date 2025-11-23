# Migration to SSO New Structure (2024)

**Date:** 2024-11-23
**Status:** ✅ Complete

---

## Overview

The Iranian Social Security Organization (SSO) updated their DBF file structure in Autumn 2024 (آذر ۱۴۰۳). All our tools have been updated to support the new structure.

## What Changed

### Header File (DSKKAR00.DBF)
- **Fields:** 26 → 25 (1 field removed)
- **Record length:** 609 bytes → 311 bytes
- **Removed field:** DSK_TBIM20

#### Field Length Changes:
| Field | Old Length | New Length | Change |
|-------|------------|------------|--------|
| DSK_NAME | 100 | 30 | -70% |
| DSK_FARM | 100 | 30 | -70% |
| DSK_ADRS | 100 | 40 | -60% |
| DSK_DISC | 100 | 30 | -70% |
| DSK_TMAH | 13 | 12 | -1 |
| DSK_TTOTL | 13 | 12 | -1 |
| DSK_INC | 19 | 12 | -7 |
| DSK_SPOUSE | 19 | 12 | -7 |

### Workers File (DSKWOR00.DBF)
- **Fields:** 31 → 29 (2 fields removed)
- **Record length:** 398 bytes → 469 bytes
- **Removed fields:** DSW_KOSO, DSW_BIME20

#### Field Length Changes:
| Field | Old Length | New Length | Change |
|-------|------------|------------|--------|
| DSW_FNAME | 20 | 60 | +200% 🎉 |
| DSW_LNAME | 25 | 60 | +140% 🎉 |
| DSW_DNAME | 20 | 60 | +200% 🎉 |
| DSW_JOB | 10 | 6 | -4 |
| DSW_INC | 19 | 12 | -7 |
| DSW_SPOUSE | N19 | C10 | Type changed! |

#### Field Order Changes:
- **DSW_JOB:** Position 29 → 26
- **PER_NATCOD:** Position 28 → 27

#### Field Type Changes:
- **DSW_SPOUSE:** Number (N19) → Character (C10)

---

## Updated Tools

All tools have been updated to use the new structure:

### ✅ `tools/csv_to_dbf_complete.py`
- Updated header structure (25 fields)
- Updated workers structure (29 fields)
- Handles DSW_SPOUSE as Character type
- Persian field encoding works correctly

### ✅ `tools/dbf_to_csv.py`
- Reads new structure correctly
- Decodes Persian fields properly
- DSW_JOB treated as numeric code (not Persian text)

### ✅ `docs/NEW_STRUCTURE_2024.md`
- Complete documentation of all changes
- Field-by-field comparison
- Python code definitions

---

## Verification Tests

### Structure Verification ✅
```bash
# Header file: 25 fields, 311 bytes record length
# Workers file: 29 fields, 469 bytes record length
```

### Round-Trip Test ✅
```bash
# CSV → DBF → CSV
# Persian text preserved: کارگاه تست, کارفرما تست, علی, محمدی
# Persian digits preserved: فتح ۵
# Spaces preserved correctly
# All field values match
```

### Encoding Tests ✅
- ✅ Iran System encoding works
- ✅ Persian digits (۰-۹) convert correctly
- ✅ Space preservation maintained
- ✅ Visual/logical order reversal works
- ✅ Language Driver ID (0x7E) set correctly

---

## Migration Guide

### For Existing Users

**No action needed!** All tools automatically use the new structure.

If you have CSV files with the old structure fields (DSK_TBIM20, DSW_KOSO, DSW_BIME20), these fields will be ignored when creating DBF files.

### CSV File Requirements

#### Header CSV must include these fields (minimum):
- DSK_ID, DSK_NAME, DSK_FARM, DSK_ADRS
- DSK_DISC (optional)

#### Workers CSV must include these fields (minimum):
- DSW_ID1, DSW_FNAME, DSW_LNAME, DSW_DNAME
- DSW_IDNO, DSW_IDPLC, DSW_IDATE, DSW_BDATE
- DSW_SEX, DSW_NAT, DSW_OCP
- DSW_SDATE, DSW_EDATE, DSW_DD
- DSW_ROOZ, DSW_MAH, DSW_MAZ, DSW_MASH, DSW_TOTL, DSW_BIME
- DSW_PRATE, DSW_JOB, PER_NATCOD, DSW_INC, DSW_SPOUSE

#### Important Notes:
- **DSW_SPOUSE** is now a text field - enter as string: "25000000"
- **DSW_JOB** is a numeric code (like "123456"), not Persian text
- Field length limits enforced:
  - Names (DSW_FNAME, DSW_LNAME, DSW_DNAME): Max 60 characters
  - Workshop name (DSK_NAME): Max 30 characters
  - Address (DSK_ADRS): Max 40 characters

---

## Technical Details

### Persian Fields (Iran System Encoding)
These fields use Iran System encoding:
- DSW_FNAME, DSW_LNAME, DSW_DNAME (names)
- DSW_IDPLC (ID issue place)
- DSW_OCP (occupation)
- DSW_SEX (sex: مرد/زن)
- DSW_NAT (nationality: ایرانی)
- DSK_NAME, DSK_FARM (workshop/employer names)
- DSK_ADRS, DSK_DISC (address/description)

### Non-Persian Fields
These are ASCII/numeric fields:
- DSW_JOB (job code: numeric like "123456")
- PER_NATCOD (national code: numeric "1234567890")
- All date fields (format: YYYYMMDD)
- All numeric amount fields

---

## Example Usage

### Convert CSV to DBF (New Structure)
```bash
python tools/csv_to_dbf_complete.py \
    header.csv workers.csv \
    --workshop-id "1234567890" \
    --year 3 \
    --month 9 \
    --output-dir output
```

### Convert DBF to CSV
```bash
python tools/dbf_to_csv.py output/dskkar00.dbf --output header.csv
python tools/dbf_to_csv.py output/dskwor00.dbf --output workers.csv
```

---

## Files Modified

### Code Changes:
- ✅ `tools/csv_to_dbf_complete.py` - Updated field structures
- ✅ `tools/dbf_to_csv.py` - Updated Persian fields list

### Documentation:
- ✅ `docs/NEW_STRUCTURE_2024.md` - Complete structure reference
- ✅ `docs/MIGRATION_TO_NEW_STRUCTURE.md` - This file

### Test Files:
- ✅ `newsample/DSKKAR00.DBF` - New structure header template
- ✅ `newsample/DSKWOR00.DBF` - New structure workers template

---

## Backward Compatibility

The old structure (sample/ directory files) is no longer supported by SSO. All files must use the new 2024 structure.

If you have old DBF files, convert them to CSV first, then regenerate using the new structure.

---

## Troubleshooting

### "Unable to parse column" error from SSO
- ✅ Fixed: Structure updated to match SSO requirements
- ✅ Fixed: Language Driver ID (0x7E) set correctly
- ✅ Fixed: All field lengths match SSO requirements

### Persian text shows as "???"
- Use UTF-8 encoding when viewing CSV files
- Ensure Iran System encoding enabled for DBF files

### Name fields truncated
- Old structure: Max 20-25 characters
- New structure: Max 60 characters ✅
- Persian names now fit properly!

---

**Last Updated:** 2024-11-23
**SSO Structure Version:** 2024 (آذر ۱۴۰۳)
