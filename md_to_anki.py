import json
import requests
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import List, Dict, Optional
import os
import sys

class MarkdownToAnki:
    def __init__(self, deck_name: str = "Default"):
        self.deck_name = deck_name
        self.current_book = ""
        self.current_chapter = ""
        self.cards = []

    @staticmethod
    def get_deck_names() -> List[str]:
        """Get all deck names from Anki via AnkiConnect."""
        payload = {
            "action": "deckNames",
            "version": 6
        }
        try:
            response = requests.post('http://localhost:8765', json=payload)
            if response.status_code == 200:
                result = response.json()
                if not result.get("error"):
                    return result["result"]
            return []
        except:
            return []

    def parse_markdown_content(self, content: str) -> None:
        """Parse markdown content and convert to Anki cards."""
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
                print(f"Found book: {self.current_book}")
            
            # Chapter (h2)
            elif line.startswith('## '):
                self.current_chapter = line[3:].strip()
                print(f"Found chapter: {self.current_chapter}")
                
            # Content (bullet points)
            elif line.startswith('- '):
                # If there was a previous context, save it as a card
                if current_context:
                    print(f"Adding card with context: {current_context}")
                    print(f"Notes for this card: {current_notes}")
                    self._add_card(current_context, "\n".join(current_notes) if current_notes else "")
                
                current_context = line[2:].strip()
                current_notes = []
                
            # Notes (sub-bullet points)
            # Check for both space-based (2 or 4 spaces) and tab-based indentation
            elif (original_line.startswith('    *') or  # 4 spaces
                  original_line.startswith('  *') or    # 2 spaces
                  original_line.startswith('\t*')):     # tab
                note_text = line[1:].strip() if line.startswith('*') else line
                print(f"Found note: {note_text}")
                current_notes.append(note_text)
                print(f"Current notes list: {current_notes}")

        # Don't forget to add the last card
        if current_context:
            print(f"Adding final card with context: {current_context}")
            print(f"Notes for final card: {current_notes}")
            self._add_card(current_context, "\n".join(current_notes) if current_notes else "")

    def parse_markdown_file(self, file_path: str) -> None:
        """Parse markdown file and convert to Anki cards."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.parse_markdown_content(content)

    def _add_card(self, context: str, notes: str) -> None:
        """Add a new card to the cards list."""
        card = {
            "Context": context,
            "Book": self.current_book,
            "Chapter": self.current_chapter,
            "Notes": notes
        }
        print(f"Created card: {card}")
        self.cards.append(card)

    def send_to_anki(self) -> None:
        """Send all cards to Anki via AnkiConnect."""
        for card in self.cards:
            self._create_anki_note(card)
        print(f"Successfully added {len(self.cards)} cards to Anki.")

    def _create_anki_note(self, card: Dict[str, str]) -> None:
        """Create a single note in Anki via AnkiConnect."""
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
        if response.status_code != 200:
            print(f"Error adding note: {response.text}")
            return

        result = response.json()
        if result.get("error"):
            print(f"Error adding note: {result['error']}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.title("Markdown to Anki")
        
        # Set window size and position
        window_width = 700  # 调整默认宽度
        window_height = 500  # 调整默认高度
        
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 计算窗口居中位置
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # 设置窗口大小和位置
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 设置最小窗口大小
        self.minsize(600, 400)  # 调整最小宽度和高度
        
        # Configure the appearance
        ctk.set_appearance_mode("system")  # Use system theme
        ctk.set_default_color_theme("blue")  # Use blue theme
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make text area expandable
        
        # Input method selection
        self.input_method_frame = ctk.CTkFrame(self.main_frame)
        self.input_method_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.input_method = tk.StringVar(value="file")
        
        self.file_radio = ctk.CTkRadioButton(
            self.input_method_frame,
            text="从文件导入",
            variable=self.input_method,
            value="file",
            command=self.toggle_input_method
        )
        self.file_radio.pack(side="left", padx=(0, 20))
        
        self.text_radio = ctk.CTkRadioButton(
            self.input_method_frame,
            text="直接输入",
            variable=self.input_method,
            value="text",
            command=self.toggle_input_method
        )
        self.text_radio.pack(side="left")
        
        # File selection frame
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")
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
        
        # Text input frame
        self.text_frame = ctk.CTkFrame(self.main_frame)
        self.text_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)
        
        self.text_input = ctk.CTkTextbox(
            self.text_frame,
            wrap="word",
            font=("SF Pro Display", 13)
        )
        self.text_input.grid(row=0, column=0, sticky="nsew")
        
        # Initially hide text frame
        self.text_frame.grid_remove()
        
        # Deck selection section
        self.deck_label = ctk.CTkLabel(
            self.main_frame,
            text="Anki牌组名称：",
            font=("SF Pro Display", 13)
        )
        self.deck_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Deck selection frame
        self.deck_frame = ctk.CTkFrame(self.main_frame)
        self.deck_frame.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.deck_frame.grid_columnconfigure(0, weight=1)
        
        # Get deck names
        deck_names = MarkdownToAnki.get_deck_names()
        
        # Deck combobox
        self.deck_name = tk.StringVar()
        self.deck_combo = ctk.CTkComboBox(
            self.deck_frame,
            values=deck_names,
            variable=self.deck_name,
            state="normal" if deck_names else "disabled"
        )
        self.deck_combo.grid(row=0, column=0, sticky="ew")
        
        # Add new deck entry and button
        self.new_deck_frame = ctk.CTkFrame(self.main_frame)
        self.new_deck_frame.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.new_deck_frame.grid_columnconfigure(0, weight=1)
        
        self.new_deck_entry = ctk.CTkEntry(
            self.new_deck_frame,
            placeholder_text="或输入新牌组名称"
        )
        self.new_deck_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Convert button
        self.convert_button = ctk.CTkButton(
            self.main_frame,
            text="转换并添加到Anki",
            command=self.convert,
            height=32,
            font=("SF Pro Display", 14)
        )
        self.convert_button.grid(row=6, column=0, padx=10, pady=(0, 10))

    def toggle_input_method(self):
        if self.input_method.get() == "file":
            self.text_frame.grid_remove()
            self.file_frame.grid()
        else:
            self.file_frame.grid_remove()
            self.text_frame.grid()

    def browse_file(self):
        initial_dir = os.path.expanduser("~")
        filename = filedialog.askopenfilename(
            title="选择Markdown文件",
            initialdir=initial_dir,
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def convert(self):
        deck_name = self.new_deck_entry.get() or self.deck_name.get()
        
        if not deck_name:
            messagebox.showerror("错误", "请选择或输入牌组名称")
            return
            
        try:
            converter = MarkdownToAnki(deck_name)
            
            if self.input_method.get() == "file":
                file_path = self.file_path.get()
                if not file_path:
                    messagebox.showerror("错误", "请选择Markdown文件")
                    return
                converter.parse_markdown_file(file_path)
            else:
                content = self.text_input.get("1.0", tk.END)
                if not content.strip():
                    messagebox.showerror("错误", "请输入Markdown内容")
                    return
                converter.parse_markdown_content(content)
                
            converter.send_to_anki()
            messagebox.showinfo("成功", "转换完成！")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败：{str(e)}")

def suppress_macos_warnings():
    """Suppress macOS-specific warnings."""
    import os
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

if __name__ == "__main__":
    suppress_macos_warnings()
    app = App()
    app.mainloop() 