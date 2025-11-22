*&---------------------------------------------------------------------*
*& Report ZHCM_SSO_EXTRACT
*&---------------------------------------------------------------------*
*& استخراج اطلاعات حقوق و دستمزد برای دیسکت بیمه تامین اجتماعی
*& SAP Payroll Data Extraction for Iranian Social Security (SSO)
*&---------------------------------------------------------------------*
REPORT zhcm_sso_extract.

*----------------------------------------------------------------------*
* Type Definitions
*----------------------------------------------------------------------*
TYPES: BEGIN OF ty_payroll_data,
         pernr       TYPE pa0001-pernr,      "Personnel Number
         ins_number  TYPE char20,             "شماره بیمه
         national_id TYPE char10,             "کد ملی
         first_name  TYPE char30,             "نام
         last_name   TYPE char40,             "نام خانوادگی
         father_name TYPE char30,             "نام پدر
         birth_date  TYPE datum,              "تاریخ تولد
         work_days   TYPE int4,               "روزهای کارکرد
         base_salary TYPE pc207-betrg,       "حقوق مبنا
         overtime    TYPE pc207-betrg,       "اضافه کار
         benefits    TYPE pc207-betrg,       "مزایای مشمول
         total       TYPE pc207-betrg,       "جمع مزایا
         start_date  TYPE datum,              "تاریخ شروع کار
         end_date    TYPE datum,              "تاریخ پایان کار
       END OF ty_payroll_data.

TYPES: BEGIN OF ty_sso_output,
         ins_number  TYPE char20,             "شماره بیمه
         national_id TYPE char10,             "کد ملی
         first_name  TYPE char30,             "نام
         last_name   TYPE char40,             "نام خانوادگی
         father_name TYPE char30,             "نام پدر
         birth_date  TYPE char8,              "تاریخ تولد (شمسی)
         work_days   TYPE char3,              "روزهای کارکرد
         base_salary TYPE char15,             "حقوق مبنا
         overtime    TYPE char15,             "اضافه کار
         benefits    TYPE char15,             "مزایای مشمول
         total       TYPE char15,             "جمع مزایا
         job_start   TYPE char8,              "تاریخ شروع کار (شمسی)
         job_end     TYPE char8,              "تاریخ پایان کار (شمسی)
       END OF ty_sso_output.

*----------------------------------------------------------------------*
* Data Declarations
*----------------------------------------------------------------------*
DATA: gt_payroll_data TYPE TABLE OF ty_payroll_data,
      gs_payroll_data TYPE ty_payroll_data,
      gt_sso_output   TYPE TABLE OF ty_sso_output,
      gs_sso_output   TYPE ty_sso_output,
      gv_file_path    TYPE string,
      gv_file_name    TYPE string.

*----------------------------------------------------------------------*
* Selection Screen
*----------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
PARAMETERS: p_pernr TYPE pa0001-pernr OBLIGATORY,  "Personnel Number Range
            p_begda TYPE datum OBLIGATORY,          "Start Date
            p_endda TYPE datum OBLIGATORY.          "End Date
SELECTION-SCREEN END OF BLOCK b1.

SELECTION-SCREEN BEGIN OF BLOCK b2 WITH FRAME TITLE TEXT-002.
PARAMETERS: p_year  TYPE numc4 OBLIGATORY,         "سال
            p_month TYPE numc2 OBLIGATORY.         "ماه
SELECTION-SCREEN END OF BLOCK b2.

SELECTION-SCREEN BEGIN OF BLOCK b3 WITH FRAME TITLE TEXT-003.
PARAMETERS: p_output TYPE char1 DEFAULT 'J',       "J=JSON, D=DBF
            p_file   TYPE string.                  "Output File Path
SELECTION-SCREEN END OF BLOCK b3.

*----------------------------------------------------------------------*
* Initialization
*----------------------------------------------------------------------*
INITIALIZATION.
  p_begda = sy-datum.
  p_endda = sy-datum.
  p_year  = sy-datum(4).
  p_month = sy-datum+4(2).

*----------------------------------------------------------------------*
* Start of Selection
*----------------------------------------------------------------------*
START-OF-SELECTION.

  PERFORM extract_payroll_data.
  PERFORM transform_to_sso_format.
  PERFORM generate_output_file.

