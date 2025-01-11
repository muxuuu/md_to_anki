import json
import requests
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import List, Dict, Optional
import os
import sys
import traceback
import logging
from datetime import datetime

# 设置日志文件路径到用户主目录
log_file = os.path.expanduser('~/markdown_to_anki.log')

# 设置日志
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def handle_exception(exc_type, exc_value, exc_traceback):
    """处理未捕获的异常"""
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"未捕获的异常:\n{error_details}")
    error_msg = f"程序发生错误：\n{exc_type.__name__}: {exc_value}\n\n详细信息已写入日志文件：\n{log_file}"
    try:
        messagebox.showerror("错误", error_msg)
    except:
        print(error_msg)

# 设置全局异常处理器
sys.excepthook = handle_exception

# 记录启动信息
logging.info("="*50)
logging.info(f"应用程序启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info(f"Python版本: {sys.version}")
logging.info(f"操作系统: {sys.platform}")
logging.info("="*50)

class MarkdownToAnki:
    def __init__(self, deck_name: str = "Default"):
        self.deck_name = deck_name
        self.current_book = ""
        self.current_chapter = ""
        self.cards = []

    def parse_markdown_file(self, file_path: str) -> None:
        """Parse markdown file and convert to Anki cards."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logging.info(f"Reading file: {file_path}")
            lines = content.split('\n')
            current_context = ""
            current_notes = []

            for line in lines:
                original_line = line  # Store the original line before stripping
                line = line.strip()
                if not line:
                    continue

                # Book title (h1)
                if line.startswith('# '):
                    self.current_book = line[2:].strip()
                    logging.info(f"Found book: {self.current_book}")
                
                # Chapter (h2)
                elif line.startswith('## '):
                    self.current_chapter = line[3:].strip()
                    logging.info(f"Found chapter: {self.current_chapter}")
                    
                # Content (bullet points)
                elif line.startswith('- '):
                    # If there was a previous context, save it as a card
                    if current_context:
                        logging.debug(f"Adding card with context: {current_context}")
                        logging.debug(f"Notes for this card: {current_notes}")
                        self._add_card(current_context, "\n".join(current_notes) if current_notes else "")
                    
                    current_context = line[2:].strip()
                    current_notes = []
                    
                # Notes (sub-bullet points)
                # Check for both space-based (2 or 4 spaces) and tab-based indentation
                elif (original_line.startswith('    *') or  # 4 spaces
                      original_line.startswith('  *') or    # 2 spaces
                      original_line.startswith('\t*')):     # tab
                    note_text = line[1:].strip() if line.startswith('*') else line
                    logging.debug(f"Found note: {note_text}")
                    current_notes.append(note_text)

            # Don't forget to add the last card
            if current_context:
                logging.debug(f"Adding final card with context: {current_context}")
                logging.debug(f"Notes for final card: {current_notes}")
                self._add_card(current_context, "\n".join(current_notes) if current_notes else "")
        except Exception as e:
            logging.error(f"Error parsing file: {str(e)}", exc_info=True)
            raise

    def _add_card(self, context: str, notes: str) -> None:
        """Add a new card to the cards list."""
        card = {
            "Context": context,
            "Book": self.current_book,
            "Chapter": self.current_chapter,
            "Notes": notes
        }
        logging.debug(f"Created card: {card}")
        self.cards.append(card)

    def send_to_anki(self) -> None:
        """Send all cards to Anki via AnkiConnect."""
        try:
            # 首先检查 AnkiConnect 是否可用
            test_payload = {
                "action": "version",
                "version": 6
            }
            response = requests.post('http://localhost:8765', json=test_payload, timeout=5)
            response.raise_for_status()
            
            for card in self.cards:
                self._create_anki_note(card)
            logging.info(f"Successfully added {len(self.cards)} cards to Anki.")
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到Anki。请确保：\n1. Anki 已经打开\n2. AnkiConnect 插件已安装并启用"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            logging.error(f"Error sending cards to Anki: {str(e)}", exc_info=True)
            raise

    def _create_anki_note(self, card: Dict[str, str]) -> None:
        """Create a single note in Anki via AnkiConnect."""
        try:
            note = {
                "deckName": self.deck_name,
                "modelName": "Reading",
                "fields": {
                    "Context": card["Context"],
                    "Book": card["Book"],
                    "Chapter": card["Chapter"],
                    "Notes": card["Notes"]
                },
                "options": {
                    "allowDuplicate": False
                },
                "tags": []
            }

            payload = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": note
                }
            }

            response = requests.post('http://localhost:8765', json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("error"):
                error_msg = f"Anki返回错误：{result['error']}"
                logging.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            logging.error(f"Error creating note: {str(e)}", exc_info=True)
            raise

class App(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            
            # Configure the window
            self.title("Markdown to Anki")
            
            # Set window size and position
            window_width = 500  # 调整默认宽度
            window_height = 260  # 调整默认高度
            
            # 获取屏幕尺寸
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # 计算窗口居中位置
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            
            # 设置窗口大小和位置
            self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            
            # 设置最小窗口大小
            self.minsize(500, 180)  # 调整最小宽度和高度
            
            # Configure the appearance
            ctk.set_appearance_mode("system")  # Use system theme
            ctk.set_default_color_theme("blue")  # Use blue theme
            
            # Configure grid layout
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(3, weight=1)
            
            # Create main frame
            self.main_frame = ctk.CTkFrame(self)
            self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            self.main_frame.grid_columnconfigure(0, weight=1)
            
            # File selection section
            self.file_label = ctk.CTkLabel(
                self.main_frame, 
                text="选择Markdown文件：",
                font=("SF Pro Display", 13)
            )
            self.file_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
            
            self.file_frame = ctk.CTkFrame(self.main_frame)
            self.file_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
            self.file_frame.grid_columnconfigure(0, weight=1)
            
            self.file_path = tk.StringVar()
            self.file_entry = ctk.CTkEntry(
                self.file_frame,
                textvariable=self.file_path,
                placeholder_text="请选择Markdown文件"
            )
            self.file_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
            
            self.browse_button = ctk.CTkButton(
                self.file_frame,
                text="选择文件",
                command=self.browse_file,
                width=100
            )
            self.browse_button.grid(row=0, column=1)
            
            # Deck name section
            self.deck_label = ctk.CTkLabel(
                self.main_frame,
                text="Anki牌组名称：",
                font=("SF Pro Display", 13)
            )
            self.deck_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
            
            self.deck_name = tk.StringVar()
            self.deck_entry = ctk.CTkEntry(
                self.main_frame,
                textvariable=self.deck_name,
                placeholder_text="请输入Anki牌组名称"
            )
            self.deck_entry.grid(row=3, column=0, padx=10, pady=(5, 20), sticky="ew")
            
            # Convert button
            self.convert_button = ctk.CTkButton(
                self.main_frame,
                text="转换并添加到Anki",
                command=self.convert,
                height=32,  # 调整按钮高度
                font=("SF Pro Display", 14)
            )
            self.convert_button.grid(row=4, column=0, padx=10, pady=(0, 10))
            
            logging.info("Application initialized successfully")
        except Exception as e:
            logging.error("Error initializing application", exc_info=True)
            raise

    def browse_file(self):
        try:
            initial_dir = os.path.expanduser("~")
            filename = filedialog.askopenfilename(
                title="选择Markdown文件",
                initialdir=initial_dir,
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )
            if filename:
                self.file_path.set(filename)
                logging.info(f"Selected file: {filename}")
        except Exception as e:
            logging.error("Error browsing file", exc_info=True)
            messagebox.showerror("错误", f"选择文件时出错：{str(e)}")

    def convert(self):
        try:
            file_path = self.file_path.get()
            deck_name = self.deck_name.get()
            
            if not file_path or not deck_name:
                messagebox.showerror("错误", "请选择文件并输入牌组名称")
                return
            
            logging.info(f"Starting conversion with file: {file_path}, deck: {deck_name}")
            converter = MarkdownToAnki(deck_name)
            converter.parse_markdown_file(file_path)
            converter.send_to_anki()
            messagebox.showinfo("成功", "转换完成！")
            logging.info("Conversion completed successfully")
        except Exception as e:
            logging.error("Error during conversion", exc_info=True)
            error_msg = str(e)
            if isinstance(e, ConnectionError):
                error_msg = e.args[0]
            messagebox.showerror("错误", f"转换失败：{error_msg}")

def suppress_macos_warnings():
    """Suppress macOS-specific warnings."""
    import os
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

if __name__ == "__main__":
    try:
        suppress_macos_warnings()
        app = App()
        app.mainloop()
    except Exception as e:
        logging.error("Fatal error in main loop", exc_info=True)
        messagebox.showerror("严重错误", f"程序启动失败：{str(e)}\n\n详细信息已写入日志文件：\n{log_file}") 