# نصب Offline برای سرورهای بدون اینترنت

این راهنما برای نصب کتابخانه‌های Python روی سرورهایی است که به اینترنت دسترسی ندارند (مثل SAP Application Server).

---

## 📋 مراحل کلی

```
1. دانلود پکیج‌ها روی ماشین با اینترنت
2. کپی به سرور
3. نصب offline روی سرور
```

---

## 🔧 مرحله 1: دانلود پکیج‌ها (روی ماشینی با اینترنت)

### الف) برای SUSE SLES 15 / Python 3.6

```bash
# ایجاد دایرکتوری برای پکیج‌ها
mkdir -p ~/sap_packages
cd ~/sap_packages

# دانلود pandas و تمام dependencies آن
pip3 download -d . 'pandas>=1.1.0,<2.0.0'

# دانلود openpyxl و dependencies
pip3 download -d . 'openpyxl>=3.0.0,<3.1.0'

# دانلود xlrd و dependencies
pip3 download -d . 'xlrd>=1.2.0,<2.0.0'
```

**نتیجه:** تمام فایل‌های `.whl` و `.tar.gz` در `~/sap_packages` ذخیره می‌شوند.

### ب) برای سیستم‌های جدید / Python 3.8+

```bash
mkdir -p ~/sap_packages
cd ~/sap_packages

pip3 download -d . pandas openpyxl xlrd
```

---

## 📦 مرحله 2: بسته‌بندی پکیج‌ها

```bash
# فشرده‌سازی پکیج‌ها
cd ~
tar -czf sap_packages.tar.gz sap_packages/

# بررسی سایز
ls -lh sap_packages.tar.gz
```

---

## 📤 مرحله 3: انتقال به سرور SAP

### روش 1: SCP (اگر SSH فعال است)

```bash
# از ماشین local
scp sap_packages.tar.gz <user>@<sap-server>:/tmp/
```

### روش 2: USB/فایل شبکه (اگر SSH غیرفعال است)

1. کپی `sap_packages.tar.gz` روی USB
2. Mount USB روی سرور
3. کپی به `/tmp/`

### روش 3: SFTP

```bash
sftp <user>@<sap-server>
put sap_packages.tar.gz /tmp/
quit
```

---

## 💿 مرحله 4: نصب Offline روی سرور

### ورود به سرور SAP

```bash
ssh <user>@<sap-server>
# یا مستقیم روی console
```

### باز کردن بسته

```bash
cd /tmp
tar -xzf sap_packages.tar.gz
cd sap_packages
ls -la
```

**خروجی مثال:**
```
pandas-1.1.5-cp36-cp36m-manylinux1_x86_64.whl
python_dateutil-2.8.2-py2.py3-none-any.whl
pytz-2023.3-py2.py3-none-any.whl
numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl
openpyxl-3.0.10-py2.py3-none-any.whl
et_xmlfile-1.1.0-py3-none-any.whl
xlrd-1.2.0-py2.py3-none-any.whl
```

### نصب offline

```bash
# نصب تمام پکیج‌ها
pip3 install --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd

# یا اگر می‌خواهید برای کاربر فعلی نصب شود (بدون sudo):
pip3 install --user --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd
```

**توضیح پارامترها:**
- `--no-index`: به pip می‌گه از PyPI استفاده نکن
- `--find-links=/tmp/sap_packages`: مسیر پکیج‌های local
- `--user`: نصب در home directory کاربر (بدون نیاز به sudo)

---

## ✅ مرحله 5: تست نصب

```bash
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

---

## 🔄 نصب برای کاربر SAP (`<sid>adm`)

معمولاً باید برای کاربر SAP هم نصب کنید:

```bash
# تغییر به کاربر SAP
su - <sid>adm

# نصب
pip3 install --user --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd

# تست
python3 -c "import pandas; print(pandas.__version__)"
```

---

## 📝 اسکریپت کامل نصب Offline

فایل: `install_offline.sh`

```bash
#!/bin/bash
# اسکریپت نصب offline برای SAP Application Server

PACKAGES_DIR="/tmp/sap_packages"
PACKAGES_FILE="/tmp/sap_packages.tar.gz"

echo "==================================================================="
echo "نصب Offline کتابخانه‌های Python برای SAP DBF Converter"
echo "==================================================================="

