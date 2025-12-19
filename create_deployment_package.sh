#!/bin/bash
# Create Complete Offline Deployment Package
# For customer server with NO INTERNET

set -e

echo "=========================================="
echo "Creating Complete Offline Deployment Package"
echo "=========================================="
echo ""

# Create deployment structure
DEPLOY_DIR="sso_offline_deployment"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/{python_packages,project_files,scripts,docs}

echo "Step 1: Downloading Python packages offline..."
pip3 download \
    dbfread==2.0.7 \
    pandas==2.0.3 \
    openpyxl==3.1.2 \
    xlrd==2.0.1 \
    jdatetime==4.1.1 \
    python-dateutil==2.8.2 \
    numpy==1.24.4 \
    -d $DEPLOY_DIR/python_packages 2>&1 | grep -v "Requirement already satisfied" || true

echo ""
echo "Step 2: Copying project files..."
cp -r sap_integration $DEPLOY_DIR/project_files/
cp -r src $DEPLOY_DIR/project_files/
cp -r tools $DEPLOY_DIR/project_files/
[ -d config ] && cp -r config $DEPLOY_DIR/project_files/ || true

echo ""
echo "Step 3: Copying documentation..."
cp OFFLINE_DEPLOYMENT_COMPLETE.md $DEPLOY_DIR/docs/
cp README.md $DEPLOY_DIR/docs/ 2>/dev/null || echo "README.md not found, skipping"

echo ""
echo "Step 4: Creating installation script..."
cat > $DEPLOY_DIR/scripts/install_python_packages.sh << 'INSTALL_SCRIPT'
#!/bin/bash
echo "Installing Python packages from offline files..."
echo "This does NOT require internet connection"
echo ""

cd "$(dirname "$0")/../python_packages"
pip3 install --no-index --find-links=. \
    dbfread \
    pandas \
    openpyxl \
    xlrd \
    jdatetime \
    python-dateutil \
    numpy

echo ""
echo "✅ Installation complete!"
echo ""
echo "Verifying installation..."
python3 << 'VERIFY'
import sys
packages = ['dbfread', 'pandas', 'openpyxl', 'xlrd', 'jdatetime', 'dateutil', 'numpy']
print("\nInstalled packages:")
for pkg in packages:
    try:
        exec(f"import {pkg}")
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg} - FAILED")
        sys.exit(1)
print("\n✅ All packages verified!")
VERIFY
INSTALL_SCRIPT

chmod +x $DEPLOY_DIR/scripts/install_python_packages.sh

echo ""
echo "Step 5: Creating setup script for SAP server..."
cat > $DEPLOY_DIR/scripts/setup_on_server.sh << 'SETUP_SCRIPT'
#!/bin/bash
# Run this on customer SAP server

echo "=========================================="
echo "Setting up SSO DBF System on SAP Server"
echo "=========================================="
echo ""

# Define installation directory
INSTALL_DIR="/usr/sap/scripts/sso_system"
WORK_DIR="/usr/sap/scripts/dbf_converter"

echo "Installation directory: $INSTALL_DIR"
echo "Working directory: $WORK_DIR"
echo ""

# Check if running as root or SAP user
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Not running as root. Make sure you have permissions for /usr/sap/scripts/"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directories
echo "Creating directories..."
mkdir -p $INSTALL_DIR
mkdir -p $WORK_DIR/{tmp,output,logs}

# Copy project files
echo "Copying project files..."
cp -r project_files/* $INSTALL_DIR/

# Set permissions
echo "Setting permissions..."
chmod -R 755 $INSTALL_DIR
chmod -R 755 $WORK_DIR
find $INSTALL_DIR -name "*.py" -exec chmod +x {} \;

echo ""
echo "✅ File structure created!"
echo ""
echo "Directory structure:"
ls -la $INSTALL_DIR
echo ""
ls -la $WORK_DIR
echo ""

echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. Install Python packages:"
echo "   cd $(pwd)"
echo "   ./scripts/install_python_packages.sh"
echo ""
echo "2. Configure SAP SM69 commands (see docs)"
echo "3. Deploy ABAP programs via SE38"
echo "4. Test with sample data"
echo ""
SETUP_SCRIPT

chmod +x $DEPLOY_DIR/scripts/setup_on_server.sh

echo ""
echo "Step 6: Creating README for deployment..."
cat > $DEPLOY_DIR/README_DEPLOY.txt << 'README'
========================================
SSO DBF SYSTEM - OFFLINE DEPLOYMENT
========================================

This package contains EVERYTHING needed to deploy the SSO DBF system
on a customer server with NO INTERNET ACCESS.

CONTENTS:
---------
1. python_packages/     - All Python dependencies (.whl files)
2. project_files/       - Complete project code
   - sap_integration/   - ABAP and Python integration scripts
   - src/               - Core Python modules
   - tools/             - Utility scripts
3. scripts/             - Installation scripts
4. docs/                - Complete documentation

QUICK START:
------------
1. Copy this entire folder to customer server (USB/CD)

2. Run setup on server:
   cd sso_offline_deployment
   ./scripts/setup_on_server.sh

3. Install Python packages (NO INTERNET NEEDED):
   ./scripts/install_python_packages.sh

4. Follow docs/OFFLINE_DEPLOYMENT_COMPLETE.md for:
   - SAP SM69 configuration
   - ABAP program deployment
   - Testing procedures

FILE SIZES:
-----------
Python packages: ~50 MB
Project files:   ~5 MB
Total:           ~55 MB

SYSTEM REQUIREMENTS:
--------------------
- Python 3.8 or higher
- SAP NetWeaver (any version with ABAP)
- Linux/Unix OS on application server
- ~200 MB free disk space

For detailed instructions, see:
docs/OFFLINE_DEPLOYMENT_COMPLETE.md

========================================
README

echo ""
echo "Step 7: Creating package archive..."
cd ..
tar -czf sso_offline_deployment_v2.0.tar.gz $DEPLOY_DIR/
zip -r sso_offline_deployment_v2.0.zip $DEPLOY_DIR/ >/dev/null 2>&1

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT PACKAGE CREATED!"
echo "=========================================="
echo ""
echo "Package details:"
ls -lh sso_offline_deployment_v2.0.*
echo ""
echo "Package structure:"
tree -L 2 $DEPLOY_DIR 2>/dev/null || find $DEPLOY_DIR -maxdepth 2 -type d
echo ""
echo "Files included:"
echo "  Python packages: $(ls -1 $DEPLOY_DIR/python_packages | wc -l) files"
echo "  Python scripts:  $(find $DEPLOY_DIR/project_files -name "*.py" | wc -l) files"
echo "  ABAP programs:   $(find $DEPLOY_DIR/project_files -name "*.abap" | wc -l) files"
echo ""
echo "=========================================="
echo "TRANSFER TO CUSTOMER:"
echo "=========================================="
echo "1. Copy sso_offline_deployment_v2.0.tar.gz to USB drive"
echo "2. Or burn sso_offline_deployment_v2.0.zip to CD"
echo "3. Transfer to customer server"
echo "4. Extract and run setup scripts"
echo ""
echo "See $DEPLOY_DIR/README_DEPLOY.txt for details"
echo "=========================================="
