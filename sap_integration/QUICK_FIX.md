# رفع سریع خطا: "No module named 'csv_to_dbf_complete'"

این خطا به این دلیل است که فایل‌ها درست کپی نشده‌اند.

---

## ❌ مشکل:

```
2025-11-28 07:44:32,438 - ERROR - Failed to import conversion modules: No module named 'csv_to_dbf_complete'
```

## ✅ راه‌حل:

### گام 1: بررسی ساختار فعلی

```bash
cd ~/scripts
ls -la
```

**احتمالاً چیزی شبیه این می‌بینید:**
```
sap_xls_to_dbf.py
DSKKAR00.XLS
DSKWOR00.XLS
```

### گام 2: ساختار صحیح

باید این ساختار را داشته باشید:

```
~/scripts/
├── tools/
│   └── csv_to_dbf_complete.py
├── src/
│   └── utils/
│       └── iran_system_encoding.py
└── sap_xls_to_dbf.py
```

### گام 3: کپی فایل‌های لازم

#### روش A: کپی از پروژه اصلی

```bash
cd ~/scripts

# کپی tools/
cp -r /path/to/abap-mdf-sso/tools .

# کپی src/
cp -r /path/to/abap-mdf-sso/src .

# بررسی ساختار
ls -la
```

#### روش B: دانلود مستقیم از GitHub

```bash
cd ~/scripts

# دانلود tools/
git clone --depth 1 --no-checkout https://github.com/jalaliamirreza/abap-mdf-sso.git temp
cd temp
git sparse-checkout set tools src
git checkout
mv tools ../
mv src ../
cd ..
rm -rf temp
```

#### روش C: استفاده از کل پروژه

```bash
# حذف فایل‌های جاری
rm -rf ~/scripts/*

# کلون کامل پروژه
cd ~
git clone https://github.com/jalaliamirreza/abap-mdf-sso.git scripts

# اجرا از داخل پروژه
cd ~/scripts
python3 sap_integration/sap_xls_to_dbf.py \
  DSKKAR00.XLS \
  DSKWOR00.XLS \
  ~/scripts/pack/out
```

### گام 4: تست

```bash
cd ~/scripts

# بررسی وجود فایل‌ها
test -f tools/csv_to_dbf_complete.py && echo "✅ tools/csv_to_dbf_complete.py موجود است" || echo "❌ tools/csv_to_dbf_complete.py یافت نشد"
test -f src/utils/iran_system_encoding.py && echo "✅ src/utils/iran_system_encoding.py موجود است" || echo "❌ src/utils/iran_system_encoding.py یافت نشد"
test -f sap_xls_to_dbf.py && echo "✅ sap_xls_to_dbf.py موجود است" || echo "❌ sap_xls_to_dbf.py یافت نشد"
```

**خروجی مورد انتظار:**
```
✅ tools/csv_to_dbf_complete.py موجود است
✅ src/utils/iran_system_encoding.py موجود است
✅ sap_xls_to_dbf.py موجود است
```

### گام 5: اجرای دوباره

```bash
cd ~/scripts
python3 sap_xls_to_dbf.py DSKKAR00.XLS DSKWOR00.XLS ~/scripts/pack/out
```

---

## 📦 نصب برای محیط Production (توصیه می‌شود)

برای استفاده در SAP، بهتر است ساختار استاندارد را رعایت کنید:

```bash
# ایجاد دایرکتوری استاندارد
sudo mkdir -p /usr/sap/scripts/dbf_converter
cd /usr/sap/scripts/dbf_converter

# کپی کل پروژه
sudo git clone https://github.com/jalaliamirreza/abap-mdf-sso.git .

# یا اگر git ندارید:
sudo scp -r /path/to/local/abap-mdf-sso/* .

# تنظیم مجوزها
sudo chmod +x sap_integration/sap_xls_to_dbf.py
sudo chmod 755 -R /usr/sap/scripts/dbf_converter

# تست
python3 sap_integration/sap_xls_to_dbf.py \
  /path/to/DSKKAR00.XLS \
  /path/to/DSKWOR00.XLS \
  /tmp/output
```

---

## 🔍 عیب‌یابی

### خطا: "tools/ directory not found"

```bash
# بررسی مسیر فعلی
pwd

# بررسی محتویات
find . -name "csv_to_dbf_complete.py"

# اگر فایل در مسیر دیگری هست:
# کپی به جای درست
```

### خطا: "Permission denied"

```bash
# تغییر ownership به کاربر SAP
sudo chown -R <sid>adm:sapsys /usr/sap/scripts/dbf_converter

# یا اجرا با کاربر درست
su - <sid>adm
cd /usr/sap/scripts/dbf_converter
python3 sap_integration/sap_xls_to_dbf.py ...
```

---

## 📞 در صورت ادامه مشکل

اگر خطا ادامه داشت، این اطلاعات را ارسال کنید:

```bash
cd ~/scripts
pwd
ls -la
ls -la tools/ 2>/dev/null || echo "tools/ not found"
ls -la src/utils/ 2>/dev/null || echo "src/utils/ not found"
python3 --version
```

---

## ✅ خلاصه

**مشکل:** فایل‌های `tools/` و `src/` کپی نشده‌اند

**راه‌حل:** کپی کردن کامل ساختار پروژه یا فقط دایرکتوری‌های `tools/` و `src/`

**دستور سریع:**
```bash
cd ~/scripts
cp -r /path/to/abap-mdf-sso/tools .
cp -r /path/to/abap-mdf-sso/src .
python3 sap_xls_to_dbf.py DSKKAR00.XLS DSKWOR00.XLS ~/scripts/pack/out
```
