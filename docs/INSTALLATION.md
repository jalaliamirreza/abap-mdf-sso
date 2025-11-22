# راهنمای نصب و پیکربندی
# Installation and Configuration Guide

## فهرست مطالب / Table of Contents

1. [پیش‌نیازها / Prerequisites](#prerequisites)
2. [نصب در SAP / SAP Installation](#sap-installation)
3. [نصب ابزارهای Python / Python Tools Installation](#python-installation)
4. [پیکربندی / Configuration](#configuration)
5. [تست / Testing](#testing)

---

## <a name="prerequisites"></a>پیش‌نیازها / Prerequisites

### سیستم SAP / SAP System

- SAP S/4HANA or SAP ECC 6.0 or higher
- ماژول HCM نصب شده باشد
- دسترسی به تراکنش‌های زیر:
  - SE38 (ABAP Editor)
  - SE11 (Data Dictionary)
  - PA30 (Maintain HR Master Data)
  - PC00_M40_CALC (Payroll Driver)

### دسترسی‌های مورد نیاز / Required Authorizations

- S_DEVELOP: برای ایجاد برنامه‌های ABAP
- S_DATASET: برای دسترسی به فایل‌ها
- S_TCODE: برای اجرای تراکنش‌های HR
- P_ORGIN: برای دسترسی به اطلاعات پرسنل
- P_PERNR: برای دسترسی به شماره پرسنلی

### نرم‌افزارهای خارجی / External Software

- Python 3.8 یا بالاتر
- pip (Python Package Manager)
- Git (اختیاری)

---

## <a name="sap-installation"></a>نصب در SAP / SAP Installation

### مرحله 1: ایجاد Infotype سفارشی (اختیاری)

اگر سیستم SAP شما دارای Infotype برای شماره بیمه نیست:

1. وارد تراکنش **PM01** شوید
2. Infotype جدید با شماره **0185** ایجاد کنید
3. فیلدهای زیر را اضافه کنید:
   - `INSNO`: شماره بیمه (CHAR20)
   - `INS_START`: تاریخ شروع بیمه (DATUM)
   - `INS_END`: تاریخ پایان بیمه (DATUM)

### مرحله 2: آپلود برنامه ABAP

1. فایل `src/abap/ZHCM_SSO_EXTRACT.abap` را باز کنید
2. وارد تراکنش **SE38** شوید
3. برنامه جدید با نام **ZHCM_SSO_EXTRACT** ایجاد کنید
4. کد ABAP را کپی و پیست کنید
5. برنامه را Activate کنید (Ctrl+F3)

### مرحله 3: تنظیمات Wage Types

در تراکنش **V_T512W_D**، Wage Types زیر را بررسی کنید:

```
/101 - حقوق پایه (Base Salary)
/102 - اضافه کار (Overtime)
/103 - مزایا (Benefits)
/104 - مزایای مشمول بیمه (Insured Benefits)
/105 - فوق‌العاده (Allowances)
```

اگر Wage Types متفاوتی دارید، فایل `config/field_mappings.json` را ویرایش کنید.

### مرحله 4: ایجاد Variant

1. برنامه **ZHCM_SSO_EXTRACT** را در SE38 اجرا کنید
2. پارامترهای پیش‌فرض را وارد کنید
3. از منوی **Goto > Variants > Save as Variant** استفاده کنید
4. Variant را با نام **MONTHLY** ذخیره کنید

### مرحله 5: زمان‌بندی Job (اختیاری)

برای اجرای خودکار ماهانه:

1. وارد تراکنش **SM36** شوید
2. Job جدید ایجاد کنید
3. Step اضافه کنید:
   - Name: ZHCM_SSO_EXTRACT
   - Variant: MONTHLY
4. زمان‌بندی ماهانه تنظیم کنید

---

## <a name="python-installation"></a>نصب ابزارهای Python

### مرحله 1: نصب Python

#### Windows:
```powershell
# دانلود از python.org
# یا استفاده از Chocolatey
choco install python
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS:
```bash
brew install python3
```

### مرحله 2: Clone کردن Repository

```bash
git clone https://github.com/your-org/abap-mdf-sso.git
cd abap-mdf-sso
```

### مرحله 3: ایجاد Virtual Environment

```bash
# ایجاد virtual environment
python3 -m venv venv

# فعال‌سازی
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### مرحله 4: نصب وابستگی‌ها

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### بررسی نصب

```bash
python src/utils/generate_dbf.py --help
```

باید راهنمای استفاده نمایش داده شود.

---

## <a name="configuration"></a>پیکربندی / Configuration

### مرحله 1: تنظیم فایل SAP Config

```bash
cp config/sap-config.template.json config/sap-config.json
```

ویرایش `config/sap-config.json`:

```json
{
  "sap_connection": {
    "host": "sap.yourcompany.com",
    "system_number": "00",
    "client": "100",
    "user": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "language": "FA"
  }
}
```

⚠️ **هشدار امنیتی**: فایل `sap-config.json` را به Git اضافه نکنید!

### مرحله 2: تنظیم Field Mappings

فایل `config/field_mappings.json` را بررسی کنید و در صورت نیاز ویرایش کنید:

```json
{
  "wage_types": {
    "base_salary": ["/101", "/110"],
    "overtime": ["/102", "/120"],
    "benefits": ["/103", "/104", "/105"]
  }
}
```

### مرحله 3: تست پیکربندی

```bash
python tests/test_dbf_generation.py
```

---

## <a name="testing"></a>تست / Testing

### تست با داده‌های نمونه

```bash
# اجرای تست‌ها
python tests/test_dbf_generation.py

# تولید DBF از داده‌های نمونه
python src/utils/generate_dbf.py \
  --input tests/sample_data.json \
  --output tests/output/test.dbf
```

### بررسی فایل DBF

می‌توانید از نرم‌افزارهای زیر برای باز کردن DBF استفاده کنید:

- **DBF Viewer 2000** (Windows)
- **LibreOffice Calc** (همه پلتفرم‌ها)
- **DB Browser for SQLite** با پلاگین DBF

### تست آپلود در سایت تامین اجتماعی

1. وارد سایت تامین اجتماعی شوید: https://www.tamin.ir
2. بخش کارفرمایان > لیست بیمه
3. فایل DBF تست را آپلود کنید
4. خطاها را بررسی کنید
5. در صورت نیاز، تنظیمات را اصلاح کنید

---

## عیب‌یابی / Troubleshooting

### خطای "Module not found: dbfpy3"

```bash
pip install dbfpy3
```

### خطا در اتصال به SAP

- سرور SAP در دسترس است؟
- نام کاربری و رمز عبور صحیح است؟
- Firewall مشکلی ایجاد نمی‌کند؟

### خطای کدگذاری فارسی

مطمئن شوید:
- فایل JSON با encoding UTF-8 ذخیره شده
- فایل DBF با Windows-1256 تولید می‌شود

### خطای اعتبارسنجی کد ملی

کد ملی باید:
- 10 رقم باشد
- الگوریتم checksum را بگذراند
- تمام ارقام یکسان نباشد

---

## منابع بیشتر / Additional Resources

- [مستندات SAP HCM](https://help.sap.com/hcm)
- [راهنمای تامین اجتماعی](https://www.tamin.ir)
- [Python DBF Documentation](https://pypi.org/project/dbfpy3/)

---

## پشتیبانی / Support

برای مشکلات فنی:
- Issue در GitHub باز کنید
- به تیم توسعه ایمیل بزنید
- مستندات را مطالعه کنید

---

**نسخه**: 1.0
**آخرین بروزرسانی**: 1403/11/01
