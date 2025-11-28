# دستورالعمل نصب و راه‌اندازی DBF Direct Generation

این راهنما مراحل نصب و پیکربندی سیستم تولید مستقیم DBF از SAP را شرح می‌دهد.

---

## 📋 پیش‌نیازها

### 1. Python و کتابخانه‌های مورد نیاز

**⚠️ برای SUSE Linux Enterprise Server 15 یا سیستم‌های قدیمی‌تر:**
👉 **لطفاً فایل `SUSE_INSTALLATION.md` را مطالعه کنید!**

**برای سیستم‌های جدید (Python 3.8+):**
```bash
# بررسی نسخه Python
python3 --version

# نصب کتابخانه‌های مورد نیاز (روش 1: مستقیم)
pip3 install pandas openpyxl xlrd

# یا (روش 2: از requirements-minimal.txt)
pip3 install -r requirements-minimal.txt
```

**برای سیستم‌های قدیمی (Python 3.6+):**
```bash
# نصب نسخه‌های سازگار
pip3 install -r requirements-suse.txt

# یا مستقیم:
pip3 install 'pandas>=1.1.0,<2.0.0' 'openpyxl>=3.0.0,<3.1.0' 'xlrd>=1.2.0,<2.0.0'
```

### 2. دسترسی‌های مورد نیاز
- ✅ دسترسی به SAP Application Server file system
- ✅ دسترسی به تعریف External Command (SM69)
- ✅ دسترسی به ویرایش ABAP programs
- ✅ دسترسی به تعریف PF-STATUS

---

## 🔧 مرحله 1: نصب Python Scripts روی Application Server

### 1.1. ایجاد دایرکتوری پروژه
```bash
# ورود به SAP Application Server
ssh <SAP_USER>@<SAP_HOST>

# ایجاد دایرکتوری
mkdir -p /usr/sap/scripts/dbf_converter
cd /usr/sap/scripts/dbf_converter
```

### 1.2. کپی فایل‌های پروژه
فایل‌های زیر را به دایرکتوری `/usr/sap/scripts/dbf_converter/` کپی کنید:

```
/usr/sap/scripts/dbf_converter/
├── sap_xls_to_dbf.py           # Script اصلی
├── tools/
│   └── csv_to_dbf_complete.py  # ماژول تبدیل
└── src/
    └── utils/
        └── iran_system_encoding.py  # ماژول encoding
```

**راه کپی:**
```bash
# از ماشین local
scp -r /path/to/abap-mdf-sso/sap_integration/sap_xls_to_dbf.py <USER>@<HOST>:/usr/sap/scripts/dbf_converter/
scp -r /path/to/abap-mdf-sso/tools <USER>@<HOST>:/usr/sap/scripts/dbf_converter/
scp -r /path/to/abap-mdf-sso/src <USER>@<HOST>:/usr/sap/scripts/dbf_converter/
```

### 1.3. تنظیم مجوزها
```bash
chmod +x /usr/sap/scripts/dbf_converter/sap_xls_to_dbf.py
chmod -R 755 /usr/sap/scripts/dbf_converter/
```

### 1.4. تست Script
```bash
cd /usr/sap/scripts/dbf_converter
python3 sap_xls_to_dbf.py --help

# تست با فایل‌های نمونه
python3 sap_xls_to_dbf.py \
  /path/to/sample/DSKKAR00.XLS \
  /path/to/sample/DSKWOR00.XLS \
  /tmp/test_output
```

---

## 🔧 مرحله 2: تعریف External Command در SAP

### 2.1. ورود به Transaction SM69
```
Transaction: SM69
```

### 2.2. ایجاد Command جدید
1. کلیک **Create** (یا F5)
2. پر کردن فیلدها:

```
Command Name:        ZDBF_XLS_CONVERT
Operating System:    UNIX / Linux
```

3. **Additional Data Tab:**
```
Command:             /usr/bin/python3
Parameters:          /usr/sap/scripts/dbf_converter/sap_xls_to_dbf.py
```

4. **Security & Restrictions:**
- ☑ Execute the command with the SAP System user
- ☑ Additional parameters allowed on command line

5. **Save** و **Activate**

### 2.3. تست External Command
```
Transaction: SM49
```
1. Select: **ZDBF_XLS_CONVERT**
2. Execute with test parameters:
```
/tmp/test/KAR.XLS /tmp/test/WOR.XLS /tmp/test/output
```

---

## 🔧 مرحله 3: تغییرات ABAP

### 3.1. اضافه کردن Include جدید

**در Report `ZHR_INS_REP`:**

```abap
REPORT zhr_ins_rep.
INCLUDE zhr_ins_rep_data.
INCLUDE zhr_ins_rep_dsply.
INCLUDE zhr_ins_rep_files.
INCLUDE zhr_ins_rep_files_dbf.    " <<<< خط جدید
```

### 3.2. اضافه کردن دکمه DBF به PF-STATUS

**Transaction: SE41** یا **SE80**

1. باز کردن PF-STATUS `ZPY_INSURANCE_STATUS`
2. رفتن به **Application Toolbar**
3. اضافه کردن دکمه جدید:

```
Function Code:  ZDBF
Function Text:  تولید DBF مستقیم
Icon:           @17@  (یا ICON_XLS)
```