*----------------------------------------------------------------------*
* End of Selection
*----------------------------------------------------------------------*
END-OF-SELECTION.

  WRITE: / 'استخراج اطلاعات با موفقیت انجام شد'.
  WRITE: / 'تعداد رکوردها:', lines( gt_sso_output ).

*&---------------------------------------------------------------------*
*& Form extract_payroll_data
*&---------------------------------------------------------------------*
*& استخراج اطلاعات حقوق و دستمزد از SAP HCM
*&---------------------------------------------------------------------*
FORM extract_payroll_data.

  DATA: lt_pa0000 TYPE TABLE OF pa0000,  "Personnel Actions
        lt_pa0001 TYPE TABLE OF pa0001,  "Organizational Assignment
        lt_pa0002 TYPE TABLE OF pa0002,  "Personal Data
        lt_pa0041 TYPE TABLE OF pa0041,  "Date Specifications
        lt_pa0185 TYPE TABLE OF pa0185,  "Insurance Data (Iran)
        lt_rgdir  TYPE TABLE OF pc261,   "Payroll Directory
        ls_pa0000 TYPE pa0000,
        ls_pa0001 TYPE pa0001,
        ls_pa0002 TYPE pa0002,
        ls_pa0041 TYPE pa0041,
        ls_pa0185 TYPE pa0185,
        ls_rgdir  TYPE pc261.

  " Extract PA0000 - Personnel Actions
  SELECT * FROM pa0000
    INTO TABLE lt_pa0000
    WHERE pernr = p_pernr
      AND begda <= p_endda
      AND endda >= p_begda.

  " Extract PA0001 - Organizational Assignment
  SELECT * FROM pa0001
    INTO TABLE lt_pa0001
    WHERE pernr = p_pernr
      AND begda <= p_endda
      AND endda >= p_begda.

  " Extract PA0002 - Personal Data
  SELECT * FROM pa0002
    INTO TABLE lt_pa0002
    WHERE pernr = p_pernr
      AND begda <= p_endda
      AND endda >= p_begda.

  " Extract PA0041 - Date Specifications (Birth Date)
  SELECT * FROM pa0041
    INTO TABLE lt_pa0041
    WHERE pernr = p_pernr
      AND begda <= p_endda
      AND endda >= p_begda.

  " Extract PA0185 - Insurance Data (Custom infotype for Iran)
  " Note: This may need to be adjusted based on your SAP customization
  SELECT * FROM pa0185
    INTO TABLE lt_pa0185
    WHERE pernr = p_pernr
      AND begda <= p_endda
      AND endda >= p_begda.

  " Extract Payroll Results using HR_PAYROLL_RESULTS_GET
  DATA: lt_payroll_result TYPE STANDARD TABLE OF pc207,
        ls_payroll_result TYPE pc207.

  CALL FUNCTION 'PYXX_READ_PAYROLL_RESULT'
    EXPORTING
      employeenumber          = p_pernr
      sequencenumber          = 1
    TABLES
      payroll_result          = lt_payroll_result
    EXCEPTIONS
      no_record_found         = 1
      wrong_employeenumber    = 2
      wrong_sequencenumber    = 3
      OTHERS                  = 4.

  IF sy-subrc <> 0.
    WRITE: / 'خطا در استخراج اطلاعات حقوق برای پرسنل:', p_pernr.
    RETURN.
  ENDIF.

  " Process and combine data
  LOOP AT lt_pa0002 INTO ls_pa0002.
    CLEAR gs_payroll_data.

    gs_payroll_data-pernr = ls_pa0002-pernr.
    gs_payroll_data-first_name = ls_pa0002-vorna.   "First Name
    gs_payroll_data-last_name = ls_pa0002-nachn.    "Last Name
    gs_payroll_data-father_name = ls_pa0002-fanam.  "Father Name (Custom field)

    " Get Birth Date from PA0041
    READ TABLE lt_pa0041 INTO ls_pa0041
      WITH KEY pernr = ls_pa0002-pernr.
    IF sy-subrc = 0.
      gs_payroll_data-birth_date = ls_pa0041-dar01.
    ENDIF.

    " Get National ID from PA0002 or custom field
    gs_payroll_data-national_id = ls_pa0002-perid.  "National ID

    " Get Insurance Number from PA0185 (Custom)
    READ TABLE lt_pa0185 INTO ls_pa0185
      WITH KEY pernr = ls_pa0002-pernr.
    IF sy-subrc = 0.
      gs_payroll_data-ins_number = ls_pa0185-insno. "Insurance Number
    ENDIF.

    " Calculate payroll data from results
    PERFORM calculate_payroll_amounts
      USING lt_payroll_result
      CHANGING gs_payroll_data.

    " Calculate working days
    PERFORM calculate_working_days
      USING p_begda p_endda
      CHANGING gs_payroll_data-work_days.

    " Set start and end dates
    gs_payroll_data-start_date = p_begda.
    gs_payroll_data-end_date = p_endda.

    APPEND gs_payroll_data TO gt_payroll_data.
  ENDLOOP.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form calculate_payroll_amounts
