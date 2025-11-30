# SAP Payroll ZIP Creation Setup

## Overview

This document explains how to set up Python-based ZIP file creation for SAP payroll exports, replacing the problematic ABAP `cl_abap_zip` approach.

## Problem Background

The ABAP `cl_abap_zip` class was causing file corruption when creating ZIP archives:
- Files on Application Server: Correct (1145 bytes)
- Files in downloaded ZIP: Corrupted (1020 bytes)
- Issue: ABAP's binary file reading was truncating the last partial chunk

## Solution

Move ZIP creation from ABAP to Python:
1. ABAP creates the 4 payroll files (XLS and DBF) on Application Server
2. Python script creates ZIP archive from these files
3. ABAP downloads the pre-created ZIP to user's PC

## Files

### Python Script
- **Location**: `/usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py`
- **Purpose**: Creates ZIP archive from payroll files
- **Usage**: `python3 create_payroll_zip.py <directory> [zip_name]`

### ABAP Code
- **File**: `ZHR_INS_REP_FILES_DBF.abap`
- **Modified Forms**:
  - `download_zip_to_pc`: Now calls Python script instead of using `cl_abap_zip`
  - `execute_python_zip`: Executes Python script via `SXPG_COMMAND_EXECUTE`
  - `read_zip_from_server`: Reads created ZIP file from server
  - `check_file_exists`: Verifies ZIP file was created

## Setup Options

### Option 1: Automatic Execution (Recommended)

Configure ABAP to call Python script automatically using `SXPG_COMMAND_EXECUTE`:

1. **Create External Command in SM69**:
   - Transaction: `SM69`
   - Command Name: `ZPYTHON`
   - Operating System: Choose your OS (e.g., `UNIX`)
   - External Program: `/usr/bin/python3`
   - Parameters for Add. Command: `<space for parameters>`
   - Check "Additional parameters allowed"

2. **Test the Command**:
   ```bash
   # On SAP server, verify Python 3 is available:
   which python3
   python3 --version
   ```

3. **Deploy Python Script**:
   ```bash
   # Copy Python script to SAP server
   scp tools/create_payroll_zip.py <sap-server>:/usr/sap/scripts/dbf_converter/tools/

   # Make executable
   chmod +x /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py
   ```

4. **Test from ABAP**:
   The ABAP code will now automatically call the Python script when creating ZIP files.

### Option 2: Manual Execution

If automatic execution is not available:

1. **Deploy Python Script** (same as Option 1 step 3)

2. **When Running ABAP Program**:
   - ABAP will display a message: "WARNING: Could not execute Python script automatically"
   - A popup will show the command to run manually
   - Example: `python3 /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/ SSO_Files_251130_143022.zip`

3. **Run Command on SAP Server**:
   ```bash
   # SSH to SAP server
   ssh <sap-server>

   # Run the displayed command
   python3 /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/ SSO_Files_251130_143022.zip
   ```

4. **Confirm in ABAP**:
   - Click "Yes" in the popup to continue
   - ABAP will download the created ZIP

### Option 3: Scheduled/Cron Job

For regular automated ZIP creation:

1. **Create Shell Wrapper** (see `create_payroll_zip.sh`)

2. **Add Cron Job**:
   ```bash
   # Edit crontab
   crontab -e

   # Add entry to run every hour (or as needed)
   0 * * * * /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.sh
   ```

## Python Script Usage

### Command Line

```bash
# Basic usage - creates payroll_export.zip in the directory
python3 create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/

# Specify custom ZIP name
python3 create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/ custom_name.zip

# With full path
python3 create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/ SSO_Files_251130_143022.zip
```

### Output