# بررسی وجود فایل
if [ ! -f "$PACKAGES_FILE" ]; then
    echo "❌ خطا: فایل $PACKAGES_FILE یافت نشد!"
    echo "لطفاً فایل sap_packages.tar.gz را به /tmp کپی کنید."
    exit 1
fi

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

# نصب
echo "💿 در حال نصب..."
pip3 install --user --no-index --find-links=$PACKAGES_DIR pandas openpyxl xlrd

if [ $? -eq 0 ]; then
    echo "✅ نصب با موفقیت انجام شد!"

    # تست
    echo ""
    echo "🧪 تست نصب:"
    python3 << 'EOF'
import pandas as pd
import openpyxl
import xlrd

print(f"✅ pandas: {pd.__version__}")
print(f"✅ openpyxl: {openpyxl.__version__}")
print(f"✅ xlrd: {xlrd.__version__}")
print("\n🎉 همه چیز آماده است!")
EOF

else
    echo "❌ خطا در نصب!"
    exit 1
fi

echo "==================================================================="
```

**استفاده:**
```bash
chmod +x install_offline.sh
./install_offline.sh
```

---

## 🎯 چک‌لیست کامل

### روی ماشین با اینترنت:
- [ ] دانلود پکیج‌ها با `pip3 download`
- [ ] فشرده‌سازی با `tar -czf`
- [ ] انتقال به سرور SAP

### روی سرور SAP:
- [ ] باز کردن بسته با `tar -xzf`
- [ ] نصب با `pip3 install --no-index --find-links=...`
- [ ] تست import
- [ ] نصب برای کاربر SAP (`<sid>adm`)
- [ ] تست با کاربر SAP

---

## ⚠️ نکات مهم

### 1. سازگاری Platform
مطمئن شوید پکیج‌ها را روی همان platform دانلود کنید:
```bash
# اگر سرور Linux x86_64 است:
pip3 download --platform manylinux1_x86_64 --only-binary=:all: pandas

# یا برای SUSE SLES 15:
pip3 download --platform manylinux2010_x86_64 pandas
```

### 2. نسخه Python
مطمئن شوید Python روی هر دو سیستم یکسان است:
```bash
# بررسی روی ماشین local
python3 --version

# بررسی روی سرور SAP
ssh <user>@<sap-server> python3 --version
```

### 3. فضای دیسک
بررسی فضای کافی در `/tmp`:
```bash
df -h /tmp
```

معمولاً 100-200 MB کافی است.

### 4. دسترسی‌ها
```bash
# اطمینان از دسترسی write به /tmp
ls -ld /tmp

# باید drwxrwxrwt باشد
```

---

## 🆘 عیب‌یابی

### خطا: "No matching distribution found"
**علت:** platform یا نسخه Python سازگار نیست

**راه‌حل:**
```bash
# دانلود source distribution (کندتر ولی سازگارتر)
pip3 download --no-binary :all: pandas openpyxl xlrd
```

### خطا: "Permission denied"
**راه‌حل:**
```bash
# استفاده از --user
pip3 install --user --no-index --find-links=... pandas
```

### خطا: "Could not find a version"
**راه‌حل:**
```bash
# دانلود تمام dependencies به صورت recursive
pip3 download -r requirements-suse.txt
```

---

## 📊 لیست کامل پکیج‌های مورد نیاز

برای SUSE SLES 15 / Python 3.6:

```
pandas==1.1.5
  ↳ numpy>=1.15.4
  ↳ python-dateutil>=2.7.3
    ↳ six>=1.5
  ↳ pytz>=2017.2

openpyxl==3.0.10
  ↳ et-xmlfile

xlrd==1.2.0
  (بدون dependency)
```

**تعداد کل فایل‌ها:** حدود 7-10 فایل
**حجم کل:** حدود 50-100 MB

---

## ✅ خلاصه دستورات

```bash
# 1. روی ماشین با اینترنت
mkdir ~/sap_packages
cd ~/sap_packages
pip3 download 'pandas<2.0' 'openpyxl<3.1' 'xlrd<2.0'
cd ~
tar -czf sap_packages.tar.gz sap_packages/

# 2. انتقال
scp sap_packages.tar.gz user@sap-server:/tmp/

# 3. روی سرور SAP
cd /tmp
tar -xzf sap_packages.tar.gz
pip3 install --user --no-index --find-links=/tmp/sap_packages pandas openpyxl xlrd

# 4. تست
python3 -c "import pandas; print('✅ pandas:', pandas.__version__)"
```

---

همه چیز آماده! 🚀
