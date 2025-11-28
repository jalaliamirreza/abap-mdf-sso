# SAP Integration - تولید مستقیم DBF از SAP

این پوشه شامل فایل‌های لازم برای یکپارچه‌سازی تولید DBF با SAP است تا کاربران بتوانند **مستقیماً** از SAP فایل‌های DBF دریافت کنند.

---

## 📊 وضعیت فعلی vs آینده

### ❌ قبل (وضعیت فعلی):
```
SAP Report
    ↓
Excel Export (DSKKAR00.XLS + DSKWOR00.XLS)
    ↓
کانورتر خارجی (شرکت دیگر)
    ↓
DBF Files
    ↓
آپلود به SSO
```

### ✅ بعد (با این راه‌حل):
```
SAP Report
    ↓
کلیک دکمه "DBF" 🚀
    ↓
DBF Files (مستقیم!)
    ↓
آپلود به SSO
```

---

## 📁 فایل‌ها

### 1. `sap_xls_to_dbf.py`
**Python script اصلی برای تبدیل**
- ✅ خواندن فایل‌های XLS خروجی SAP (Tab-delimited UTF-16)
- ✅ ارزیابی فرمول‌های Excel (`=REPT` برای zero-padding)
- ✅ تبدیل به DBF با Iran System encoding
- ✅ پشتیبانی از ساختار SSO 2024 (25+29 فیلد)

**استفاده:**
```bash
python3 sap_xls_to_dbf.py DSKKAR00.XLS DSKWOR00.XLS /output/dir/
```

### 2. `ZHR_INS_REP_FILES_DBF.abap`
**ABAP Include برای گزارش اصلی**
- ✅ دکمه جدید "DBF" در toolbar
- ✅ Export داده‌های انتخاب شده به XLS موقت
- ✅ فراخوانی Python script از طریق External Command
- ✅ دانلود فایل‌های DBF به PC کاربر
- ✅ پاکسازی خودکار فایل‌های موقت

**استفاده:**
```abap
" در Report اصلی:
INCLUDE zhr_ins_rep_files_dbf.

" در USER_COMMAND:
WHEN 'ZDBF'.
  PERFORM fill_dbf_direct.
```

### 3. `ZABAP_DBF_CONVERTER.abap`
**نسخه قدیمی‌تر** (استفاده نکنید - فقط برای مرجع)

### 4. `sap_dbf_wrapper.py`
**نسخه قدیمی‌تر** (استفاده نکنید - از `sap_xls_to_dbf.py` استفاده کنید)

### 5. `INSTALLATION_GUIDE.md`
**📖 راهنمای کامل نصب و پیکربندی**
- مراحل نصب Python روی SAP Application Server
- تعریف External Command (SM69)
- تغییرات ABAP (PF-STATUS, USER_COMMAND)
- تست و عیب‌یابی

---

## 🚀 نصب سریع

### گام 1: نصب Python Scripts
```bash
# روی SAP Application Server
mkdir -p /usr/sap/scripts/dbf_converter
cd /usr/sap/scripts/dbf_converter

# کپی فایل‌ها
# از local: scp -r tools/ src/ sap_integration/ <HOST>:/usr/sap/scripts/dbf_converter/

chmod +x sap_xls_to_dbf.py
```

### گام 2: تعریف External Command
```
Transaction: SM69
Command Name: ZDBF_XLS_CONVERT
Command:      /usr/bin/python3
Parameters:   /usr/sap/scripts/dbf_converter/sap_xls_to_dbf.py
✅ Additional parameters allowed
```

### گام 3: تغییرات ABAP
```abap
" 1. اضافه کردن Include
INCLUDE zhr_ins_rep_files_dbf.

" 2. اضافه کردن دکمه به PF-STATUS (SE41)
Function Code: ZDBF
Function Text: تولید DBF مستقیم
Icon:          @17@

" 3. اضافه کردن به USER_COMMAND
WHEN 'ZDBF'.
  PERFORM fill_dbf_direct.
```

### گام 4: فعال‌سازی و تست
```
✅ Activate all objects
✅ اجرای گزارش
✅ انتخاب رکوردها
✅ کلیک "DBF"
✅ دریافت فایل‌ها!
```

---

## 📊 تست شده با داده‌های واقعی

### ✅ نمونه تست:
- **تعداد کارگران:** 652 نفر
- **خروجی KAR:** 1.2 KB (1 ردیف header)
- **خروجی WOR:** 300 KB (652 ردیف worker)
- **Encoding:** Iran System (100% دقیق)
- **ساختار:** SSO 2024 (25 فیلد KAR + 29 فیلد WOR)
- **نتیجه:** ✅ پذیرفته شده توسط سایت SSO

---

## 🔍 جزئیات فنی

### فرمول‌های Excel پشتیبانی شده:
```excel
=REPT(0,10-LEN("0853900011"))&"0853900011"  → "0853900011"
=REPT(0,2-LEN("04"))&"04"                   → "04"
=REPT(0,11)&"1"                             → "00000000001"
```

### Iran System Encoding:
- ✅ حروف فارسی با فرم‌های مختلف (isolated, initial, medial, final)
- ✅ ترتیب visual (چپ به راست)
- ✅ اعداد فارسی → اعداد انگلیسی (۰-۹ → 0-9)
- ✅ حفظ فضاها (spaces preserved)
- ✅ Language Driver ID: 0x7E

### ساختار DBF:
**DSKKAR00.DBF (Header):**
- 25 فیلد
- 311 بایت هر رکورد
- 1 ردیف (خلاصه کل کارگران)

**DSKWOR00.DBF (Workers):**
- 29 فیلد
- 469 بایت هر رکورد
- N ردیف (یک ردیف برای هر کارگر)

---

## 🛠️ عیب‌یابی

### مشکل: "Command not found"
```bash
# بررسی مسیر Python
which python3
# اصلاح در SM69
```

### مشکل: "Module not found"
```bash
pip3 install pandas openpyxl xlrd
```

### مشکل: "Permission denied"
```bash
chmod 755 /usr/sap/scripts/dbf_converter/
chmod +x /usr/sap/scripts/dbf_converter/*.py
```

### مشکل: "DBF files not created"
```bash
# بررسی لاگ
tail -f /tmp/sap_dbf_converter.log
```

---

## 📚 مستندات کامل

برای راهنمای کامل نصب، **حتماً** فایل `INSTALLATION_GUIDE.md` را مطالعه کنید.

---

## ✅ مزایا

- 🚀 **سریع:** یک کلیک، دریافت DBF
- ✅ **دقیق:** Iran System encoding صد درصد
- 🔒 **امن:** بدون نیاز به نرم‌افزار شخص ثالث
- 💰 **صرفه‌جو:** بدون هزینه کانورتر
- 👥 **کاربرپسند:** بدون مرحله دستی
- 📊 **مطابق:** SSO 2024 structure

---

## 🎯 نتیجه

کاربران حالا می‌توانند:
```
1. گزارش را اجرا کنند
2. رکوردها را انتخاب کنند
3. دکمه "DBF" را بزنند
4. فایل‌های DBF را مستقیماً دریافت کنند
5. به سایت SSO آپلود کنند ✓
```

**تمام!** 🎉
