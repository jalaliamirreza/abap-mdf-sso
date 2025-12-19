*&---------------------------------------------------------------------*
*& Include          ZABAP_DBF_CONVERTER
*&---------------------------------------------------------------------*
*& تبدیل مستقیم به DBF با استفاده از Python و Iran System Encoding
*& نویسنده: Best eRun Development Team
*& تاریخ: 1403
*&---------------------------------------------------------------------*

*----------------------------------------------------------------------*
* FORM generate_dbf_directly
*----------------------------------------------------------------------*
* تولید مستقیم فایل‌های DBF بدون نیاز به Excel
* استفاده از Python wrapper برای تبدیل با Iran System encoding
*----------------------------------------------------------------------*
FORM generate_dbf_directly.

  DATA: lv_kar_csv     TYPE string,
        lv_wor_csv     TYPE string,
        lv_output_dir  TYPE string,
        lv_kar_dbf     TYPE string,
        lv_wor_dbf     TYPE string,
        lv_timestamp   TYPE string,
        lv_command     TYPE string,
        lv_workshop    TYPE string,
        lv_count       TYPE i.

  DATA: lt_kar_data TYPE TABLE OF zpy_insurance_dskk_struc,
        lt_wor_data TYPE TABLE OF zpy_insurance_dskw_struc.

  " بررسی تعداد رکوردهای انتخاب شده
  CLEAR lv_count.
  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    lv_count = lv_count + 1.
  ENDLOOP.

  IF lv_count = 0.
    MESSAGE e000(zhr_msg_cl). " حداقل یک رکورد باید انتخاب شود
    RETURN.
  ENDIF.

  " ایجاد timestamp برای فایل‌های موقت
  CONCATENATE sy-datum sy-uzeit INTO lv_timestamp.

  " تعریف مسیرهای فایل روی Application Server
  " توجه: این مسیر باید با SAP Basis هماهنگ شود
  CONCATENATE '/tmp/sap_dbf_' lv_timestamp INTO lv_output_dir.
  CONCATENATE lv_output_dir '_kar.csv' INTO lv_kar_csv.
  CONCATENATE lv_output_dir '_wor.csv' INTO lv_wor_csv.

  " آماده‌سازی داده‌های KAR (Header)
  PERFORM prepare_kar_data USING lv_count CHANGING lt_kar_data.

  " آماده‌سازی داده‌های WOR (Workers)
  PERFORM prepare_wor_data CHANGING lt_wor_data.

  " Export داده‌ها به CSV روی Application Server
  PERFORM export_to_csv_appserver USING lv_kar_csv lt_kar_data.
  PERFORM export_to_csv_appserver USING lv_wor_csv lt_wor_data.

  " فراخوانی Python script
  lv_workshop = id. " کد کارگاه از selection screen

  PERFORM execute_python_converter
    USING lv_kar_csv lv_wor_csv lv_output_dir lv_workshop
    CHANGING lv_kar_dbf lv_wor_dbf.

  " دانلود فایل‌های DBF به Presentation Server (PC کاربر)
  PERFORM download_dbf_files USING lv_kar_dbf lv_wor_dbf.

  " پاکسازی فایل‌های موقت
  PERFORM cleanup_temp_files USING lv_kar_csv lv_wor_csv
                                    lv_kar_dbf lv_wor_dbf.

  MESSAGE 'فایل‌های DBF با موفقیت ایجاد شدند' TYPE 'S'.

ENDFORM.

*----------------------------------------------------------------------*
* FORM prepare_kar_data
*----------------------------------------------------------------------*
FORM prepare_kar_data USING p_count TYPE i
                      CHANGING pt_kar_data TYPE STANDARD TABLE.

  DATA: ls_kar TYPE zpy_insurance_dskk_struc.

  CLEAR ls_kar.

  " محاسبه مجموع‌ها
  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    ls_kar-dsk_tdd    = ls_kar-dsk_tdd + wa01-dsw_dd.
    ls_kar-dsk_trooz  = ls_kar-dsk_trooz + wa01-dsw_rooz.
    ls_kar-dsk_tmah   = ls_kar-dsk_tmah + wa01-dsw_mah.
    ls_kar-dsk_tmaz   = ls_kar-dsk_tmaz + wa01-dsw_maz.
    ls_kar-dsk_tspouse = ls_kar-dsk_tspouse + wa01-dsw_spouse.
    ls_kar-dsk_tinc   = ls_kar-dsk_tinc + wa01-dsw_inc.
    ls_kar-dsk_tmash  = ls_kar-dsk_tmash + wa01-dsw_mash.
    ls_kar-dsk_ttotl  = ls_kar-dsk_ttotl + wa01-dsw_totl.
    ls_kar-dsk_tbime  = ls_kar-dsk_tbime + wa01-dsw_bime.
    ls_kar-dsk_tkoso  = ls_kar-dsk_tkoso + wa01-dsw_tkoso.
    ls_kar-dsk_bic    = ls_kar-dsk_bic + wa01-dsw_bic.
  ENDLOOP.

  " پر کردن فیلدهای header
  ls_kar-dsk_id     = id.           " کد کارگاه
  ls_kar-dsk_name   = p_code.       " نام کارگاه
  ls_kar-dsk_adrs   = adrs.         " آدرس
  ls_kar-dsk_yy     = wa01-dsw_yy.  " سال
  ls_kar-dsk_mm     = wa01-dsw_mm.  " ماه
  ls_kar-dsk_kind   = 0.            " نوع لیست
  ls_kar-dsk_rate   = 23.           " نرخ بیمه
  ls_kar-dsk_prate  = 0.            " نرخ اضافی
  ls_kar-dsk_listno = '1'.          " شماره لیست
  ls_kar-dsk_disk   = ''.           " تخفیف
  ls_kar-dsk_bimh   = 0.            " بیمه بیکاری
  ls_kar-dsk_num    = p_count.      " تعداد کارگران
  ls_kar-mon_pym    = zmon_pym.     " ماه پرداخت

  SELECT SINGLE farm FROM zhr_ins_workcent
    INTO ls_kar-dsk_farm
    WHERE place = p_code.

  APPEND ls_kar TO pt_kar_data.

