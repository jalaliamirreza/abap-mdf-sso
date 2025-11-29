*&---------------------------------------------------------------------*
*& Include          ZHR_INS_REP_FILES_DBF
*&---------------------------------------------------------------------*
*& تولید مستقیم فایل‌های DBF با Iran System Encoding
*& بدون نیاز به کانورتر خارجی
*&---------------------------------------------------------------------*

*----------------------------------------------------------------------*
* FORM fill_dbf_direct
*----------------------------------------------------------------------*
* تولید مستقیم فایل‌های DBF از داده‌های انتخاب شده
* این روش از Python wrapper استفاده می‌کند
*----------------------------------------------------------------------*
FORM fill_dbf_direct.

  DATA: lv_kar_xls     TYPE string,
        lv_wor_xls     TYPE string,
        lv_output_dir  TYPE string,
        lv_count       TYPE i,
        lv_path        TYPE string.

  DATA: lt_wor_data TYPE TABLE OF zpy_insurance_dskw_struc_xls,
        wa_wor_data LIKE LINE OF lt_wor_data,
        lt_kar_data TYPE TABLE OF zpy_insurance_dskk_struc,
        wa_kar_data LIKE LINE OF lt_kar_data.

  " ================== بررسی تعداد رکوردهای انتخاب شده ==================
  CLEAR lv_count.
  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    lv_count = lv_count + 1.
  ENDLOOP.

  IF lv_count = 0.
    MESSAGE e000(zhr_msg_cl). " حداقل یک رکورد باید انتخاب شود
    RETURN.
  ENDIF.

  " مسیرهای فایل روی Application Server
  " استفاده از پوشه اختصاصی با دسترسی کامل (بدون نیاز به ساخت subdirectory)
  lv_output_dir = '/usr/sap/scripts/dbf_converter/tmp/'.
  CONCATENATE lv_output_dir 'DSKKAR00.XLS' INTO lv_kar_xls.
  CONCATENATE lv_output_dir 'DSKWOR00.XLS' INTO lv_wor_xls.

  " ================== آماده‌سازی داده‌ها ==================
  " KAR (Header)
  PERFORM prepare_kar_data_for_dbf USING lv_count CHANGING lt_kar_data.

  " WOR (Workers)
  PERFORM prepare_wor_data_for_dbf CHANGING lt_wor_data.

  " ================== Export به فایل‌های XLS (Tab-delimited UTF-16) ==================
  PERFORM export_to_xls_appserver USING lv_kar_xls lt_kar_data.
  PERFORM export_to_xls_appserver USING lv_wor_xls lt_wor_data.

  " ================== بررسی وجود فایل‌های XLS ==================
  DATA: lv_kar_exists TYPE abap_bool,
        lv_wor_exists TYPE abap_bool.

  OPEN DATASET lv_kar_xls FOR INPUT IN TEXT MODE.
  IF sy-subrc = 0.
    lv_kar_exists = abap_true.
    CLOSE DATASET lv_kar_xls.
  ENDIF.

  OPEN DATASET lv_wor_xls FOR INPUT IN TEXT MODE.
  IF sy-subrc = 0.
    lv_wor_exists = abap_true.
    CLOSE DATASET lv_wor_xls.
  ENDIF.

  IF lv_kar_exists = abap_false OR lv_wor_exists = abap_false.
    WRITE: / 'خطا: فایل‌های XLS ساخته نشدند!'.
    IF lv_kar_exists = abap_false.
      WRITE: / 'Missing:', lv_kar_xls.
    ENDIF.
    IF lv_wor_exists = abap_false.
      WRITE: / 'Missing:', lv_wor_xls.
    ENDIF.
    MESSAGE 'خطا در ساخت فایل‌های XLS موقت' TYPE 'E'.
    RETURN.
  ENDIF.

  " ================== فراخوانی Python Converter ==================
  PERFORM execute_python_dbf_converter
    USING lv_kar_xls lv_wor_xls lv_output_dir.

  " ================== دانلود فایل‌های DBF به PC کاربر ==================
  PERFORM download_dbf_to_pc USING lv_output_dir.

  " ================== پاکسازی فایل‌های موقت ==================
  PERFORM cleanup_temp_dbf_files USING lv_output_dir.

  MESSAGE 'فایل‌های DBF با موفقیت ایجاد و دانلود شدند!' TYPE 'S'.

