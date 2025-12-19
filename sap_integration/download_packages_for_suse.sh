#!/bin/bash
# اسکریپت دانلود پکیج‌های Python برای نصب offline روی SUSE SLES 15

set -e  # خروج در صورت خطا

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES_DIR="$SCRIPT_DIR/sap_packages"
OUTPUT_FILE="$SCRIPT_DIR/sap_packages.tar.gz"

echo "========================================================================="
echo "دانلود پکیج‌های Python برای نصب Offline روی SUSE SLES 15"
echo "========================================================================="
echo ""

# بررسی pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ خطا: pip3 یافت نشد!"
    echo "لطفاً Python 3 و pip3 را نصب کنید."
    exit 1
fi

echo "✅ pip3 version: $(pip3 --version)"
echo ""

# پاک کردن دایرکتوری قبلی (اگر وجود دارد)
if [ -d "$PACKAGES_DIR" ]; then
    echo "🗑️  پاک کردن دایرکتوری قبلی..."
    rm -rf "$PACKAGES_DIR"
fi

# ایجاد دایرکتوری جدید
echo "📁 ایجاد دایرکتوری: $PACKAGES_DIR"
mkdir -p "$PACKAGES_DIR"

echo ""
echo "📦 دانلود پکیج‌ها (برای Python 3.6 / SUSE SLES 15)..."
echo "این ممکن است چند دقیقه طول بکشد..."
echo ""

# دانلود pandas و dependencies
echo "1/3 دانلود pandas و dependencies..."
pip3 download -d "$PACKAGES_DIR" 'pandas>=1.1.0,<2.0.0' --no-deps
pip3 download -d "$PACKAGES_DIR" 'numpy>=1.15.4,<1.20.0'
pip3 download -d "$PACKAGES_DIR" 'python-dateutil>=2.7.3'
pip3 download -d "$PACKAGES_DIR" 'pytz>=2017.2'
pip3 download -d "$PACKAGES_DIR" 'six>=1.5'

# دانلود openpyxl و dependencies
echo "2/3 دانلود openpyxl و dependencies..."
pip3 download -d "$PACKAGES_DIR" 'openpyxl>=3.0.0,<3.1.0'
pip3 download -d "$PACKAGES_DIR" 'et-xmlfile'

# دانلود xlrd
echo "3/3 دانلود xlrd..."
pip3 download -d "$PACKAGES_DIR" 'xlrd>=1.2.0,<2.0.0'

echo ""
echo "✅ دانلود کامل شد!"
echo ""

# بررسی تعداد فایل‌ها
FILE_COUNT=$(ls -1 "$PACKAGES_DIR" | wc -l)
echo "📊 تعداد فایل‌های دانلود شده: $FILE_COUNT"
echo ""

# نمایش لیست فایل‌ها
echo "📋 لیست فایل‌ها:"
ls -lh "$PACKAGES_DIR"
echo ""

# فشرده‌سازی
echo "🗜️  فشرده‌سازی پکیج‌ها..."
cd "$SCRIPT_DIR"
tar -czf "$OUTPUT_FILE" sap_packages/

if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "✅ فایل فشرده ایجاد شد: $OUTPUT_FILE"
    echo "📏 حجم: $FILE_SIZE"
    echo ""

    echo "========================================================================="
    echo "✅ موفقیت آمیز!"
    echo "========================================================================="
    echo ""
    echo "مراحل بعدی:"
    echo "1. فایل زیر را به سرور SAP منتقل کنید:"
    echo "   $OUTPUT_FILE"
    echo ""
    echo "2. روی سرور SAP، دستورات زیر را اجرا کنید:"
    echo "   scp $OUTPUT_FILE <user>@<sap-server>:/tmp/"
    echo ""
    echo "3. روی سرور SAP:"
    echo "   cd /tmp"
    echo "   tar -xzf sap_packages.tar.gz"
    echo "   pip3 install --user --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd"
    echo ""
    echo "برای جزئیات بیشتر، فایل OFFLINE_INSTALLATION.md را مطالعه کنید."
    echo "========================================================================="
else
    echo "❌ خطا در ایجاد فایل فشرده!"
    exit 1
fi
