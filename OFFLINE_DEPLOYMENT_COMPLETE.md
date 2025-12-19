# Complete Offline Deployment Guide - SAP to SSO DBF System
**Version:** 2.0 - FULL OFFLINE DEPLOYMENT
**Date:** 2025-12-19
**Target:** Customer Server (NO INTERNET ACCESS)
**Deployment Path:** DEV → QUA → PRD

---

## 🚨 IMPORTANT: NO INTERNET ON CUSTOMER SERVER

This guide assumes **ZERO internet connectivity** on the customer server.
All dependencies must be downloaded beforehand and transferred manually.

---

## 📦 PART 1: PREPARE DEPLOYMENT PACKAGE (On Machine WITH Internet)

### Step 1.1: Download Python Dependencies OFFLINE

**On your LOCAL machine with internet:**

```bash
# Create offline packages directory
mkdir sso_deployment_offline
cd sso_deployment_offline

# Download ALL Python packages with dependencies
pip download \
    dbfread==2.0.7 \
    pandas==2.0.3 \
    openpyxl==3.1.2 \
    xlrd==2.0.1 \
    jdatetime==4.1.1 \
    python-dateutil==2.8.2 \
    numpy==1.24.4 \
    -d ./python_packages
```

This will download approximately **~50MB** of `.whl` and `.tar.gz` files.

### Step 1.2: Verify Downloaded Packages

```bash
ls -lh python_packages/
# Should show files like:
# - pandas-2.0.3-*.whl
# - numpy-1.24.4-*.whl
# - openpyxl-3.1.2-*.whl
# - etc.
```

### Step 1.3: Package Project Files

Create deployment archive:

```bash
# Go to project root
cd /path/to/abap-mdf-sso

# Create deployment directory structure
mkdir -p deployment_package/sap_sso_system
mkdir -p deployment_package/python_packages

# Copy all project files
cp -r sap_integration deployment_package/sap_sso_system/
cp -r src deployment_package/sap_sso_system/
cp -r tools deployment_package/sap_sso_system/
cp -r config deployment_package/sap_sso_system/ 2>/dev/null || true

# Copy Python packages
cp python_packages/* deployment_package/python_packages/

# Copy documentation
cp DEPLOYMENT_GUIDE.md deployment_package/
cp OFFLINE_DEPLOYMENT_COMPLETE.md deployment_package/
cp README.md deployment_package/ 2>/dev/null || true

# Create installation script
cat > deployment_package/INSTALL_OFFLINE.sh << 'EOF'
#!/bin/bash
echo "Installing Python packages offline..."
pip install --no-index --find-links=./python_packages dbfread pandas openpyxl xlrd jdatetime python-dateutil numpy
echo "Installation complete!"
EOF

chmod +x deployment_package/INSTALL_OFFLINE.sh

# Create ZIP archive
zip -r sso_deployment_v2.0.zip deployment_package/

echo "✅ Package created: sso_deployment_v2.0.zip"
ls -lh sso_deployment_v2.0.zip
```

---

## 📦 PART 2: TRANSFER TO CUSTOMER SERVER

### Step 2.1: Transfer Methods

**Option A: USB Drive**
```
1. Copy sso_deployment_v2.0.zip to USB drive
2. Physically transport to customer location
3. Copy from USB to server
```

**Option B: Secure File Transfer** (if available without internet)
```
scp sso_deployment_v2.0.zip user@customer-server:/tmp/
```

**Option C: CD/DVD**
```
Burn sso_deployment_v2.0.zip to disc
```

### Step 2.2: Verify Transfer

On customer server:
```bash
cd /tmp  # or wherever you copied the file
ls -lh sso_deployment_v2.0.zip
md5sum sso_deployment_v2.0.zip  # Compare with source
```

---

## 🔧 PART 3: INSTALLATION ON CUSTOMER SERVER

### Step 3.1: Extract Package

```bash
# Create installation directory
mkdir -p /usr/sap/scripts/sso_system
cd /usr/sap/scripts/sso_system

# Extract archive
unzip /tmp/sso_deployment_v2.0.zip
cd deployment_package
```