ENDFORM.

*----------------------------------------------------------------------*
* FORM prepare_kar_data_for_dbf
*----------------------------------------------------------------------*
FORM prepare_kar_data_for_dbf USING p_count TYPE i
                               CHANGING pt_kar_data TYPE STANDARD TABLE.

  DATA: ls_kar TYPE zpy_insurance_dskk_struc.

  CLEAR: ls_kar, pt_kar_data.

  " محاسبه مجموع‌ها
  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    ls_kar-dsk_tdd     = ls_kar-dsk_tdd + wa01-dsw_dd.
    ls_kar-dsk_trooz   = ls_kar-dsk_trooz + wa01-dsw_rooz.
    ls_kar-dsk_tmah    = ls_kar-dsk_tmah + wa01-dsw_mah.
    ls_kar-dsk_tmaz    = ls_kar-dsk_tmaz + wa01-dsw_maz.
    ls_kar-dsk_tspouse = ls_kar-dsk_tspouse + wa01-dsw_spouse.
    ls_kar-dsk_tinc    = ls_kar-dsk_tinc + wa01-dsw_inc.
    ls_kar-dsk_tmash   = ls_kar-dsk_tmash + wa01-dsw_mash.
    ls_kar-dsk_ttotl   = ls_kar-dsk_ttotl + wa01-dsw_totl.
    ls_kar-dsk_tbime   = ls_kar-dsk_tbime + wa01-dsw_bime.
    ls_kar-dsk_tkoso   = ls_kar-dsk_tkoso + wa01-dsw_tkoso.
    ls_kar-dsk_bic     = ls_kar-dsk_bic + wa01-dsw_bic.
  ENDLOOP.

  " پر کردن فیلدهای header با فرمول Excel برای zero-padding
  PERFORM format_with_excel_formula
    USING id 10
    CHANGING ls_kar-dsk_id.

  ls_kar-dsk_name = p_code.
  ls_kar-dsk_adrs = adrs.

  PERFORM format_with_excel_formula
    USING wa01-dsw_yy 2
    CHANGING ls_kar-dsk_yy.

  PERFORM format_with_excel_formula
    USING wa01-dsw_mm 2
    CHANGING ls_kar-dsk_mm.

  ls_kar-dsk_kind = 0.
  ls_kar-dsk_rate = 23.
  ls_kar-dsk_prate = 0.

  " فرمول برای شماره لیست
  ls_kar-dsk_listno = '=REPT(0,11)&' && '"1"'.

  ls_kar-dsk_disk = ''.
  ls_kar-dsk_bimh = 0.
  ls_kar-dsk_num = p_count.
  ls_kar-mon_pym = zmon_pym.

  SELECT SINGLE farm FROM zhr_ins_workcent
    INTO ls_kar-dsk_farm
    WHERE place = p_code.

  APPEND ls_kar TO pt_kar_data.

ENDFORM.

