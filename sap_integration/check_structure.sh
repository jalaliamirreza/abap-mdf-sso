#!/bin/bash
# اسکریپت بررسی ساختار فایل‌ها

echo "بررسی ساختار فایل‌ها..."
echo ""
echo "مسیر فعلی: $(pwd)"
echo ""
echo "فایل‌های موجود در این دایرکتوری:"
ls -la
echo ""
echo "ساختار مورد نیاز:"
echo "  ~/scripts/"
echo "    ├── tools/"
echo "    │   └── csv_to_dbf_complete.py"
echo "    ├── src/"
echo "    │   └── utils/"
echo "    │       └── iran_system_encoding.py"
echo "    └── sap_xls_to_dbf.py"