*&---------------------------------------------------------------------*
*& محاسبه مبالغ حقوق و دستمزد از نتایج پیرول
*&---------------------------------------------------------------------*
FORM calculate_payroll_amounts
  USING    it_payroll_result TYPE STANDARD TABLE
  CHANGING cs_payroll_data   TYPE ty_payroll_data.

  DATA: ls_result TYPE pc207,
        lv_amount TYPE pc207-betrg.

  " Initialize amounts
  cs_payroll_data-base_salary = 0.
  cs_payroll_data-overtime = 0.
  cs_payroll_data-benefits = 0.
  cs_payroll_data-total = 0.

  " Loop through payroll results and sum by wage type
  LOOP AT it_payroll_result INTO ls_result.

    CASE ls_result-lgart.
      WHEN '/101'.  " Base Salary (حقوق پایه)
        cs_payroll_data-base_salary = cs_payroll_data-base_salary + ls_result-betrg.

      WHEN '/102'.  " Overtime (اضافه کار)
        cs_payroll_data-overtime = cs_payroll_data-overtime + ls_result-betrg.

      WHEN '/103' OR '/104' OR '/105'.  " Benefits (مزایا)
        cs_payroll_data-benefits = cs_payroll_data-benefits + ls_result-betrg.

    ENDCASE.

  ENDLOOP.

  " Calculate total
  cs_payroll_data-total = cs_payroll_data-base_salary +
                          cs_payroll_data-overtime +
                          cs_payroll_data-benefits.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form calculate_working_days
*&---------------------------------------------------------------------*
*& محاسبه تعداد روزهای کارکرد
*&---------------------------------------------------------------------*
FORM calculate_working_days
  USING    iv_start_date TYPE datum
           iv_end_date   TYPE datum
  CHANGING cv_work_days  TYPE int4.

  DATA: lv_days TYPE int4.

  " Simple calculation - can be enhanced with holiday calendar
  lv_days = iv_end_date - iv_start_date + 1.

  " Exclude weekends (Friday in Iran)
  " This is a simplified calculation - should use HR calendar
  cv_work_days = lv_days - ( lv_days / 7 ).

ENDFORM.

*&---------------------------------------------------------------------*
*& Form transform_to_sso_format
*&---------------------------------------------------------------------*
*& تبدیل داده‌ها به فرمت تامین اجتماعی
*&---------------------------------------------------------------------*
FORM transform_to_sso_format.

  DATA: lv_jalali_date TYPE char8.

  LOOP AT gt_payroll_data INTO gs_payroll_data.
    CLEAR gs_sso_output.

    " Copy basic fields
    gs_sso_output-ins_number  = gs_payroll_data-ins_number.
    gs_sso_output-national_id = gs_payroll_data-national_id.
    gs_sso_output-first_name  = gs_payroll_data-first_name.
    gs_sso_output-last_name   = gs_payroll_data-last_name.
    gs_sso_output-father_name = gs_payroll_data-father_name.

    " Convert dates to Jalali (Persian calendar)
    PERFORM convert_to_jalali
      USING gs_payroll_data-birth_date
      CHANGING gs_sso_output-birth_date.

    PERFORM convert_to_jalali
      USING gs_payroll_data-start_date
      CHANGING gs_sso_output-job_start.

    PERFORM convert_to_jalali
      USING gs_payroll_data-end_date
      CHANGING gs_sso_output-job_end.

    " Convert numeric fields to character
    gs_sso_output-work_days   = gs_payroll_data-work_days.
    gs_sso_output-base_salary = gs_payroll_data-base_salary.
    gs_sso_output-overtime    = gs_payroll_data-overtime.
    gs_sso_output-benefits    = gs_payroll_data-benefits.
    gs_sso_output-total       = gs_payroll_data-total.

    APPEND gs_sso_output TO gt_sso_output.
  ENDLOOP.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form convert_to_jalali