*----------------------------------------------------------------------*
* FORM prepare_wor_data_for_dbf
*----------------------------------------------------------------------*
FORM prepare_wor_data_for_dbf CHANGING pt_wor_data TYPE STANDARD TABLE.

  DATA: ls_wor TYPE zpy_insurance_dskw_struc_xls.

  CLEAR pt_wor_data.

  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    CLEAR ls_wor.

    " فیلدهایی که نیاز به فرمول Excel دارند
    IF wa01-dsw_id IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_id 10
        CHANGING ls_wor-dsw_id.
    ENDIF.

    PERFORM format_with_excel_formula
      USING wa01-dsw_yy 2
      CHANGING ls_wor-dsw_yy.

    PERFORM format_with_excel_formula
      USING wa01-dsw_mm 2
      CHANGING ls_wor-dsw_mm.

    " شماره لیست
    ls_wor-dsw_listno = '=REPT(0,11)&' && '"1"'.

    " کد بیمه تامین اجتماعی
    IF wa01-dsw_id1 IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_id1 10
        CHANGING ls_wor-dsw_id1.
    ENDIF.

    " فیلدهای متنی بدون تغییر
    ls_wor-dsw_fname = wa01-dsw_fname.
    ls_wor-dsw_lname = wa01-dsw_lname.
    ls_wor-dsw_dname = wa01-dsw_dname.

    " شماره شناسنامه
    IF wa01-dsw_idno IS NOT INITIAL.
      IF strlen( wa01-dsw_idno ) = 10.
        PERFORM format_with_excel_formula
          USING wa01-dsw_idno 10
          CHANGING ls_wor-dsw_idno.
      ELSE.
        ls_wor-dsw_idno = wa01-dsw_idno.
      ENDIF.
    ENDIF.

    ls_wor-dsw_idplc = wa01-dsw_idplc.

    " تاریخ‌ها با فرمول
    IF wa01-dsw_idate IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_idate 8
        CHANGING ls_wor-dsw_idate.
    ENDIF.

    IF wa01-dsw_bdate IS NOT INITIAL.
      ls_wor-dsw_bdate = wa01-dsw_bdate.  " بدون فرمول
    ENDIF.

    ls_wor-dsw_sex = wa01-dsw_sex.
    ls_wor-dsw_nat = wa01-dsw_nat.
    ls_wor-dsw_ocp = wa01-dsw_ocp.

    IF wa01-dsw_sdate IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_sdate 8
        CHANGING ls_wor-dsw_sdate.
    ENDIF.

    IF wa01-dsw_edate IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_edate 8
        CHANGING ls_wor-dsw_edate.
    ENDIF.

    " فیلدهای عددی
    ls_wor-dsw_dd = wa01-dsw_dd.
    ls_wor-dsw_rooz = wa01-dsw_rooz.
    ls_wor-dsw_mah = wa01-dsw_mah.
    ls_wor-dsw_maz = wa01-dsw_maz.
    ls_wor-dsw_spouse = wa01-dsw_spouse.
    ls_wor-dsw_inc = wa01-dsw_inc.
    ls_wor-dsw_mash = wa01-dsw_mash.
    ls_wor-dsw_totl = wa01-dsw_totl.
    ls_wor-dsw_bime = wa01-dsw_bime.

    " PRATE
    ls_wor-dsw_prate = '=REPT(0,2)'.

    " کد شغل
    IF wa01-dsw_job IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-dsw_job 6
        CHANGING ls_wor-dsw_job.
    ENDIF.

    " کد ملی
    IF wa01-per_natcod IS NOT INITIAL.
      PERFORM format_with_excel_formula
        USING wa01-per_natcod 10
        CHANGING ls_wor-per_natcod.
    ENDIF.

    APPEND ls_wor TO pt_wor_data.
  ENDLOOP.

ENDFORM.

*----------------------------------------------------------------------*
* FORM format_with_excel_formula
*----------------------------------------------------------------------*
* ایجاد فرمول Excel برای zero-padding
* مثال: =REPT(0,10-LEN("0853900011"))&"0853900011"
*----------------------------------------------------------------------*
FORM format_with_excel_formula USING p_value TYPE any
                                     p_width TYPE i
                               CHANGING p_output TYPE any.

  DATA: lv_value TYPE string,
        lv_formula TYPE string,
        lv_width_str TYPE string.

  lv_value = p_value.
  CONDENSE lv_value NO-GAPS.

  " تبدیل width به string
  lv_width_str = p_width.
  CONDENSE lv_width_str NO-GAPS.

  " ساخت فرمول Excel
  CONCATENATE '=REPT(0,' lv_width_str '-LEN("' lv_value '"))&"' lv_value '"'
    INTO lv_formula.

  p_output = lv_formula.

ENDFORM.

