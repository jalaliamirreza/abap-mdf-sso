# SAP Payroll to Iranian Social Security (MDF) Integration
# استخراج حقوق و دستمزد SAP به فرمت دیسکت بیمه تامین اجتماعی

## English Description

This project provides integration between SAP S/4HANA HCM (Human Capital Management) and the Iranian Social Security Organization (SSO - تامین اجتماعی). It extracts payroll and personnel contract data from SAP and converts it to the DBF (dBase) format required for insurance diskette submission to the Iranian Social Security website.

### Features

- Extract payroll data from SAP HCM module
- Extract personnel contract information
- Generate DBF files in the format required by Iranian Social Security
- Support for monthly insurance list (لیست ماهانه بیمه)
- Configurable field mappings
- Data validation and error checking

### Architecture

```
SAP S/4HANA HCM
    |
    v
ABAP Program (Data Extraction)
    |
    v
Data Transformation Layer
    |
    v
DBF File Generator
    |
    v
Iranian Social Security Format (MDF)
```

### Components

1. **ABAP Programs** (`/src/abap/`): SAP programs for data extraction
2. **Configuration** (`/config/`): Field mappings and format specifications
3. **Documentation** (`/docs/`): Iranian Social Security format documentation
4. **Utilities** (`/src/utils/`): DBF generation utilities

---

## توضیحات فارسی

این پروژه یک پل ارتباطی بین سیستم SAP S/4HANA (ماژول مدیریت سرمایه انسانی) و سازمان تامین اجتماعی ایران فراهم می‌کند. این سیستم اطلاعات حقوق و دستمزد و قراردادهای پرسنلی را از SAP استخراج کرده و به فرمت DBF (دی‌بیس) مورد نیاز برای ارسال دیسکت بیمه به وب‌سایت تامین اجتماعی تبدیل می‌کند.

### امکانات

- استخراج اطلاعات حقوق و دستمزد از ماژول HCM سیستم SAP
- استخراج اطلاعات قراردادهای پرسنلی
- تولید فایل‌های DBF به فرمت مورد نیاز سازمان تامین اجتماعی
- پشتیبانی از لیست ماهانه بیمه
- قابلیت پیکربندی نگاشت فیلدها
- اعتبارسنجی داده‌ها و بررسی خطا

### ساختار پروژه

```
📁 abap-mdf-sso/
├── 📁 src/
│   ├── 📁 abap/          # برنامه‌های ABAP برای استخراج داده
│   ├── 📁 utils/         # ابزارهای کمکی برای تولید DBF
│   └── 📁 transform/     # منطق تبدیل داده‌ها
├── 📁 config/            # فایل‌های پیکربندی و نگاشت فیلدها
├── 📁 docs/              # مستندات فرمت تامین اجتماعی
└── 📁 tests/             # داده‌های نمونه و تست‌ها
```

### فیلدهای اصلی دیسکت بیمه

فایل DBF تامین اجتماعی شامل فیلدهای زیر است:

1. **شماره بیمه** (Insurance Number)
2. **کد ملی** (National ID)
3. **نام** (First Name)
4. **نام خانوادگی** (Last Name)
5. **نام پدر** (Father's Name)
6. **تاریخ تولد** (Birth Date)
7. **روزهای کارکرد** (Working Days)
8. **حقوق مبنا** (Base Salary)
9. **اضافه کار** (Overtime)
10. **مزایای مشمول** (Taxable Benefits)
11. **جمع مزایا** (Total Benefits)

### نحوه استفاده

#### 1. نصب و پیکربندی

```bash
# Clone the repository
git clone <repository-url>
cd abap-mdf-sso

# Configure SAP connection
cp config/sap-config.template.json config/sap-config.json
# Edit config/sap-config.json with your SAP credentials
```

#### 2. اجرای برنامه ABAP در SAP

1. وارد سیستم SAP شوید
2. تراکنش SE38 را اجرا کنید
3. برنامه `ZHCM_SSO_EXTRACT` را اجرا کنید
4. ماه و سال مورد نظر را وارد کنید
5. خروجی را دانلود کنید

#### 3. تولید فایل DBF

```bash
# Run the DBF generator
python src/utils/generate_dbf.py --input data/payroll.json --output diskette.dbf
```

### پیش‌نیازها

- SAP S/4HANA with HCM module
- ABAP development authorization
- Python 3.8+ (for DBF generation utilities)
- Required Python packages: `dbfpy`, `pandas`

### نصب وابستگی‌های Python

```bash
pip install -r requirements.txt
```

## Iranian Social Security (MDF) Format Specification

The Iranian Social Security Organization requires insurance data in a specific DBF format. The structure includes:

- **File Type**: dBase III/IV (.dbf)
- **Character Encoding**: Windows-1256 (Persian/Arabic)
- **Record Structure**: Fixed field widths and types

See `/docs/SSO_FORMAT_SPEC.md` for detailed field specifications.

## Development

### Adding New Fields

1. Update the ABAP extraction program in `/src/abap/`
2. Add field mapping in `/config/field_mappings.json`
3. Update the DBF structure in `/src/utils/dbf_structure.py`

### Testing

```bash
# Run tests with sample data
python tests/test_dbf_generation.py
```

## License

This project is proprietary software developed for specific client requirements.

## Support

For issues and questions, please contact the development team.

---

## نکات مهم

⚠️ **توجه**:
- اطمینان حاصل کنید که اطلاعات شماره بیمه و کد ملی صحیح است
- قبل از ارسال به سایت تامین اجتماعی، فایل DBF را با داده‌های نمونه تست کنید
- از نسخه پشتیبان قبل از اجرای برنامه تهیه کنید
- فرمت تاریخ باید شمسی (جلالی) باشد

## مراجع

- [سایت تامین اجتماعی](https://www.tamin.ir)
- SAP HCM Documentation
- dBase File Format Specification
