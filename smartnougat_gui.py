#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartNougat GUI - Graphical User Interface for SmartNougat 0712
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import re
import time
import queue
from pathlib import Path
import json
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD

class SmartNougatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartNougat GUI - PDF/DOCX to LaTeX Converter")
        self.root.geometry("900x700")
        
        # Variables
        self.selected_file = tk.StringVar()
        self.page_range = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.is_processing = False
        self.process = None
        self.output_queue = queue.Queue()
        self.start_time = None
        
        # Statistics
        self.current_page = tk.IntVar(value=0)
        self.total_pages = tk.IntVar(value=0)
        self.found_formulas = tk.IntVar(value=0)
        self.fixed_formulas = tk.IntVar(value=0)
        self.processing_time = tk.StringVar(value="0초")
        
        # Create UI
        self.create_widgets()
        
        # Start output reader thread
        self.root.after(100, self.check_output_queue)
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection section
        ttk.Label(main_frame, text="파일 선택:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="파일 찾기", command=self.browse_file).grid(row=0, column=0, padx=(0, 5))
        
        # File entry with drag and drop support
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file, state='readonly')
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Enable drag and drop
        self.enable_drag_drop()
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="옵션 설정", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="페이지 범위:").grid(row=0, column=0, sticky=tk.W, pady=5)
        page_entry = ttk.Entry(options_frame, textvariable=self.page_range, width=20)
        page_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(options_frame, text="(예: 1-5, 10, 15 또는 비워두면 전체)", 
                 font=('Arial', 8), foreground='gray').grid(row=0, column=2, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="출력 폴더:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(options_frame, textvariable=self.output_folder, state='readonly').grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="실시간 정보", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        # Progress bar
        ttk.Label(stats_frame, text="진행률:").grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(stats_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Statistics labels
        ttk.Label(stats_frame, text="처리 페이지:").grid(row=1, column=0, sticky=tk.W)
        self.page_label = ttk.Label(stats_frame, text="0 / 0")
        self.page_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="발견된 수식:").grid(row=1, column=2, sticky=tk.E)
        self.formula_label = ttk.Label(stats_frame, text="0개")
        self.formula_label.grid(row=1, column=3, sticky=tk.W)
        
        ttk.Label(stats_frame, text="수정된 수식:").grid(row=2, column=0, sticky=tk.W)
        self.fixed_label = ttk.Label(stats_frame, text="0개")
        self.fixed_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="처리 시간:").grid(row=2, column=2, sticky=tk.E)
        self.time_label = ttk.Label(stats_frame, textvariable=self.processing_time)
        self.time_label.grid(row=2, column=3, sticky=tk.W)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="처리 로그", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for coloring
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('warning', foreground='orange')
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="시작", command=self.start_processing, 
                                      style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", command=self.stop_processing, 
                                     state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Create style for accent button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    def enable_drag_drop(self):
        """Enable drag and drop functionality"""
        try:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop_file)
            
            # Visual feedback for drag and drop area
            drop_label = ttk.Label(self.root, text="파일을 여기로 끌어다 놓으세요", 
                                  font=('Arial', 9), foreground='gray')
            drop_label.place(relx=0.5, rely=0.1, anchor='center')
        except:
            # If tkinterdnd2 is not available, just skip
            pass
    
    def drop_file(self, event):
        """Handle dropped file"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith(('.pdf', '.docx')):
                self.selected_file.set(file_path)
                file_stem = Path(file_path).stem
                output_path = f"C:\\test\\{file_stem}_output"
                self.output_folder.set(output_path)
                self.log(f"파일 드롭됨: {file_path}", 'info')
            else:
                messagebox.showwarning("경고", "PDF 또는 DOCX 파일만 지원됩니다.")
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="PDF 또는 DOCX 파일 선택",
            filetypes=[
                ("문서 파일", "*.pdf;*.docx"),
                ("PDF 파일", "*.pdf"),
                ("DOCX 파일", "*.docx"),
                ("모든 파일", "*.*")
            ]
        )
        
        if filename:
            self.selected_file.set(filename)
            # Set default output folder
            file_stem = Path(filename).stem
            output_path = f"C:\\test\\{file_stem}_output"
            self.output_folder.set(output_path)
            self.log(f"파일 선택됨: {filename}", 'info')
    
    def log(self, message, tag=None):
        """Add message to log with optional formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_processing(self):
        if not self.selected_file.get():
            messagebox.showwarning("경고", "파일을 먼저 선택해주세요.")
            return
        
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start(10)
        
        # Reset statistics
        self.current_page.set(0)
        self.total_pages.set(0)
        self.found_formulas.set(0)
        self.fixed_formulas.set(0)
        self.start_time = time.time()
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        self.log("처리 시작...", 'info')
        
        # Start processing thread
        thread = threading.Thread(target=self.run_smartnougat, daemon=True)
        thread.start()
        
        # Start timer update
        self.update_timer()
    
    def run_smartnougat(self):
        try:
            # Build command
            cmd = [sys.executable, "smartnougat_0714.py", self.selected_file.get()]
            
            # Add page range if specified
            if self.page_range.get():
                cmd.extend(["-p", self.page_range.get()])
            
            # Add output folder
            cmd.extend(["-o", self.output_folder.get()])
            
            self.output_queue.put(("info", f"실행 명령: {' '.join(cmd)}"))
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.parse_output(line.strip())
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self.output_queue.put(("success", "처리 완료!"))
                # Open output folder
                self.root.after(1000, lambda: self.open_output_folder())
            else:
                self.output_queue.put(("error", f"처리 실패 (코드: {self.process.returncode})"))
                
        except Exception as e:
            self.output_queue.put(("error", f"오류 발생: {str(e)}"))
        finally:
            self.is_processing = False
            self.root.after(0, self.processing_finished)
    
    def parse_output(self, line):
        """Parse output line and extract information"""
        self.output_queue.put(("normal", line))
        
        # Extract page information
        page_match = re.search(r'페이지\s*(\d+)/(\d+)', line)
        if page_match:
            current, total = map(int, page_match.groups())
            self.current_page.set(current)
            self.total_pages.set(total)
            self.update_page_label()
        
        # Extract formula count
        formula_match = re.search(r'(\d+)개?\s*(?:발견|수식)', line)
        if formula_match and '수식' in line:
            count = int(formula_match.group(1))
            self.found_formulas.set(count)
            self.update_formula_label()
        
        # Extract fixed count
        if 'LaTeX 수정 완료' in line or 'Fixed' in line:
            self.output_queue.put(("success", "LaTeX 수정 완료"))
        
        # Check for errors
        if 'error' in line.lower() or '오류' in line:
            self.output_queue.put(("error", line))
    
    def check_output_queue(self):
        """Check output queue and update UI"""
        try:
            while True:
                tag, message = self.output_queue.get_nowait()
                self.log(message, tag)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_output_queue)
    
    def update_timer(self):
        """Update processing time"""
        if self.is_processing and self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.processing_time.set(f"{elapsed}초")
            self.root.after(1000, self.update_timer)
    
    def update_page_label(self):
        self.page_label.config(text=f"{self.current_page.get()} / {self.total_pages.get()}")
    
    def update_formula_label(self):
        self.formula_label.config(text=f"{self.found_formulas.get()}개")
    
    def stop_processing(self):
        if self.process:
            self.process.terminate()
            self.log("처리 중지됨", 'warning')
            self.processing_finished()
    
    def processing_finished(self):
        """Reset UI after processing finished"""
        self.progress_bar.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_processing = False
    
    def open_output_folder(self):
        """Open output folder in Windows Explorer"""
        output_path = self.output_folder.get()
        if os.path.exists(output_path):
            os.startfile(output_path)
            self.log(f"출력 폴더 열기: {output_path}", 'info')
        else:
            # Try to find the actual output folder
            parent_dir = os.path.dirname(output_path)
            base_name = Path(self.selected_file.get()).stem
            
            # Look for folders with similar pattern
            for folder in os.listdir(parent_dir) if os.path.exists(parent_dir) else []:
                if folder.startswith(base_name) and os.path.isdir(os.path.join(parent_dir, folder)):
                    actual_path = os.path.join(parent_dir, folder)
                    os.startfile(actual_path)
                    self.log(f"출력 폴더 열기: {actual_path}", 'info')
                    break


def main():
    try:
        # Try to use TkinterDnD for drag and drop support
        root = TkinterDnD.Tk()
    except:
        # Fall back to regular Tk if TkinterDnD is not available
        root = tk.Tk()
    
    app = SmartNougatGUI(root)
    
    # Set window icon if available
    try:
        root.iconbitmap('smartnougat.ico')
    except:
        pass
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()