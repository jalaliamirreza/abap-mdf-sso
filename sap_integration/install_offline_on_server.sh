#!/bin/bash
# اسکریپت نصب offline روی سرور SAP

set -e

PACKAGES_DIR="/tmp/sap_packages"
PACKAGES_FILE="/tmp/sap_packages.tar.gz"

echo "========================================================================="
echo "نصب Offline کتابخانه‌های Python برای SAP DBF Converter"
echo "========================================================================="
echo ""

# بررسی نسخه Python
echo "🐍 بررسی Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ خطا: python3 یافت نشد!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# بررسی pip
echo "📦 بررسی pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ خطا: pip3 یافت نشد!"
    echo "در حال تلاش برای نصب pip..."
    python3 -m ensurepip --upgrade || {
        echo "❌ نصب pip ناموفق بود. لطفاً pip3 را به صورت دستی نصب کنید."
        exit 1
    }
fi

PIP_VERSION=$(pip3 --version 2>&1)
echo "✅ $PIP_VERSION"
echo ""

# بررسی وجود فایل
echo "🔍 بررسی فایل پکیج‌ها..."
if [ ! -f "$PACKAGES_FILE" ]; then
    echo "❌ خطا: فایل $PACKAGES_FILE یافت نشد!"
    echo ""
    echo "لطفاً ابتدا فایل sap_packages.tar.gz را به /tmp منتقل کنید:"
    echo "  scp sap_packages.tar.gz user@$(hostname):/tmp/"
    echo ""
    exit 1
fi

FILE_SIZE=$(du -h "$PACKAGES_FILE" | cut -f1)
echo "✅ فایل یافت شد: $PACKAGES_FILE ($FILE_SIZE)"
echo ""

# باز کردن بسته
echo "📦 در حال باز کردن بسته..."
cd /tmp
tar -xzf sap_packages.tar.gz

if [ ! -d "$PACKAGES_DIR" ]; then
    echo "❌ خطا: دایرکتوری $PACKAGES_DIR یافت نشد!"
    exit 1
fi

# بررسی تعداد پکیج‌ها
PKG_COUNT=$(ls -1 $PACKAGES_DIR/*.whl $PACKAGES_DIR/*.tar.gz 2>/dev/null | wc -l)
echo "✅ تعداد پکیج‌ها: $PKG_COUNT"
echo ""

# نمایش لیست پکیج‌ها
echo "📋 پکیج‌های موجود:"
ls -1 $PACKAGES_DIR/*.whl $PACKAGES_DIR/*.tar.gz 2>/dev/null | while read file; do
    echo "  - $(basename $file)"
done
echo ""

# نصب
echo "💿 در حال نصب پکیج‌ها (--user mode)..."
echo "این ممکن است چند دقیقه طول بکشد..."
echo ""

pip3 install --user --no-index --find-links=$PACKAGES_DIR pandas openpyxl xlrd

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ نصب با موفقیت انجام شد!"
    echo ""

    # تست
    echo "🧪 تست نصب..."
    python3 << 'EOF'
try:
    import pandas as pd
    import openpyxl
    import xlrd

    print("=" * 70)
    print("✅ pandas version:", pd.__version__)
    print("✅ openpyxl version:", openpyxl.__version__)
    print("✅ xlrd version:", xlrd.__version__)
    print("=" * 70)
    print("")
    print("🎉 همه کتابخانه‌ها با موفقیت نصب شدند!")
    print("")

except ImportError as e:
    print("❌ خطا در import:", e)
    exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================================================="
        echo "✅ نصب موفقیت‌آمیز بود!"
        echo "========================================================================="
        echo ""
        echo "مراحل بعدی:"
        echo ""
        echo "1. اگر از کاربر SAP (<sid>adm) استفاده می‌کنید، با آن کاربر هم نصب کنید:"
        echo "   su - <sid>adm"
        echo "   pip3 install --user --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd"
        echo ""
        echo "2. تست اسکریپت Python:"
        echo "   cd /usr/sap/scripts/dbf_converter"
        echo "   python3 sap_integration/sap_xls_to_dbf.py --help"
        echo ""
        echo "3. پاکسازی فایل‌های موقت (اختیاری):"
        echo "   rm -rf /tmp/sap_packages /tmp/sap_packages.tar.gz"
        echo ""
        echo "========================================================================="
    else
        echo ""
        echo "❌ خطا در تست! لطفاً لاگ‌ها را بررسی کنید."
        exit 1
    fi

else
    echo ""
    echo "❌ خطا در نصب پکیج‌ها!"
    echo ""
    echo "لطفاً موارد زیر را بررسی کنید:"
    echo "1. نسخه Python (باید 3.6 یا بالاتر باشد)"
    echo "2. دسترسی write به ~/.local/lib/python*/site-packages/"
    echo "3. فضای کافی در home directory"
    echo ""
    exit 1
fi