ENDFORM.

*----------------------------------------------------------------------*
* FORM prepare_wor_data
*----------------------------------------------------------------------*
FORM prepare_wor_data CHANGING pt_wor_data TYPE STANDARD TABLE.

  DATA: ls_wor TYPE zpy_insurance_dskw_struc.

  LOOP AT it01 INTO wa01 WHERE checkbox = 'X'.
    MOVE-CORRESPONDING wa01 TO ls_wor.
    APPEND ls_wor TO pt_wor_data.
  ENDLOOP.

ENDFORM.

*----------------------------------------------------------------------*
* FORM export_to_csv_appserver
*----------------------------------------------------------------------*
FORM export_to_csv_appserver USING p_filename TYPE string
                                   p_data     TYPE STANDARD TABLE.

  DATA: lv_line   TYPE string,
        lv_output TYPE string.

  FIELD-SYMBOLS: <fs_data> TYPE any,
                 <fs_field> TYPE any.

  DATA: lt_components TYPE abap_component_tab,
        ls_component  LIKE LINE OF lt_components,
        lo_structdescr TYPE REF TO cl_abap_structdescr.

  " باز کردن فایل برای نوشتن
  OPEN DATASET p_filename FOR OUTPUT IN TEXT MODE ENCODING UTF-8.

  IF sy-subrc <> 0.
    MESSAGE 'خطا در ایجاد فایل موقت' TYPE 'E'.
    RETURN.
  ENDIF.

  " نوشتن هدر CSV
  LOOP AT p_data ASSIGNING <fs_data>.
    lo_structdescr ?= cl_abap_typedescr=>describe_by_data( <fs_data> ).
    lt_components = lo_structdescr->get_components( ).

    " ساخت خط هدر
    CLEAR lv_line.
    LOOP AT lt_components INTO ls_component.
      IF sy-tabix > 1.
        CONCATENATE lv_line ',' INTO lv_line.
      ENDIF.
      CONCATENATE lv_line ls_component-name INTO lv_line.
    ENDLOOP.

    TRANSFER lv_line TO p_filename.
    EXIT. " فقط یک بار هدر بنویس
  ENDLOOP.

  " نوشتن داده‌ها
  LOOP AT p_data ASSIGNING <fs_data>.
    CLEAR lv_line.

    LOOP AT lt_components INTO ls_component.
      ASSIGN COMPONENT ls_component-name OF STRUCTURE <fs_data> TO <fs_field>.

      IF sy-tabix > 1.
        CONCATENATE lv_line ',' INTO lv_line.
      ENDIF.

      " تبدیل فیلد به رشته
      lv_output = <fs_field>.
      CONDENSE lv_output NO-GAPS.

      " Escape کاما و گیومه
      IF lv_output CA ','.
        CONCATENATE '"' lv_output '"' INTO lv_output.
      ENDIF.

      CONCATENATE lv_line lv_output INTO lv_line.
    ENDLOOP.

    TRANSFER lv_line TO p_filename.
  ENDLOOP.

  CLOSE DATASET p_filename.

ENDFORM.