### Step 3.2: Install Python (if not already installed)

**Check Python version:**
```bash
python3 --version
# Required: Python 3.8 or higher
```

**If Python not installed:**
```
Contact customer Basis team to install Python 3.8+
Or use system Python if available
```

### Step 3.3: Install Python Dependencies OFFLINE

```bash
# Install from local packages (NO INTERNET NEEDED)
chmod +x INSTALL_OFFLINE.sh
./INSTALL_OFFLINE.sh

# OR manually:
pip3 install --no-index --find-links=./python_packages \
    dbfread pandas openpyxl xlrd jdatetime python-dateutil numpy
```

### Step 3.4: Verify Installation

```bash
python3 << 'EOF'
import sys
print("Python version:", sys.version)

packages = [
    'dbfread',
    'pandas',
    'openpyxl',
    'xlrd',
    'jdatetime',
    'dateutil',
    'numpy'
]

print("\nInstalled packages:")
for pkg in packages:
    try:
        exec(f"import {pkg}")
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg} - MISSING!")
EOF
```

Expected output:
```
✓ dbfread
✓ pandas
✓ openpyxl
✓ xlrd
✓ jdatetime
✓ dateutil
✓ numpy
```

### Step 3.5: Set Up Directory Structure

```bash
cd /usr/sap/scripts/sso_system/deployment_package/sap_sso_system

# Create working directories
mkdir -p /usr/sap/scripts/dbf_converter/tmp
mkdir -p /usr/sap/scripts/dbf_converter/output
mkdir -p /usr/sap/scripts/dbf_converter/logs

# Set permissions
chmod -R 755 /usr/sap/scripts/dbf_converter
chmod +x sap_integration/*.py
chmod +x tools/*.py

# Verify structure
ls -la /usr/sap/scripts/dbf_converter/
```

---

## 🔧 PART 4: SAP CONFIGURATION

### Step 4.1: Register External OS Commands (SM69)

**Transaction: SM69**

Create these commands:

#### Command 1: XLS to DBF Converter
```
Command Name:    ZDBF_XLS_CONVERT
Operating System: Unix/Linux
External Program: /usr/bin/python3
Parameters:      /usr/sap/scripts/sso_system/deployment_package/sap_sso_system/sap_integration/sap_xls_to_dbf.py
Additional Parameters: ip
Logon User:      <SAP service user>
```

#### Command 2: ZIP Creator
```
Command Name:    ZDBF_ZIP_CREATE
Operating System: Unix/Linux
External Program: /usr/bin/python3
Parameters:      /usr/bin/python3
Additional Parameters: ip
Logon User:      <SAP service user>
```

**Test Commands:**
```
SM69 → Select command → Execute (F8)
Check return code = 0
```

### Step 4.2: Deploy ABAP Programs

**Transaction: SE38**

Deploy these programs in order:

#### Program 1: ZHR_INS_REP_FILES_DBF

```
1. SE38 → Create Program
   Name: ZHR_INS_REP_FILES_DBF
   Type: Include

2. Copy content from:
   deployment_package/sap_sso_system/sap_integration/ZHR_INS_REP_FILES_DBF.abap

3. Save → Activate (Ctrl+F3)

4. Check syntax → Should show 0 errors
```

#### Program 2: ZABAP_DBF_CONVERTER (if needed)

```
1. SE38 → Create Program
   Name: ZABAP_DBF_CONVERTER
   Type: Include

2. Copy content from:
   deployment_package/sap_sso_system/sap_integration/ZABAP_DBF_CONVERTER.abap

3. Save → Activate
```

#### Program 3: Main Execution Program

```
1. Create or modify your main payroll report
2. Add INCLUDE ZHR_INS_REP_FILES_DBF
3. Add button/function to call: PERFORM fill_dbf_direct
```

### Step 4.3: Configure File Paths

**In ABAP code, verify these paths match your server:**

```abap
" Line ~40 in ZHR_INS_REP_FILES_DBF.abap
lv_output_dir = '/usr/sap/scripts/dbf_converter/tmp/'.

" Adjust if your path is different:
" lv_output_dir = '/your/custom/path/'.
```