The script provides detailed output:
```
Found: DSKKAR00.XLS (1145 bytes)
Found: DSKWOR00.XLS (2048 bytes)
Found: DSKKAR00.DBF (1145 bytes)
Found: DSKWOR00.DBF (2048 bytes)

Creating ZIP archive: /usr/sap/scripts/dbf_converter/tmp/payroll_export.zip
Added to ZIP: DSKKAR00.XLS (1145 bytes uncompressed, 523 bytes compressed)
Added to ZIP: DSKWOR00.XLS (2048 bytes uncompressed, 892 bytes compressed)
Added to ZIP: DSKKAR00.DBF (1145 bytes uncompressed, 523 bytes compressed)
Added to ZIP: DSKWOR00.DBF (2048 bytes uncompressed, 892 bytes compressed)

ZIP file created successfully: /usr/sap/scripts/dbf_converter/tmp/payroll_export.zip
ZIP file size: 3024 bytes

Verifying ZIP integrity...
ZIP integrity check passed ✓

ZIP contents:
  - DSKKAR00.XLS: 1145 bytes
  - DSKWOR00.XLS: 2048 bytes
  - DSKKAR00.DBF: 1145 bytes
  - DSKWOR00.DBF: 2048 bytes

✓ Success! ZIP file created at: /usr/sap/scripts/dbf_converter/tmp/payroll_export.zip
```

## Verification

### Check File Sizes

After downloading ZIP to PC:

1. **Extract ZIP files**
2. **Verify file sizes**:
   - `DSKKAR00.XLS`: Should be 1145 bytes (NOT 1020!)
   - Check that DSK_TKOSO field is NOT zero
   - Verify all columns have data

### Common Issues

**Issue**: Python script not found
- **Solution**: Verify path in ABAP line 594: `lv_python_script = '/usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py'`

**Issue**: Permission denied
- **Solution**:
  ```bash
  chmod +x /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py
  chmod 755 /usr/sap/scripts/dbf_converter/tmp/
  ```

**Issue**: SXPG_COMMAND_EXECUTE fails
- **Solution**: Use Option 2 (Manual Execution) or contact SAP Basis team to configure SM69

**Issue**: ZIP file empty or corrupt
- **Solution**: Check that Python 3 is available: `python3 --version`
- Verify payroll files exist in the directory before creating ZIP

## Architecture Flow

```
1. User runs ABAP program (ZHR_INS_REP_FILES_DBF)
   ↓
2. ABAP creates 4 files on Application Server:
   - DSKKAR00.XLS (header XLS)
   - DSKWOR00.XLS (workers XLS)
   - DSKKAR00.DBF (header DBF)
   - DSKWOR00.DBF (workers DBF)
   ↓
3. ABAP calls Python script:
   python3 create_payroll_zip.py /usr/sap/.../tmp/ SSO_Files_251130_143022.zip
   ↓
4. Python creates ZIP file on Application Server
   - Reads each file completely (no truncation)
   - Creates ZIP with proper compression
   - Verifies integrity
   ↓
5. ABAP reads ZIP file from Application Server
   ↓
6. ABAP downloads ZIP to user's PC
   ↓
7. User extracts ZIP - all files correct!
```

## Benefits

- **No file corruption**: Python reads files completely
- **Integrity verification**: ZIP is tested after creation
- **Detailed logging**: See exactly what's in the ZIP
- **Flexible deployment**: Can be automatic or manual
- **Debugging**: Easy to test Python script independently

## Testing

### Test Python Script Independently

```bash
# 1. Create test files
mkdir -p /tmp/test_payroll
echo "test data for DSKKAR00.XLS" > /tmp/test_payroll/DSKKAR00.XLS
echo "test data for DSKWOR00.XLS" > /tmp/test_payroll/DSKWOR00.XLS
echo "test data for DSKKAR00.DBF" > /tmp/test_payroll/DSKKAR00.DBF
echo "test data for DSKWOR00.DBF" > /tmp/test_payroll/DSKWOR00.DBF

# 2. Run Python script
python3 tools/create_payroll_zip.py /tmp/test_payroll/

# 3. Verify ZIP
unzip -l /tmp/test_payroll/payroll_export.zip
unzip -t /tmp/test_payroll/payroll_export.zip

# 4. Extract and verify contents
cd /tmp/test_payroll
unzip payroll_export.zip -d extracted
ls -lh extracted/
```

## Migration Path

1. ✅ Deploy Python script to SAP server
2. ✅ Update ABAP code (already done)
3. ⏳ Test with sample data
4. ⏳ Configure SM69 (optional, for automatic execution)
5. ⏳ Test with real payroll data
6. ⏳ Verify file sizes and data integrity
7. ⏳ Deploy to production

## Support

For issues or questions:
1. Check this documentation
2. Review Python script output for errors
3. Test Python script independently
4. Check SAP system logs for ABAP errors
5. Verify file permissions on Application Server
