#!/bin/bash
###############################################################################
# SAP Payroll ZIP Creation Wrapper Script
#
# This script wraps the Python ZIP creation tool for easier execution
# Can be used for:
# - Manual execution
# - Cron jobs
# - Called from ABAP via SXPG_COMMAND_EXECUTE
#
# Usage:
#   ./create_payroll_zip.sh [directory] [zip_name]
#
# Examples:
#   ./create_payroll_zip.sh
#   ./create_payroll_zip.sh /usr/sap/scripts/dbf_converter/tmp/
#   ./create_payroll_zip.sh /usr/sap/scripts/dbf_converter/tmp/ custom.zip
###############################################################################

# Default configuration
DEFAULT_DIR="/usr/sap/scripts/dbf_converter/tmp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/create_payroll_zip.py"
LOG_FILE="/var/log/sap_payroll_zip.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to log errors
error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    log "ERROR: $1"
}

# Function to log success
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

# Function to log warnings
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    error "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Get directory from argument or use default
WORK_DIR="${1:-$DEFAULT_DIR}"

# Get ZIP name from argument (optional)
ZIP_NAME="${2:-}"

# Verify directory exists
if [ ! -d "$WORK_DIR" ]; then
    error "Directory does not exist: $WORK_DIR"
    exit 1
fi

# Log execution start
log "=========================================="
log "Starting ZIP creation"
log "Directory: $WORK_DIR"
log "ZIP Name: ${ZIP_NAME:-default (payroll_export.zip)}"
log "=========================================="

# Execute Python script
if [ -n "$ZIP_NAME" ]; then
    # ZIP name specified
    python3 "$PYTHON_SCRIPT" "$WORK_DIR" "$ZIP_NAME"
else
    # Use default ZIP name
    python3 "$PYTHON_SCRIPT" "$WORK_DIR"
fi

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    success "ZIP file created successfully"
    log "=========================================="

    # List ZIP files in directory
    log "ZIP files in directory:"
    ls -lh "$WORK_DIR"/*.zip 2>/dev/null | while read -r line; do
        log "  $line"
    done

    exit 0
else
    error "ZIP creation failed with exit code: $EXIT_CODE"
    log "=========================================="
    exit $EXIT_CODE
fi