*----------------------------------------------------------------------*
* FORM export_to_xls_appserver
*----------------------------------------------------------------------*
* Export داده‌ها به فایل XLS (Tab-delimited UTF-16)
* همان فرمتی که SAP الان تولید می‌کند
*----------------------------------------------------------------------*
FORM export_to_xls_appserver USING p_filename TYPE string
                                   p_data TYPE STANDARD TABLE.

  DATA: lv_line TYPE string,
        lv_output TYPE string.

  FIELD-SYMBOLS: <fs_data> TYPE any,
                 <fs_field> TYPE any.

  DATA: lt_components TYPE abap_component_tab,
        ls_component LIKE LINE OF lt_components,
        lo_structdescr TYPE REF TO cl_abap_structdescr.

  " باز کردن فایل با encoding UTF-8 (SAP standard)
  " توجه: دایرکتوری /usr/sap/scripts/dbf_converter/tmp/ باید از قبل وجود داشته باشد
  " Note: برای UTF-16 باید از binary mode و conversion استفاده شود
  OPEN DATASET p_filename FOR OUTPUT IN TEXT MODE ENCODING UTF-8.

  IF sy-subrc <> 0.
    MESSAGE 'خطا در ایجاد فایل XLS موقت' TYPE 'E'.
    RETURN.
  ENDIF.

  " نوشتن هدر
  LOOP AT p_data ASSIGNING <fs_data>.
    lo_structdescr ?= cl_abap_typedescr=>describe_by_data( <fs_data> ).
    lt_components = lo_structdescr->get_components( ).

    CLEAR lv_line.
    LOOP AT lt_components INTO ls_component.
      IF sy-tabix > 1.
        CONCATENATE lv_line cl_abap_char_utilities=>horizontal_tab INTO lv_line.
      ENDIF.
      CONCATENATE lv_line ls_component-name INTO lv_line.
    ENDLOOP.

    TRANSFER lv_line TO p_filename.
    EXIT.
  ENDLOOP.

  " نوشتن داده‌ها
  LOOP AT p_data ASSIGNING <fs_data>.
    CLEAR lv_line.

    LOOP AT lt_components INTO ls_component.
      ASSIGN COMPONENT ls_component-name OF STRUCTURE <fs_data> TO <fs_field>.

      IF sy-tabix > 1.
        CONCATENATE lv_line cl_abap_char_utilities=>horizontal_tab INTO lv_line.
      ENDIF.

      lv_output = <fs_field>.
      " حذف فضاهای اضافی از انتها (اما نه ابتدا - مهم برای متن فارسی)
      IF lv_output IS NOT INITIAL.
        " فقط از سمت راست trim کن
        SHIFT lv_output RIGHT DELETING TRAILING space.
        SHIFT lv_output LEFT DELETING LEADING space.
      ENDIF.

      CONCATENATE lv_line lv_output INTO lv_line.
    ENDLOOP.

    TRANSFER lv_line TO p_filename.
  ENDLOOP.

  CLOSE DATASET p_filename.

ENDFORM.

*----------------------------------------------------------------------*
* FORM execute_python_dbf_converter
*----------------------------------------------------------------------*
FORM execute_python_dbf_converter
  USING p_kar_xls TYPE string
        p_wor_xls TYPE string
        p_output_dir TYPE string.

  DATA: lv_command      TYPE sxpgcolist-name VALUE 'ZDBF_XLS_CONVERT',
        lv_parameters   TYPE btcxpgpar,
        lv_status       TYPE extcmdexex-exitcode,
        lt_exec_protocol TYPE TABLE OF btcxpm,
        ls_exec_protocol LIKE LINE OF lt_exec_protocol.

  " ساخت پارامترها
  CONCATENATE p_kar_xls p_wor_xls p_output_dir
    INTO lv_parameters SEPARATED BY space.

  " اجرای External Command
  CALL FUNCTION 'SXPG_COMMAND_EXECUTE'
    EXPORTING
      commandname                = lv_command
      additional_parameters      = lv_parameters
    IMPORTING
      exitcode                   = lv_status
    TABLES
      exec_protocol              = lt_exec_protocol
    EXCEPTIONS
      no_permission              = 1
      command_not_found          = 2
      parameters_too_long        = 3
      security_risk              = 4
      wrong_check_call_interface = 5
      program_start_error        = 6
      program_termination_error  = 7
      x_error                    = 8
      parameter_expected         = 9
      too_many_parameters        = 10
      illegal_command            = 11
      OTHERS                     = 12.

  IF sy-subrc <> 0 OR lv_status <> 0.
    DATA: lv_msg TYPE string,
          lv_subrc_str TYPE string,
          lv_status_str TYPE string.
    " تبدیل اعداد به string
    lv_subrc_str = sy-subrc.
    lv_status_str = lv_status.
    CONDENSE lv_subrc_str NO-GAPS.
    CONDENSE lv_status_str NO-GAPS.

    " نمایش جزئیات خطا
    CONCATENATE 'خطا در تبدیل به DBF - sy-subrc:' lv_subrc_str 'exitcode:' lv_status_str
      INTO lv_msg SEPARATED BY space.

    " نمایش لاگ‌ها
    WRITE: / lv_msg.
    LOOP AT lt_exec_protocol INTO ls_exec_protocol.
      WRITE: / ls_exec_protocol-message.
    ENDLOOP.

    " نمایش پارامترها برای debug
    WRITE: / 'Parameters:', lv_parameters.
    WRITE: / 'KAR XLS:', p_kar_xls.
    WRITE: / 'WOR XLS:', p_wor_xls.
    WRITE: / 'Output Dir:', p_output_dir.

    MESSAGE lv_msg TYPE 'E'.
    RETURN.
  ENDIF.