### Step 4.4: Test Python Script Execution

**From SAP:**
```
1. SE38 → Create simple test program:

REPORT ztest_python.

DATA: lv_command TYPE sxpgcolist-name VALUE 'ZDBF_XLS_CONVERT',
      lv_params  TYPE string,
      lt_output  TYPE TABLE OF btcxpm,
      lv_status  TYPE extcmdexex-exitcode.

lv_params = '--help'.

CALL FUNCTION 'SXPG_CALL_SYSTEM'
  EXPORTING
    commandname           = lv_command
    additional_parameters = lv_params
  IMPORTING
    exitcode              = lv_status
  TABLES
    exec_protocol         = lt_output.

WRITE: / 'Exit code:', lv_status.
LOOP AT lt_output INTO DATA(ls_line).
  WRITE: / ls_line-message.
ENDLOOP.

2. Execute (F8)
3. Exit code should be 0
4. Output should show Python script help
```

---

## 🧪 PART 5: TESTING (DEV Environment)

### Step 5.1: End-to-End Test

```
1. Run main payroll report
2. Select 3-5 test employees
3. Click "Generate SSO DBF" button
4. System should:
   ✓ Create XLS files in /usr/sap/scripts/dbf_converter/tmp/
   ✓ Call Python converter
   ✓ Generate DBF files
   ✓ Create ZIP archive
   ✓ Download ZIP to PC
```

### Step 5.2: Verify Generated Files

**Check on server:**
```bash
ls -la /usr/sap/scripts/dbf_converter/tmp/
# Should see:
# - DSKKAR00.XLS
# - DSKWOR00.XLS
# - DSKKAR00.DBF
# - DSKWOR00.DBF
# - SSO_Files_YYYYMMDD_HHMMSS.zip
```

**Download and verify:**
```
1. Download ZIP file from SAP
2. Extract on Windows PC
3. Open DSKKAR00.DBF and DSKWOR00.DBF with DBF viewer
4. Verify data matches test employees
```

### Step 5.3: Verify Python Script Logs

```bash
# Check logs
tail -100 /tmp/sap_dbf_converter.log

# Should show:
# - XLS files read successfully
# - CSV conversion complete
# - DBF files created
# - No Python errors
```

### Step 5.4: Test All 4 Fixes

**Fix 1: DSW_TOTL = DSW_MASHML**
```
Open DSKWOR00.XLS
Find employee row
Check: DSW_TOTL column value = DSW_MASH column value
```

**Fix 2: DSW_INC / DSW_DD**
```
Check: DSW_INC value = (original INC / DD)
Example: If INC was 3000000, DD=30 → new INC should be 100000
```

**Fix 3: DSW_ID1 padding = 8 chars**
```
Check DSW_ID1 column
All values should be exactly 8 characters with leading zeros
Example: "123" → "00000123"
```

**Fix 4: DSW_BDATE padding = 8 chars**
```
Check DSW_BDATE column
All birth dates should be 8 characters
Example: "1401215" → "01401215"
```

---

## 📋 PART 6: COMPLETE FILE CHECKLIST

### Python Files to Deploy

```
sap_integration/
├── ZHR_INS_REP_FILES_DBF.abap          ⭐ MAIN ABAP CODE (UPDATED)
├── ZABAP_DBF_CONVERTER.abap
├── sap_xls_to_dbf.py                   ⭐ XLS to DBF converter
├── sap_dbf_wrapper.py
└── sap_to_dbf_standalone.py

src/
├── utils/
│   ├── iran_system_encoding.py        ⭐ Persian text encoding
│   ├── iran_system_decoder.py
│   ├── jalali_converter.py
│   └── generate_dbf.py
└── generators/
    └── generate_dskwor.py

tools/
├── csv_to_dbf_complete.py              ⭐ CSV to DBF converter
├── dbf_converter_gui.py
├── dbf_to_csv.py
└── create_payroll_zip.py

config/  (if exists)
└── field_mappings.json
```

### Python Packages Required

