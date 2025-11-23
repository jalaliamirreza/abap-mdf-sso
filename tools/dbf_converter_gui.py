#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF Converter GUI
رابط گرافیکی تبدیل‌کننده DBF

Persian-friendly GUI for converting between CSV and DBF formats
for Iranian Social Security Organization files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
from pathlib import Path
import subprocess
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class DBFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("تبدیل‌کننده DBF - SSO 2024 (ساختار جدید)")
        self.root.geometry("800x600")

        # Configure RTL support for Persian
        self.root.option_add('*Font', 'Tahoma 10')

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_csv_to_dbf_tab()
        self.create_dbf_to_csv_tab()

    def create_csv_to_dbf_tab(self):
        """Create CSV → DBF conversion tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='CSV → DBF')

        # Title
        title = tk.Label(frame, text='تبدیل CSV به DBF', font=('Tahoma', 14, 'bold'))
        title.pack(pady=10)

        # Info label
        info = tk.Label(frame, text='✅ ساختار جدید SSO 2024 (25 فیلد header، 29 فیلد workers)',
                       font=('Tahoma', 9), fg='green')
        info.pack()

        # Input files frame
        input_frame = ttk.LabelFrame(frame, text='فایل‌های ورودی (CSV)', padding=10)
        input_frame.pack(fill='x', padx=20, pady=10)

        # Header CSV
        ttk.Label(input_frame, text='فایل Header (dskkar00):').grid(row=0, column=0, sticky='w', pady=5)
        self.header_csv_entry = ttk.Entry(input_frame, width=50)
        self.header_csv_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text='انتخاب...', command=self.browse_header_csv).grid(row=0, column=2)

        # Workers CSV
        ttk.Label(input_frame, text='فایل Workers (dskwor00):').grid(row=1, column=0, sticky='w', pady=5)
        self.workers_csv_entry = ttk.Entry(input_frame, width=50)
        self.workers_csv_entry.grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text='انتخاب...', command=self.browse_workers_csv).grid(row=1, column=2)

        # Parameters frame
        params_frame = ttk.LabelFrame(frame, text='پارامترها', padding=10)
        params_frame.pack(fill='x', padx=20, pady=10)

        # Workshop ID
        ttk.Label(params_frame, text='کد کارگاه (10 رقم):').grid(row=0, column=0, sticky='w', pady=5)
        self.workshop_id_entry = ttk.Entry(params_frame, width=20)
        self.workshop_id_entry.grid(row=0, column=1, sticky='w', padx=5)

        # Year
        ttk.Label(params_frame, text='سال (2 رقم، مثال: 3):').grid(row=1, column=0, sticky='w', pady=5)
        self.year_entry = ttk.Entry(params_frame, width=10)
        self.year_entry.grid(row=1, column=1, sticky='w', padx=5)

        # Month
        ttk.Label(params_frame, text='ماه (1-12):').grid(row=2, column=0, sticky='w', pady=5)
        self.month_entry = ttk.Entry(params_frame, width=10)
        self.month_entry.grid(row=2, column=1, sticky='w', padx=5)

        # Output directory
        ttk.Label(params_frame, text='پوشه خروجی:').grid(row=3, column=0, sticky='w', pady=5)
        self.output_dir_entry = ttk.Entry(params_frame, width=40)
        self.output_dir_entry.insert(0, 'output')
        self.output_dir_entry.grid(row=3, column=1, sticky='w', padx=5)
        ttk.Button(params_frame, text='انتخاب...', command=self.browse_output_dir).grid(row=3, column=2)

        # Convert button
        convert_btn = ttk.Button(frame, text='تبدیل به DBF', command=self.convert_csv_to_dbf,
                                style='Accent.TButton')
        convert_btn.pack(pady=10)

        # Progress text
        self.csv_to_dbf_log = scrolledtext.ScrolledText(frame, height=10, width=80)
        self.csv_to_dbf_log.pack(fill='both', expand=True, padx=20, pady=10)

    def create_dbf_to_csv_tab(self):
        """Create DBF → CSV conversion tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='DBF → CSV')

        # Title
        title = tk.Label(frame, text='تبدیل DBF به CSV', font=('Tahoma', 14, 'bold'))
        title.pack(pady=10)

        # Info label
        info = tk.Label(frame, text='✅ دیکد خودکار Iran System Encoding + ساختار SSO 2024',
                       font=('Tahoma', 9), fg='green')
        info.pack()

        # Input files frame
        input_frame = ttk.LabelFrame(frame, text='فایل‌های ورودی (DBF)', padding=10)
        input_frame.pack(fill='x', padx=20, pady=10)

        # Header DBF
        ttk.Label(input_frame, text='فایل dskkar00.dbf:').grid(row=0, column=0, sticky='w', pady=5)
        self.header_dbf_entry = ttk.Entry(input_frame, width=50)
        self.header_dbf_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text='انتخاب...', command=self.browse_header_dbf).grid(row=0, column=2)

        # Workers DBF
        ttk.Label(input_frame, text='فایل dskwor00.dbf:').grid(row=1, column=0, sticky='w', pady=5)
        self.workers_dbf_entry = ttk.Entry(input_frame, width=50)
        self.workers_dbf_entry.grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text='انتخاب...', command=self.browse_workers_dbf).grid(row=1, column=2)

        # Options
        options_frame = ttk.LabelFrame(frame, text='گزینه‌ها', padding=10)
        options_frame.pack(fill='x', padx=20, pady=10)

        self.include_hex_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text='نمایش Hex برای فیلدهای فارسی (توصیه می‌شود)',
                       variable=self.include_hex_var).pack(anchor='w')

        # Output directory
        ttk.Label(options_frame, text='پوشه خروجی:').pack(anchor='w', pady=(10,5))
        output_frame = tk.Frame(options_frame)
        output_frame.pack(fill='x')
        self.dbf_output_dir_entry = ttk.Entry(output_frame, width=50)
        self.dbf_output_dir_entry.insert(0, 'output')
        self.dbf_output_dir_entry.pack(side='left', padx=(0,5))
        ttk.Button(output_frame, text='انتخاب...', command=self.browse_dbf_output_dir).pack(side='left')

        # Convert button
        convert_btn = ttk.Button(frame, text='تبدیل به CSV', command=self.convert_dbf_to_csv,
                                style='Accent.TButton')
        convert_btn.pack(pady=10)

        # Progress text
        self.dbf_to_csv_log = scrolledtext.ScrolledText(frame, height=10, width=80)
        self.dbf_to_csv_log.pack(fill='both', expand=True, padx=20, pady=10)

    # Browse functions
    def browse_header_csv(self):
        filename = filedialog.askopenfilename(title='انتخاب فایل Header CSV',
                                             filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if filename:
            self.header_csv_entry.delete(0, tk.END)
            self.header_csv_entry.insert(0, filename)

    def browse_workers_csv(self):
        filename = filedialog.askopenfilename(title='انتخاب فایل Workers CSV',
                                             filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if filename:
            self.workers_csv_entry.delete(0, tk.END)
            self.workers_csv_entry.insert(0, filename)

    def browse_header_dbf(self):
        filename = filedialog.askopenfilename(title='انتخاب فایل dskkar00.dbf',
                                             filetypes=[('DBF files', '*.dbf'), ('All files', '*.*')])
        if filename:
            self.header_dbf_entry.delete(0, tk.END)
            self.header_dbf_entry.insert(0, filename)

    def browse_workers_dbf(self):
        filename = filedialog.askopenfilename(title='انتخاب فایل dskwor00.dbf',
                                             filetypes=[('DBF files', '*.dbf'), ('All files', '*.*')])
        if filename:
            self.workers_dbf_entry.delete(0, tk.END)
            self.workers_dbf_entry.insert(0, filename)

    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title='انتخاب پوشه خروجی')
        if dirname:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, dirname)

    def browse_dbf_output_dir(self):
        dirname = filedialog.askdirectory(title='انتخاب پوشه خروجی')
        if dirname:
            self.dbf_output_dir_entry.delete(0, tk.END)
            self.dbf_output_dir_entry.insert(0, dirname)

    # Conversion functions
    def convert_csv_to_dbf(self):
        """Convert CSV to DBF"""
        # Validate inputs
        header_csv = self.header_csv_entry.get()
        workers_csv = self.workers_csv_entry.get()
        workshop_id = self.workshop_id_entry.get()
        year = self.year_entry.get()
        month = self.month_entry.get()
        output_dir = self.output_dir_entry.get()

        if not all([header_csv, workers_csv, workshop_id, year, month]):
            messagebox.showerror('خطا', 'لطفاً تمام فیلدها را پر کنید')
            return

        # Clear log
        self.csv_to_dbf_log.delete(1.0, tk.END)

        def run_conversion():
            try:
                # Build command
                cmd = [
                    sys.executable,
                    str(Path(__file__).parent / 'csv_to_dbf_complete.py'),
                    header_csv,
                    workers_csv,
                    '--workshop-id', workshop_id,
                    '--year', year,
                    '--month', month,
                    '--output-dir', output_dir
                ]

                # Run command
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          text=True, bufsize=1)

                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.csv_to_dbf_log.insert(tk.END, line)
                        self.csv_to_dbf_log.see(tk.END)
                        self.root.update_idletasks()

                process.wait()

                if process.returncode == 0:
                    messagebox.showinfo('موفقیت', f'فایل‌های DBF با موفقیت در {output_dir} ایجاد شدند!')
                else:
                    messagebox.showerror('خطا', 'تبدیل با خطا مواجه شد')

            except Exception as e:
                messagebox.showerror('خطا', f'خطا در تبدیل: {str(e)}')

        # Run in thread
        thread = threading.Thread(target=run_conversion)
        thread.start()

    def convert_dbf_to_csv(self):
        """Convert DBF to CSV"""
        # Validate inputs
        header_dbf = self.header_dbf_entry.get()
        workers_dbf = self.workers_dbf_entry.get()
        output_dir = self.dbf_output_dir_entry.get()
        include_hex = self.include_hex_var.get()

        if not all([header_dbf, workers_dbf]):
            messagebox.showerror('خطا', 'لطفاً هر دو فایل DBF را انتخاب کنید')
            return

        # Clear log
        self.dbf_to_csv_log.delete(1.0, tk.END)

        def run_conversion():
            try:
                # Create output directory
                Path(output_dir).mkdir(parents=True, exist_ok=True)

                # Convert header
                cmd_header = [
                    sys.executable,
                    str(Path(__file__).parent / 'dbf_to_csv.py'),
                    header_dbf,
                    '-o', str(Path(output_dir) / 'header.csv')
                ]
                if include_hex:
                    cmd_header.append('--include-hex')

                self.dbf_to_csv_log.insert(tk.END, '=== Converting header file ===\n')
                process = subprocess.Popen(cmd_header, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          text=True, bufsize=1)
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.dbf_to_csv_log.insert(tk.END, line)
                        self.dbf_to_csv_log.see(tk.END)
                        self.root.update_idletasks()
                process.wait()

                # Convert workers
                cmd_workers = [
                    sys.executable,
                    str(Path(__file__).parent / 'dbf_to_csv.py'),
                    workers_dbf,
                    '-o', str(Path(output_dir) / 'workers.csv')
                ]
                if include_hex:
                    cmd_workers.append('--include-hex')

                self.dbf_to_csv_log.insert(tk.END, '\n=== Converting workers file ===\n')
                process = subprocess.Popen(cmd_workers, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          text=True, bufsize=1)
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.dbf_to_csv_log.insert(tk.END, line)
                        self.dbf_to_csv_log.see(tk.END)
                        self.root.update_idletasks()
                process.wait()

                if process.returncode == 0:
                    messagebox.showinfo('موفقیت', f'فایل‌های CSV با موفقیت در {output_dir} ایجاد شدند!')
                else:
                    messagebox.showerror('خطا', 'تبدیل با خطا مواجه شد')

            except Exception as e:
                messagebox.showerror('خطا', f'خطا در تبدیل: {str(e)}')

        # Run in thread
        thread = threading.Thread(target=run_conversion)
        thread.start()


def main():
    root = tk.Tk()
    app = DBFConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