ENDFORM.

*----------------------------------------------------------------------*
* FORM download_dbf_to_pc
*----------------------------------------------------------------------*
FORM download_dbf_to_pc USING p_output_dir TYPE string.

  DATA: lv_path      TYPE string,
        lv_kar_app   TYPE string,
        lv_wor_app   TYPE string,
        lv_kar_pc    TYPE string,
        lv_wor_pc    TYPE string.

  " ساخت مسیرهای فایل روی App Server
  CONCATENATE p_output_dir 'DSKKAR00.DBF' INTO lv_kar_app.
  CONCATENATE p_output_dir 'DSKWOR00.DBF' INTO lv_wor_app.

  " انتخاب مسیر توسط کاربر
  CALL METHOD cl_gui_frontend_services=>directory_browse
    EXPORTING
      window_title    = 'انتخاب مسیر ذخیره فایل‌های DBF'
    CHANGING
      selected_folder = lv_path
    EXCEPTIONS
      OTHERS          = 1.

  IF sy-subrc <> 0 OR lv_path IS INITIAL.
    MESSAGE 'انتخاب مسیر لغو شد' TYPE 'I'.
    RETURN.
  ENDIF.

  " ساخت مسیرهای کامل روی PC
  CONCATENATE lv_path '\DSKKAR00.DBF' INTO lv_kar_pc.
  CONCATENATE lv_path '\DSKWOR00.DBF' INTO lv_wor_pc.

  " دانلود KAR
  PERFORM download_dbf_file USING lv_kar_app lv_kar_pc.

  " دانلود WOR
  PERFORM download_dbf_file USING lv_wor_app lv_wor_pc.

ENDFORM.

*----------------------------------------------------------------------*
* FORM download_dbf_file
*----------------------------------------------------------------------*
FORM download_dbf_file USING p_source TYPE string
                             p_target TYPE string.

  DATA: lt_binary TYPE STANDARD TABLE OF x255,
        lv_line   TYPE x255,
        lv_length TYPE i.

  " خواندن از Application Server
  OPEN DATASET p_source FOR INPUT IN BINARY MODE.
  IF sy-subrc <> 0.
    MESSAGE 'خطا در خواندن فایل DBF از سرور' TYPE 'E'.
    RETURN.
  ENDIF.

  DO.
    READ DATASET p_source INTO lv_line.
    IF sy-subrc <> 0.
      EXIT.
    ENDIF.
    APPEND lv_line TO lt_binary.
  ENDDO.

  CLOSE DATASET p_source.

  " نوشتن به Presentation Server
  CALL FUNCTION 'GUI_DOWNLOAD'
    EXPORTING
      filename = p_target
      filetype = 'BIN'
    TABLES
      data_tab = lt_binary
    EXCEPTIONS
      OTHERS   = 1.

  IF sy-subrc <> 0.
    MESSAGE 'خطا در دانلود فایل DBF' TYPE 'E'.
  ENDIF.

ENDFORM.

*----------------------------------------------------------------------*
* FORM cleanup_temp_dbf_files
*----------------------------------------------------------------------*
FORM cleanup_temp_dbf_files USING p_output_dir TYPE string.

  DATA: lv_file TYPE string.

  " حذف فایل‌های موقت
  CONCATENATE p_output_dir 'DSKKAR00.XLS' INTO lv_file.
  DELETE DATASET lv_file.

  CONCATENATE p_output_dir 'DSKWOR00.XLS' INTO lv_file.
  DELETE DATASET lv_file.

  CONCATENATE p_output_dir 'DSKKAR00.DBF' INTO lv_file.
  DELETE DATASET lv_file.

  CONCATENATE p_output_dir 'DSKWOR00.DBF' INTO lv_file.
  DELETE DATASET lv_file.

  " حذف دایرکتوری (اگر خالی باشد)
  " توجه: این قسمت optional است
*  CALL 'SYSTEM' ID 'COMMAND' FIELD 'rmdir'
*                ID 'PARAMETERS' FIELD p_output_dir.

ENDFORM.
