# راهنمای نصب برای SUSE Linux Enterprise Server

این راهنما مخصوص نصب روی **SUSE Linux Enterprise Server 15 SP 5** و سیستم‌های مشابه با Python قدیمی‌تر است.

---

## 🔍 مرحله 1: بررسی نسخه Python

```bash
# بررسی نسخه Python
python3 --version

# انتظار می‌رود: Python 3.6.x
```

**نکته مهم:** SLES 15 SP 5 به طور پیش‌فرض Python 3.6 دارد که با pandas 2.0+ سازگار نیست.

---

## 📦 مرحله 2: نصب کتابخانه‌ها

### گزینه A: نصب مستقیم با نسخه‌های مشخص

```bash
# نصب نسخه‌های سازگار با Python 3.6
pip3 install 'pandas>=1.1.0,<2.0.0' 'openpyxl>=3.0.0,<3.1.0' 'xlrd>=1.2.0,<2.0.0'
```

### گزینه B: استفاده از فایل requirements

```bash
# استفاده از requirements-suse.txt
pip3 install -r requirements-suse.txt
```

### گزینه C: نصب نسخه‌های حداقلی (اگر گزینه‌های بالا کار نکرد)

```bash
pip3 install 'pandas==1.1.5' 'openpyxl==3.0.10' 'xlrd==1.2.0'
```

---

## ⚠️ مشکلات احتمالی و راه‌حل

### مشکل 1: خطای "Could not find a version that satisfies the requirement pandas>=2.0.0"

**علت:** نسخه Python قدیمی است (3.6)

**راه‌حل:**
```bash
# استفاده از pandas قدیمی‌تر
pip3 install 'pandas<2.0'
```

### مشکل 2: خطای "No module named 'pip'"

**راه‌حل:**
```bash
# نصب pip
python3 -m ensurepip --upgrade

# یا نصب از مخزن SUSE
zypper install python3-pip
```

### مشکل 3: خطای Permission Denied

**راه‌حل:**
```bash
# نصب برای کاربر فعلی (بدون sudo)
pip3 install --user 'pandas<2.0' 'openpyxl<3.1' 'xlrd<2.0'
```

### مشکل 4: خطای SSL/Certificate

**راه‌حل:**
```bash
# نصب با تنظیمات امنیتی کمتر (فقط در شبکه‌های امن!)
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org 'pandas<2.0'
```

---

## 🧪 مرحله 3: تست نصب

```bash
# تست import کتابخانه‌ها
python3 << 'EOF'
import pandas as pd
import openpyxl
import xlrd

print(f"✅ pandas: {pd.__version__}")
print(f"✅ openpyxl: {openpyxl.__version__}")
print(f"✅ xlrd: {xlrd.__version__}")
print("\n🎉 همه کتابخانه‌ها با موفقیت نصب شدند!")
EOF
```

**خروجی مورد انتظار:**
```
✅ pandas: 1.1.5
✅ openpyxl: 3.0.10
✅ xlrd: 1.2.0

🎉 همه کتابخانه‌ها با موفقیت نصب شدند!
```

---

## 📂 مرحله 4: کپی فایل‌های پروژه

```bash
# ایجاد دایرکتوری
mkdir -p /usr/sap/scripts/dbf_converter
cd /usr/sap/scripts/dbf_converter

# کپی فایل‌ها (از ماشین local)
# روش 1: scp
scp -r /path/to/abap-mdf-sso/sap_integration/sap_xls_to_dbf.py <user>@<host>:/usr/sap/scripts/dbf_converter/
scp -r /path/to/abap-mdf-sso/tools <user>@<host>:/usr/sap/scripts/dbf_converter/
scp -r /path/to/abap-mdf-sso/src <user>@<host>:/usr/sap/scripts/dbf_converter/

# روش 2: git clone
git clone https://github.com/jalaliamirreza/abap-mdf-sso.git
cd abap-mdf-sso
```

---

## ✅ مرحله 5: تست Script

```bash
cd /usr/sap/scripts/dbf_converter

# تست با فایل‌های نمونه
python3 sap_integration/sap_xls_to_dbf.py \
  exportgui/DSKKAR00.XLS \
  exportgui/DSKWOR00.XLS \
  /tmp/test_output
```