*&---------------------------------------------------------------------*
*& تبدیل تاریخ میلادی به شمسی
*&---------------------------------------------------------------------*
FORM convert_to_jalali
  USING    iv_gregorian_date TYPE datum
  CHANGING cv_jalali_date    TYPE char8.

  " This is a placeholder - implement actual Jalali conversion
  " You may use a custom function module or RFC to convert dates
  " Example: CALL FUNCTION 'Z_GREGORIAN_TO_JALALI'

  DATA: lv_year  TYPE numc4,
        lv_month TYPE numc2,
        lv_day   TYPE numc2.

  " Placeholder - replace with actual conversion
  lv_year  = iv_gregorian_date(4).
  lv_month = iv_gregorian_date+4(2).
  lv_day   = iv_gregorian_date+6(2).

  " Simple approximation (NOT ACCURATE - replace with proper conversion)
  lv_year = lv_year - 621.

  CONCATENATE lv_year lv_month lv_day INTO cv_jalali_date.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form generate_output_file
*&---------------------------------------------------------------------*
*& تولید فایل خروجی
*&---------------------------------------------------------------------*
FORM generate_output_file.

  DATA: lv_json_output TYPE string,
        lt_json_lines  TYPE TABLE OF string,
        lv_filename    TYPE string.

  CASE p_output.
    WHEN 'J'.  " JSON Output
      PERFORM generate_json_output
        CHANGING lv_json_output.

      " Download JSON file
      IF p_file IS INITIAL.
        CONCATENATE 'SSO_' p_year '_' p_month '.json' INTO lv_filename.
      ELSE.
        lv_filename = p_file.
      ENDIF.

      CALL FUNCTION 'GUI_DOWNLOAD'
        EXPORTING
          filename = lv_filename
          filetype = 'ASC'
        TABLES
          data_tab = lt_json_lines
        EXCEPTIONS
          OTHERS   = 1.

      IF sy-subrc = 0.
        WRITE: / 'فایل JSON با موفقیت ایجاد شد:', lv_filename.
      ENDIF.

    WHEN 'D'.  " DBF Output
      " Note: DBF generation should be done outside ABAP
      " Export data in format suitable for external DBF generator
      WRITE: / 'خروجی DBF باید از طریق ابزار خارجی تولید شود'.
      WRITE: / 'لطفاً ابتدا خروجی JSON را دانلود کنید'.

  ENDCASE.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form generate_json_output
*&---------------------------------------------------------------------*
*& تولید خروجی JSON
*&---------------------------------------------------------------------*
FORM generate_json_output
  CHANGING cv_json_output TYPE string.

  DATA: lo_json TYPE REF TO cl_trex_json_serializer,
        lv_json TYPE string.

  " Simple JSON generation - can be enhanced
  CONCATENATE '{'
              '"payroll_data": ['
              INTO cv_json_output.

  LOOP AT gt_sso_output INTO gs_sso_output.
    CONCATENATE cv_json_output
                '{'
                '"ins_number":"' gs_sso_output-ins_number '",'
                '"national_id":"' gs_sso_output-national_id '",'
                '"first_name":"' gs_sso_output-first_name '",'
                '"last_name":"' gs_sso_output-last_name '",'
                '"father_name":"' gs_sso_output-father_name '",'
                '"birth_date":"' gs_sso_output-birth_date '",'
                '"work_days":"' gs_sso_output-work_days '",'
                '"base_salary":"' gs_sso_output-base_salary '",'
                '"overtime":"' gs_sso_output-overtime '",'
                '"benefits":"' gs_sso_output-benefits '",'
                '"total":"' gs_sso_output-total '"'
                '}'
                INTO cv_json_output.

    IF sy-tabix < lines( gt_sso_output ).
      CONCATENATE cv_json_output ',' INTO cv_json_output.
    ENDIF.
  ENDLOOP.

  CONCATENATE cv_json_output ']' '}' INTO cv_json_output.

ENDFORM.

*&---------------------------------------------------------------------*
*& Text Symbols
*&---------------------------------------------------------------------*
* TEXT-001: پارامترهای پرسنل / Personnel Parameters
* TEXT-002: دوره زمانی / Time Period
* TEXT-003: خروجی / Output Settings
