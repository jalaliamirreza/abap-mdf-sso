#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Best eRun SAP/Tamin E-Service Assistance
رابط گرافیکی حرفه‌ای تبدیل DBF برای سازمان تامین اجتماعی

Professional GUI for converting between CSV and DBF formats
for Iranian Social Security Organization files with Iran System encoding.
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
        self.root.title("Best eRun SAP/Tamin E-Service Assistance")
        self.root.geometry("900x700")

        # Set modern color scheme
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#3498DB',    # Bright blue
            'success': '#27AE60',      # Green
            'warning': '#F39C12',      # Orange
            'danger': '#E74C3C',       # Red
            'light': '#ECF0F1',        # Light gray
            'dark': '#34495E',         # Dark gray
            'white': '#FFFFFF',
            'persian_blue': '#0C457D', # Persian blue
        }

        self.root.configure(bg=self.colors['light'])

        # Configure custom styles
        self.setup_styles()

        # Create header with logo
        self.create_header()

        # Configure RTL support for Persian
        self.root.option_add('*Font', 'Tahoma 10')

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Create tabs
        self.create_csv_to_dbf_tab()
        self.create_dbf_to_csv_tab()

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook style
        style.configure('Custom.TNotebook', background=self.colors['light'], borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       padding=[20, 10],
                       background=self.colors['dark'],
                       foreground=self.colors['white'],
                       font=('Tahoma', 10, 'bold'))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['secondary'])],
                 foreground=[('selected', self.colors['white'])])

        # Configure frame styles
        style.configure('Card.TFrame', background=self.colors['white'], relief='raised')
        style.configure('TLabelframe', background=self.colors['white'],
                       borderwidth=2, relief='groove')
        style.configure('TLabelframe.Label', background=self.colors['white'],
                       font=('Tahoma', 10, 'bold'))

        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.colors['secondary'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       font=('Tahoma', 11, 'bold'),
                       padding=[20, 10])
        style.map('Primary.TButton',
                 background=[('active', '#2980B9')])

        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       font=('Tahoma', 11, 'bold'),
                       padding=[20, 10])

    def create_header(self):
        """Create modern header with branding"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame,
                              text='Best eRun',
                              font=('Tahoma', 24, 'bold'),
                              bg=self.colors['primary'],
                              fg=self.colors['white'])
        title_label.pack(pady=(15, 0))

        # Subtitle
        subtitle = tk.Label(header_frame,
                           text='SAP/Tamin E-Service Assistance',
                           font=('Tahoma', 12),
                           bg=self.colors['primary'],
                           fg=self.colors['light'])
        subtitle.pack()

        # Version badge
        version_frame = tk.Frame(header_frame, bg=self.colors['success'],
                                borderwidth=0)
        version_frame.place(relx=0.95, rely=0.5, anchor='e')

        version_label = tk.Label(version_frame,
                                text='SSO 2024 ✓',
                                font=('Tahoma', 9, 'bold'),
                                bg=self.colors['success'],
                                fg=self.colors['white'],
                                padx=10, pady=5)
        version_label.pack()

    def create_csv_to_dbf_tab(self):
        """Create CSV → DBF conversion tab"""
        frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(frame, text='📄 CSV → DBF')

        # Create scrollable canvas
        canvas = tk.Canvas(frame, bg=self.colors['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['light'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title card
        title_card = tk.Frame(scrollable_frame, bg=self.colors['white'],
                             relief='solid', borderwidth=1)
        title_card.pack(fill='x', padx=20, pady=(20, 10))

        title = tk.Label(title_card, text='تبدیل CSV به DBF',
                        font=('Tahoma', 16, 'bold'),
                        bg=self.colors['white'],
                        fg=self.colors['primary'])
        title.pack(pady=15)

        # Info badge
        info_frame = tk.Frame(scrollable_frame, bg=self.colors['success'],
                             relief='solid', borderwidth=1)
        info_frame.pack(fill='x', padx=20, pady=5)

        info = tk.Label(info_frame,
                       text='✓ ساختار جدید SSO 2024: 25 فیلد header | 29 فیلد workers | Iran System Encoding',
                       font=('Tahoma', 9, 'bold'),
                       bg=self.colors['success'],
                       fg=self.colors['white'],
                       pady=8)
        info.pack()

        # Input files frame
        input_frame = ttk.LabelFrame(scrollable_frame, text='📁 فایل‌های ورودی (CSV)',
                                    padding=15, style='TLabelframe')
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
        params_frame = ttk.LabelFrame(scrollable_frame, text='⚙️ پارامترها',
                                     padding=15, style='TLabelframe')
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
        button_frame = tk.Frame(scrollable_frame, bg=self.colors['light'])
        button_frame.pack(pady=20)

        convert_btn = tk.Button(button_frame,
                               text='🚀 تبدیل به DBF',
                               command=self.convert_csv_to_dbf,
                               bg=self.colors['secondary'],
                               fg=self.colors['white'],
                               font=('Tahoma', 12, 'bold'),
                               borderwidth=0,
                               padx=40, pady=15,
                               cursor='hand2',
                               activebackground='#2980B9',
                               activeforeground=self.colors['white'])
        convert_btn.pack()

        # Progress text
        log_frame = ttk.LabelFrame(scrollable_frame, text='📊 گزارش پیشرفت',
                                  padding=10, style='TLabelframe')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.csv_to_dbf_log = scrolledtext.ScrolledText(log_frame,
                                                        height=8,
                                                        width=80,
                                                        bg='#2C3E50',
                                                        fg='#ECF0F1',
                                                        font=('Consolas', 9),
                                                        insertbackground='white')
        self.csv_to_dbf_log.pack(fill='both', expand=True)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_dbf_to_csv_tab(self):
        """Create DBF → CSV conversion tab"""
        frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(frame, text='💾 DBF → CSV')

        # Create scrollable canvas
        canvas = tk.Canvas(frame, bg=self.colors['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['light'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title card
        title_card = tk.Frame(scrollable_frame, bg=self.colors['white'],
                             relief='solid', borderwidth=1)
        title_card.pack(fill='x', padx=20, pady=(20, 10))

        title = tk.Label(title_card, text='تبدیل DBF به CSV',
                        font=('Tahoma', 16, 'bold'),
                        bg=self.colors['white'],
                        fg=self.colors['primary'])
        title.pack(pady=15)

        # Info badge
        info_frame = tk.Frame(scrollable_frame, bg=self.colors['persian_blue'],
                             relief='solid', borderwidth=1)
        info_frame.pack(fill='x', padx=20, pady=5)

        info = tk.Label(info_frame,
                       text='✓ دیکد خودکار Iran System | نمایش متن فارسی | ساختار SSO 2024',
                       font=('Tahoma', 9, 'bold'),
                       bg=self.colors['persian_blue'],
                       fg=self.colors['white'],
                       pady=8)
        info.pack()

        # Input files frame
        input_frame = ttk.LabelFrame(scrollable_frame, text='📁 فایل‌های ورودی (DBF)',
                                    padding=15, style='TLabelframe')
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
        options_frame = ttk.LabelFrame(scrollable_frame, text='⚙️ گزینه‌ها',
                                      padding=15, style='TLabelframe')
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
        button_frame = tk.Frame(scrollable_frame, bg=self.colors['light'])
        button_frame.pack(pady=20)

        convert_btn = tk.Button(button_frame,
                               text='📊 تبدیل به CSV',
                               command=self.convert_dbf_to_csv,
                               bg=self.colors['persian_blue'],
                               fg=self.colors['white'],
                               font=('Tahoma', 12, 'bold'),
                               borderwidth=0,
                               padx=40, pady=15,
                               cursor='hand2',
                               activebackground='#0A3A6B',
                               activeforeground=self.colors['white'])
        convert_btn.pack()

        # Progress text
        log_frame = ttk.LabelFrame(scrollable_frame, text='📊 گزارش پیشرفت',
                                  padding=10, style='TLabelframe')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.dbf_to_csv_log = scrolledtext.ScrolledText(log_frame,
                                                        height=8,
                                                        width=80,
                                                        bg='#2C3E50',
                                                        fg='#ECF0F1',
                                                        font=('Consolas', 9),
                                                        insertbackground='white')
        self.dbf_to_csv_log.pack(fill='both', expand=True)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