```
python_packages/
├── dbfread-2.0.7-*.whl
├── pandas-2.0.3-*.whl
├── openpyxl-3.1.2-*.whl
├── xlrd-2.0.1-*.whl
├── jdatetime-4.1.1-*.whl
├── python_dateutil-2.8.2-*.whl
├── numpy-1.24.4-*.whl
├── et_xmlfile-*.whl              (dependency)
├── pytz-*.whl                    (dependency)
├── six-*.whl                     (dependency)
└── tzdata-*.whl                  (dependency)
```

### Directory Structure on Server

```
/usr/sap/scripts/
├── sso_system/
│   └── deployment_package/
│       ├── sap_sso_system/       ← All Python/ABAP code
│       ├── python_packages/      ← Offline pip packages
│       └── INSTALL_OFFLINE.sh
│
└── dbf_converter/
    ├── tmp/                      ← Working directory for SAP
    ├── output/                   ← Final DBF files
    └── logs/                     ← Python script logs
```

---

## 🔄 PART 7: TRANSPORT TO QUA/PRD

### Step 7.1: Python Code Transport

**Python files are OS-level files, not transported via STMS.**

For QUA/PRD:
```
1. Repeat PART 2 (Transfer) for QUA/PRD servers
2. Repeat PART 3 (Installation) for QUA/PRD servers
3. Use same offline package: sso_deployment_v2.0.zip
```

### Step 7.2: ABAP Code Transport

```
1. In DEV: Create transport request
   SE09 → Create → Workbench request
   Description: "SSO DBF System - Initial Deployment"

2. Add programs to transport:
   SE10 → Request → Add objects
   - ZHR_INS_REP_FILES_DBF
   - ZABAP_DBF_CONVERTER
   - Any custom programs calling these

3. Release transport
4. Import to QUA via STMS
5. After QUA testing, import to PRD via STMS
```

### Step 7.3: SM69 Commands

**SM69 commands must be created manually in each system.**

```
Repeat Step 4.1 in:
- QUA system
- PRD system

Or export/import via:
SE16 → SXPGCOSTAB table
```

---

## 🐛 PART 8: TROUBLESHOOTING

### Issue 1: "Python not found"

```bash
# Find Python location
which python3
# Output: /usr/bin/python3

# Update SM69 command to use exact path
```

### Issue 2: "Module not found" (pandas, etc.)

```bash
# Verify packages installed
pip3 list | grep pandas

# If missing, reinstall offline
cd deployment_package
pip3 install --no-index --find-links=./python_packages pandas
```

### Issue 3: "Permission denied" on /usr/sap/scripts

```bash
# Check ownership
ls -la /usr/sap/scripts/

# Fix permissions
sudo chown -R <sapuser>:sapsys /usr/sap/scripts/dbf_converter
sudo chmod -R 755 /usr/sap/scripts/dbf_converter
```

### Issue 4: "ZIP file empty or corrupt"

```bash
# Check Python script output
tail -100 /tmp/sap_dbf_converter.log

# Manually test ZIP creation
cd /usr/sap/scripts/dbf_converter/tmp
python3 -m zipfile -c test.zip DSKKAR00.DBF DSKWOR00.DBF
ls -lh test.zip
```

### Issue 5: Persian text shows as ????

```
Check iran_system_encoding.py is in src/utils/
Verify Python script imports it correctly:
  from utils.iran_system_encoding import IranSystemEncoder
```

### Issue 6: SXPG_CALL_SYSTEM fails with return code 1

```
1. Check PFCG authorization for user
2. Verify SM69 command parameters
3. Test command manually from OS:
   su - <sapuser>
   /usr/bin/python3 /path/to/script.py --help
```

---

## 📊 PART 9: PERFORMANCE & SIZING

### Disk Space Requirements

```
Python packages:      ~50 MB
Project files:        ~5 MB
Working directory:    ~100 MB per run
Logs:                 ~10 MB per month

Total minimum:        ~200 MB free space
```

### Processing Time

```
Small batch (10 employees):     ~5 seconds
Medium batch (100 employees):   ~15 seconds
Large batch (1000 employees):   ~2 minutes
```