*----------------------------------------------------------------------*
* FORM execute_python_converter
*----------------------------------------------------------------------*
FORM execute_python_converter
  USING p_kar_csv     TYPE string
        p_wor_csv     TYPE string
        p_output_dir  TYPE string
        p_workshop    TYPE string
  CHANGING p_kar_dbf  TYPE string
           p_wor_dbf  TYPE string.

  DATA: lv_command      TYPE sxpgcolist-name VALUE 'ZDBF_CONVERT',
        lv_parameters   TYPE string,
        lv_status       TYPE extcmdexex-exitcode,
        lt_exec_protocol TYPE TABLE OF btcxpm,
        ls_exec_protocol LIKE LINE OF lt_exec_protocol.

  " ساخت مسیرهای خروجی
  CONCATENATE p_output_dir '/DSKKAR00.DBF' INTO p_kar_dbf.
  CONCATENATE p_output_dir '/DSKWOR00.DBF' INTO p_wor_dbf.

  " ساخت پارامترهای command
  CONCATENATE p_kar_csv p_wor_csv p_output_dir p_workshop
    INTO lv_parameters SEPARATED BY space.

  " اجرای External Command
  CALL FUNCTION 'SXPG_COMMAND_EXECUTE'
    EXPORTING
      commandname           = lv_command
      additional_parameters = lv_parameters
    IMPORTING
      exitcode              = lv_status
    TABLES
      exec_protocol         = lt_exec_protocol
    EXCEPTIONS
      no_permission         = 1
      command_not_found     = 2
      parameters_too_long   = 3
      security_risk         = 4
      wrong_check_call_interface = 5
      program_start_error   = 6
      program_termination_error = 7
      x_error               = 8
      parameter_expected    = 9
      too_many_parameters   = 10
      illegal_command       = 11
      OTHERS                = 12.

  IF sy-subrc <> 0.
    MESSAGE 'خطا در اجرای Python converter' TYPE 'E'.
    " نمایش لاگ‌ها
    LOOP AT lt_exec_protocol INTO ls_exec_protocol.
      WRITE: / ls_exec_protocol-message.
    ENDLOOP.
    RETURN.
  ENDIF.

  IF lv_status <> 0.
    MESSAGE 'Python converter با خطا مواجه شد' TYPE 'E'.
    LOOP AT lt_exec_protocol INTO ls_exec_protocol.
      WRITE: / ls_exec_protocol-message.
    ENDLOOP.
    RETURN.
  ENDIF.

  " بررسی وجود فایل‌های خروجی
  DATA: lv_exists TYPE abap_bool.

  CALL METHOD cl_gui_frontend_services=>file_exist
    EXPORTING
      file   = p_kar_dbf
    RECEIVING
      result = lv_exists.

  IF lv_exists = abap_false.
    MESSAGE 'فایل DBF ایجاد نشد' TYPE 'E'.
    RETURN.
  ENDIF.

ENDFORM.

*----------------------------------------------------------------------*
* FORM download_dbf_files
*----------------------------------------------------------------------*
FORM download_dbf_files USING p_kar_dbf TYPE string
                              p_wor_dbf TYPE string.

  DATA: lv_path      TYPE string,
        lv_kar_local TYPE string,
        lv_wor_local TYPE string,
        lt_binary    TYPE TABLE OF x255.

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

  " ساخت مسیرهای کامل
  CONCATENATE lv_path '\DSKKAR00.DBF' INTO lv_kar_local.
  CONCATENATE lv_path '\DSKWOR00.DBF' INTO lv_wor_local.

  " دانلود KAR
  PERFORM download_binary_file USING p_kar_dbf lv_kar_local.

  " دانلود WOR
  PERFORM download_binary_file USING p_wor_dbf lv_wor_local.

  MESSAGE 'فایل‌های DBF با موفقیت دانلود شدند' TYPE 'S'.

ENDFORM.

*----------------------------------------------------------------------*
* FORM download_binary_file
*----------------------------------------------------------------------*
FORM download_binary_file USING p_source TYPE string
                                p_target TYPE string.

  DATA: lt_binary TYPE TABLE OF x255,
        lv_length TYPE i.

  " خواندن فایل از Application Server
  OPEN DATASET p_source FOR INPUT IN BINARY MODE.
  IF sy-subrc <> 0.
    MESSAGE 'خطا در خواندن فایل DBF' TYPE 'E'.
    RETURN.
  ENDIF.

  DO.
    READ DATASET p_source INTO lt_binary.
    IF sy-subrc <> 0.
      EXIT.
    ENDIF.
  ENDDO.

  CLOSE DATASET p_source.

  " نوشتن به Presentation Server
  CALL FUNCTION 'GUI_DOWNLOAD'
    EXPORTING
      filename     = p_target
      filetype     = 'BIN'
    TABLES
      data_tab     = lt_binary
    EXCEPTIONS
      OTHERS       = 1.

  IF sy-subrc <> 0.
    MESSAGE 'خطا در دانلود فایل' TYPE 'E'.
  ENDIF.

ENDFORM.

*----------------------------------------------------------------------*
* FORM cleanup_temp_files
*----------------------------------------------------------------------*
FORM cleanup_temp_files USING p_kar_csv TYPE string
                              p_wor_csv TYPE string
                              p_kar_dbf TYPE string
                              p_wor_dbf TYPE string.

  " حذف فایل‌های موقت
  DELETE DATASET p_kar_csv.
  DELETE DATASET p_wor_csv.
  DELETE DATASET p_kar_dbf.
  DELETE DATASET p_wor_dbf.

ENDFORM.
