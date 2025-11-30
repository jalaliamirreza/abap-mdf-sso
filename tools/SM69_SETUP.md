# SM69 Configuration Guide for Python ZIP Creation

## Overview
The ABAP program uses `SXPG_CALL_SYSTEM` to execute Python scripts for creating ZIP files. This requires setting up an external command in SM69.

## Configuration Steps

### 1. Open Transaction SM69
```
Transaction: SM69
```

### 2. Create New External Command
Click **Create** button

### 3. Fill in the Following Details

**Command Name**: `ZPYTHON`

**Operating System**: Select based on your SAP server:
- For Linux/Unix: `UNIX`
- For AIX: `AIX`
- Or select appropriate OS

**External Program**: `/usr/bin/python3`
(Or the full path to Python 3 on your server - check with `which python3`)

**Parameters for Additional Parameters**: `<leave blank>`

**Additional parameters allowed**: ☑️ **CHECK THIS BOX** (Very Important!)

**Operating Mode**: `Current`

**Target Host**: `<leave blank>` (will use application server)

**Trace State**: `No Trace`

### 4. Save the Command

Click **Save** button

### 5. Test the Command

1. Select the command `ZPYTHON`
2. Click **Execute** button (or F8)
3. In the popup:
   - Additional Parameters: `--version`
   - Click Execute
4. Should see output like: `Python 3.x.x`

If you see the Python version, configuration is successful! ✅

### 6. Grant Permissions (if needed)

If users get "No Permission" error:

1. Go to SM69
2. Select command `ZPYTHON`
3. Click **Authorizations** button
4. Add users/roles who should execute this command
5. Or configure `EXEC_GROUPS` to allow all users

## Troubleshooting

### Error: "Command ZPYTHON not found"
**Solution**: Create the command in SM69 as described above

### Error: "No permission to execute command"
**Solution**:
1. Check authorizations in SM69
2. User needs authorization object `S_RZL_ADM` with:
   - COMMAND = ZPYTHON
   - TYPE = COMMAND
   - ACTVT = 16 (Execute)

### Error: "External program not found"
**Solution**:
1. SSH to SAP server: `ssh <sap-server>`
2. Check Python path: `which python3`
3. Update "External Program" in SM69 with the correct path

### Error: "Parameters too long (max 128 chars)"
**Solution**:
This is a limitation of SXPG. The Python command path might be too long.
Workaround: Create a shell wrapper script at a shorter path

### Python Version Issues
If `python3` command doesn't exist:
1. Try `python` instead
2. Or install Python 3 on the server
3. Or use full path like `/usr/local/bin/python3.9`

## Verifying Setup

After configuration, when you run the ABAP program:

**Expected behavior:**
```
==========================================
Creating ZIP file with Python...
==========================================

Python execution log:
---
Found: DSKKAR00.XLS (1145 bytes)
Found: DSKWOR00.XLS (2048 bytes)
...
✓ Success! ZIP file created
---

Status: 0
Exit code: 0

SUCCESS: ZIP file created successfully!
File: /usr/sap/scripts/dbf_converter/tmp/SSO_Files_251130_143022.zip
```

**If you see errors:**
1. Check the error message in the output
2. Verify Python script exists at: `/usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py`
3. Verify Python 3 is installed: `python3 --version`
4. Check file permissions on the script
5. Check SM69 configuration

## Alternative: Using Shell Wrapper

If the Python command path is too long for SM69 parameters (>128 chars), create a wrapper:

### 1. Create Wrapper Script
```bash
ssh <sap-server>
cat > /usr/local/bin/create_sap_zip.sh << 'EOF'
#!/bin/bash
/usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py "$@"
EOF

chmod +x /usr/local/bin/create_sap_zip.sh
```

### 2. Update SM69 Command
- External Program: `/usr/local/bin/create_sap_zip.sh`
- This is shorter and avoids the 128 character limit

## Security Notes

- The ZPYTHON command allows executing Python scripts
- Ensure only authorized users have access
- The script only accesses files in `/usr/sap/scripts/dbf_converter/tmp/`
- No system files or sensitive data are accessible

## Quick Reference

| Setting | Value |
|---------|-------|
| Transaction | SM69 |
| Command Name | ZPYTHON |
| OS | UNIX (or your OS) |
| External Program | /usr/bin/python3 |
| Add. Params Allowed | ✅ Yes |

## Support

If you continue to have issues:
1. Check SAP system logs (SM21)
2. Check ABAP runtime errors (ST22)
3. Verify Python script is executable: `ls -la /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py`
4. Test Python script manually: `python3 /usr/sap/scripts/dbf_converter/tools/create_payroll_zip.py /usr/sap/scripts/dbf_converter/tmp/`