4. **Save** و **Activate**

### 3.3. اضافه کردن Handler در USER_COMMAND

**در Include `ZHR_INS_REP_DSPLY`**, در `FORM user_command`:

```abap
FORM user_command USING ucomm LIKE sy-ucomm
      rs_selfield TYPE slis_selfield.
  DATA: lt_selected_rows TYPE STANDARD TABLE OF zpy_insurance_dskw_struc.

  CASE ucomm.
    WHEN '&IC1'.
      IF rs_selfield-tabindex > 0.
        DATA(ls_selected_rows) = it01[ rs_selfield-tabindex ].
        APPEND ls_selected_rows TO lt_selected_rows.
        PERFORM select_row USING sy-ucomm rs_selfield.
      ENDIF.

    WHEN 'DSKK'.
      PERFORM fill_dskkar00.

    WHEN 'DSKW'.
      PERFORM fill_dskwor00.

    WHEN 'EXCL'.
      PERFORM fill_excel.

    WHEN 'EXCL2'.
      PERFORM fill_excel2.

    WHEN 'ZDBF'.              " <<<< دکمه جدید
      PERFORM fill_dbf_direct.

  ENDCASE.
ENDFORM.
```

### 3.4. Activate All Objects
```
Transaction: SE80
```
- Activate Report `ZHR_INS_REP`
- Activate all Includes
- Activate PF-STATUS

---

## 🔧 مرحله 4: ایجاد Custom Table/Structure (اگر وجود ندارد)

### 4.1. Structure برای XLS Output
```
Transaction: SE11
```

**Create Structure: `ZPY_INSURANCE_DSKW_STRUC_XLS`**
```abap
" همان فیلدهای ZPY_INSURANCE_DSKW_STRUC ولی با نوع STRING برای فرمول‌های Excel
DSW_ID       TYPE STRING
DSW_YY       TYPE STRING
DSW_MM       TYPE STRING
...
```

---

## ✅ مرحله 5: تست سیستم کامل

### 5.1. اجرای Report
```
Transaction: ZHR_INS_REP  (یا هر نامی که دارد)
```

### 5.2. مراحل تست:
1. ✅ انتخاب کد کارگاه
2. ✅ Execute (F8)
3. ✅ انتخاب رکوردها با checkbox
4. ✅ کلیک دکمه **تولید DBF مستقیم** (ZDBF)
5. ✅ انتخاب مسیر ذخیره فایل
6. ✅ بررسی فایل‌های DBF:
   - `DSKKAR00.DBF`
   - `DSKWOR00.DBF`

### 5.3. تست آپلود به سایت SSO
1. ورود به سایت تامین اجتماعی
2. آپلود فایل‌های DBF
3. ✅ بررسی پذیرش فایل‌ها

---

## 📝 لاگ‌ها و عیب‌یابی

### لاگ Python Script
```bash
tail -f /tmp/sap_dbf_converter.log
```

### لاگ External Command
```
Transaction: SM37  (Background Jobs)
یا
Transaction: SM21  (System Log)
```

### خطاهای متداول:

#### 1. "Command not found"
**راه‌حل:**
```bash
# بررسی مسیر Python
which python3

# اصلاح در SM69
Command: /usr/bin/python3  # یا مسیر صحیح
```

#### 2. "Module not found: pandas"
**راه‌حل:**
```bash
# نصب برای کاربر SAP
sudo -u <SAP_USER> pip3 install pandas openpyxl xlrd
```

#### 3. "Permission denied"
**راه‌حل:**
```bash
# تنظیم مجوزها
chmod 755 /usr/sap/scripts/dbf_converter/
chmod +x /usr/sap/scripts/dbf_converter/*.py
chown -R <SAP_USER>:<SAP_GROUP> /usr/sap/scripts/dbf_converter/
```

#### 4. "DBF files not found"
**راه‌حل:**
```bash
# بررسی لاگ
cat /tmp/sap_dbf_converter.log

# تست دستی
python3 /usr/sap/scripts/dbf_converter/sap_xls_to_dbf.py \
  /tmp/test/KAR.XLS \
  /tmp/test/WOR.XLS \
  /tmp/test/output
```

---

## 🎯 نتیجه نهایی

پس از اتمام این مراحل، کاربران می‌توانند:

```
1. گزارش را اجرا کنند
      ↓
2. رکوردها را انتخاب کنند
      ↓
3. دکمه "تولید DBF مستقیم" را بزنند
      ↓
4. مستقیماً فایل‌های DBF را دریافت کنند
      ↓
5. آپلود به سایت SSO ✓
```

**بدون نیاز به:**
- ❌ Export Excel
- ❌ کانورتر خارجی
- ❌ مراحل دستی اضافی

---

## 📞 پشتیبانی

در صورت بروز مشکل:
1. بررسی لاگ `/tmp/sap_dbf_converter.log`
2. بررسی SM21 و SM37 در SAP
3. تست دستی Python script
4. تماس با تیم Basis

---

## 📚 منابع

- پروژه GitHub: `jalaliamirreza/abap-mdf-sso`
- مستندات پروژه: `docs/PROJECT_OVERVIEW.md`
- راهنمای GUI: `tools/README_GUI.md`
