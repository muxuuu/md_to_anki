import json
import requests
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Dict, Optional
import os

class MarkdownToAnki:
    def __init__(self, deck_name: str = "Default"):
        self.deck_name = deck_name
        self.current_book = ""
        self.current_chapter = ""
        self.cards = []

    def parse_markdown_file(self, file_path: str) -> None:
        """Parse markdown file and convert to Anki cards."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

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

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown to Anki")
        
        # Set window size and position
        window_width = 800
        window_height = 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure styles
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=6)
        style.configure('TEntry', padding=6)
        
        # Main container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="选择Markdown文件：").pack(side=tk.LEFT)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(file_frame, text="选择文件", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT)
        
        # Deck name input
        deck_frame = ttk.Frame(main_frame)
        deck_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(deck_frame, text="Anki牌组名称：").pack(side=tk.LEFT)
        
        self.deck_name = tk.StringVar()
        self.deck_entry = ttk.Entry(deck_frame, textvariable=self.deck_name, width=50)
        self.deck_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Convert button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.convert_button = ttk.Button(
            button_frame,
            text="转换并添加到Anki",
            command=self.convert,
            style='TButton'
        )
        self.convert_button.pack(pady=10)

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
        file_path = self.file_path.get()
        deck_name = self.deck_name.get()
        
        if not file_path or not deck_name:
            messagebox.showerror("错误", "请选择文件并输入牌组名称")
            return
            
        try:
            converter = MarkdownToAnki(deck_name)
            converter.parse_markdown_file(file_path)
            converter.send_to_anki()
            messagebox.showinfo("成功", "转换完成！")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop() 