**خروجی مورد انتظار:**
```
================================================================================
SAP XLS to DBF Converter Started
Arguments: ['exportgui/DSKKAR00.XLS', 'exportgui/DSKWOR00.XLS', '/tmp/test_output']
================================================================================
Step 1: Reading SAP XLS files...
Reading SAP XLS file: exportgui/DSKKAR00.XLS
  Rows: 1, Columns: 25
Reading SAP XLS file: exportgui/DSKWOR00.XLS
  Rows: 652, Columns: 29
Step 2: Converting to temporary CSV...
Step 3: Converting CSV to DBF with Iran System encoding...
  Loaded header + 652 workers
  Workshop: 0853900011, Year: 4, Month: 7
✅ Conversion successful!
  Created: /tmp/test_output/DSKKAR00.DBF (1145 bytes)
  Created: /tmp/test_output/DSKWOR00.DBF (306750 bytes)
✅ All DBF files verified
```

---

## 🔧 مرحله 6: تعریف External Command در SAP

```
Transaction: SM69

Command Name:    ZDBF_XLS_CONVERT
Operating System: UNIX / Linux
Command:         /usr/bin/python3
Parameters:      /usr/sap/scripts/dbf_converter/sap_integration/sap_xls_to_dbf.py

✅ Additional parameters allowed on command line: بله
```

---

## 🐛 عیب‌یابی پیشرفته

### بررسی مسیر Python که SAP استفاده می‌کند

```bash
# به عنوان کاربر SAP (مثلاً <sid>adm)
su - <sid>adm
which python3
python3 --version
```

### بررسی کتابخانه‌های نصب شده برای کاربر SAP

```bash
su - <sid>adm
python3 -m pip list | grep -E "pandas|openpyxl|xlrd"
```

### تست با کاربر SAP

```bash
su - <sid>adm
cd /usr/sap/scripts/dbf_converter
python3 sap_integration/sap_xls_to_dbf.py \
  exportgui/DSKKAR00.XLS \
  exportgui/DSKWOR00.XLS \
  /tmp/test_sap_user
```

### بررسی لاگ Python

```bash
tail -f /tmp/sap_dbf_converter.log
```

---

## 📊 جدول سازگاری نسخه‌ها

| سیستم عامل | Python | pandas | openpyxl | xlrd | وضعیت |
|------------|--------|--------|----------|------|-------|
| SLES 15 SP5 | 3.6 | 1.1.5 | 3.0.10 | 1.2.0 | ✅ تست شده |
| SLES 15 SP4 | 3.6 | 1.1.5 | 3.0.10 | 1.2.0 | ✅ سازگار |
| RHEL 8 | 3.6-3.9 | 1.1.5-1.5.3 | 3.0.10 | 1.2.0 | ✅ سازگار |
| Ubuntu 20.04 | 3.8+ | 2.0.0+ | 3.1.0+ | 2.0.1+ | ✅ توصیه می‌شود |

---

## 🎯 نکات مهم برای SUSE

1. **استفاده از zypper:** برای نصب پکیج‌های سیستمی
   ```bash
   zypper install python3-pip python3-devel
   ```

2. **مسیر Python:** معمولاً `/usr/bin/python3`

3. **کاربر SAP:** حتماً با کاربر `<sid>adm` تست کنید

4. **فایروال:** اگر نیاز به دانلود پکیج از اینترنت دارید، پورت 443 را باز کنید

5. **Proxy:** اگر از proxy استفاده می‌کنید:
   ```bash
   export http_proxy=http://proxy.company.com:8080
   export https_proxy=http://proxy.company.com:8080
   pip3 install ...
   ```

---

## ✅ چک‌لیست نهایی

- [ ] Python 3.6+ نصب است
- [ ] pip3 کار می‌کند
- [ ] pandas < 2.0 نصب شد
- [ ] openpyxl < 3.1 نصب شد
- [ ] xlrd < 2.0 نصب شد
- [ ] فایل‌های پروژه کپی شدند
- [ ] تست script موفقیت‌آمیز بود
- [ ] External Command در SM69 تعریف شد
- [ ] تست با کاربر SAP انجام شد
- [ ] تست کامل از SAP GUI تا دریافت DBF

---

## 🆘 پشتیبانی

در صورت بروز مشکل:
1. بررسی نسخه Python: `python3 --version`
2. بررسی لاگ: `cat /tmp/sap_dbf_converter.log`
3. تست دستی script
4. بررسی SM21 و SM37 در SAP

---

## 📞 تماس

برای مشکلات خاص SUSE یا SAP، با تیم Basis تماس بگیرید.