### Memory Usage

```
Python process:  ~200 MB RAM
No special requirements
```

---

## ✅ PART 10: DEPLOYMENT CHECKLIST

### Pre-Deployment (With Internet)
- [ ] Downloaded all Python packages offline
- [ ] Created deployment ZIP file
- [ ] Verified ZIP contains all files
- [ ] Tested package on test machine

### Server Preparation (Customer Site)
- [ ] Transferred ZIP to server via USB/CD
- [ ] Extracted to /usr/sap/scripts/sso_system
- [ ] Python 3.8+ installed
- [ ] Installed Python packages offline
- [ ] Created working directories
- [ ] Set correct permissions

### SAP Configuration (DEV)
- [ ] SM69 commands created and tested
- [ ] ABAP programs uploaded and activated
- [ ] File paths configured correctly
- [ ] Transport request created

### Testing (DEV)
- [ ] End-to-end test with 3-5 employees
- [ ] All 4 fixes verified
- [ ] DBF files open correctly
- [ ] ZIP download works
- [ ] No Python errors in logs

### QUA Deployment
- [ ] Python code copied to QUA server
- [ ] Python packages installed offline
- [ ] SM69 commands created
- [ ] ABAP transport imported
- [ ] Testing completed

### PRD Deployment
- [ ] Change approval received
- [ ] Python code copied to PRD server
- [ ] Python packages installed offline
- [ ] SM69 commands created
- [ ] ABAP transport imported
- [ ] Smoke test completed

---

## 📞 SUPPORT CONTACTS

| Component | Contact | Notes |
|-----------|---------|-------|
| Python Scripts | __________ | Linux/Python issues |
| ABAP Programs | __________ | SAP functional issues |
| Basis Team | __________ | SM69, file system, permissions |
| Network Team | __________ | File transfers |

---

## 📚 APPENDIX A: MANUAL PYTHON PACKAGE DOWNLOAD

If pip download doesn't work, download manually from PyPI:

```
1. Go to https://pypi.org/ (on internet machine)
2. Download each package + dependencies:

dbfread:
  https://pypi.org/project/dbfread/#files
  → Download dbfread-2.0.7-py2.py3-none-any.whl

pandas:
  https://pypi.org/project/pandas/#files
  → Download pandas-2.0.3-cp38-cp38-manylinux_2_17_x86_64.whl
  → Also download: numpy, pytz, python-dateutil, tzdata

openpyxl:
  https://pypi.org/project/openpyxl/#files
  → Download openpyxl-3.1.2-py2.py3-none-any.whl
  → Also download: et-xmlfile

xlrd:
  https://pypi.org/project/xlrd/#files
  → Download xlrd-2.0.1-py2.py3-none-any.whl

jdatetime:
  https://pypi.org/project/jdatetime/#files
  → Download jdatetime-4.1.1-py3-none-any.whl

3. Copy all .whl files to deployment_package/python_packages/
```

---

## 📚 APPENDIX B: ALTERNATIVE INSTALLATION (TARBALL)

If .whl files don't work:

```bash
# Extract and install from source
cd python_packages
tar -xzf pandas-2.0.3.tar.gz
cd pandas-2.0.3
python3 setup.py install --user
```

---

## 📚 APPENDIX C: CREATING SM69 SCRIPT WRAPPER

If direct Python call fails, create shell wrapper:

```bash
# Create /usr/sap/scripts/sso_converter.sh
cat > /usr/sap/scripts/sso_converter.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=/usr/sap/scripts/sso_system/deployment_package/sap_sso_system:$PYTHONPATH
/usr/bin/python3 /usr/sap/scripts/sso_system/deployment_package/sap_sso_system/sap_integration/sap_xls_to_dbf.py "$@"
EOF

chmod +x /usr/sap/scripts/sso_converter.sh

# Update SM69 to call this script instead
```

---

**END OF COMPLETE OFFLINE DEPLOYMENT GUIDE**

For questions or issues during deployment, refer to troubleshooting section or contact support.
