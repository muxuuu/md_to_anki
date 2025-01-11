# Klib Markdown to Anki Converter

一个将 Klib 导出的 Markdown 格式的读书笔记批量转换为 Anki 卡片的工具。

A tool for batch converting Markdown reading notes to Anki cards.

## 功能特点 | Features

- 支持从 Markdown 文件批量导入笔记到 Anki | Batch import notes from Markdown files to Anki
- 保持书籍、章节的层级结构 | Maintain book and chapter hierarchy
- 支持笔记和正文的对应关系 | Support mapping between notes and content
- 简单易用的图形界面 | User-friendly graphical interface
- 自动创建 Anki 卡片 | Automatically create Anki cards

## 前置要求 | Prerequisites

1. Python 3.6 或更高版本 | Python 3.6 or higher
2. Anki 软件 | Anki software
3. [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件 | AnkiConnect add-on

## 安装和运行 | Installation and Running

1. 下载源代码 | Download the source code
2. 安装依赖 | Install dependencies

```bash
pip install -r requirements.txt
```

3. 运行程序 | Run the program

```bash
python md_to_anki.py
```

## 使用方法 | Usage

1. 确保 Anki 中已创建名为 "Reading" 的笔记类型，包含以下字段：

   - Context（正文）
   - Book（书名）
   - Chapter（章节）
   - Notes（笔记）

   Make sure you have created a note type named "Reading" in Anki with the following fields:

   - Context
   - Book
   - Chapter
   - Notes
2. 在图形界面中：

   - 选择 Markdown 文件
   - 输入目标牌组名称
   - 点击"转换并添加到 Anki"

   In the GUI:

   - Select your Markdown file
   - Enter the target deck name
   - Click "Convert and Add to Anki"

## Markdown 格式要求 | Markdown Format Requirements

你的 Markdown 文件需要遵循以下格式：

Your Markdown file should follow this format:

```markdown
# 书名 | Book Title

## 章节一 | Chapter 1

- 正文一。| Content 1
    * 笔记一 | Note 1

- 正文二。| Content 2
    * 笔记二 | Note 2

## 章节二 | Chapter 2

- 正文三 | Content 3

- 正文四 | Content 4
    * 笔记四 | Note 4
```

- 使用一级标题 (#) 表示书名 | Use h1 (#) for book title
- 使用二级标题 (##) 表示章节 | Use h2 (##) for chapters
- 使用无序列表 (-) 表示正文 | Use unordered list (-) for content
- 使用缩进的无序列表 (* ) 表示笔记（可选）| Use indented list (* ) for notes (optional)

## 注意事项 | Notes

- 运行程序时确保 Anki 已打开 | Make sure Anki is running when using the program
- 确保已安装并启用 AnkiConnect 插件 | Ensure AnkiConnect add-on is installed and enabled
- 如果牌组不存在，程序会自动创建 | The program will create the deck if it doesn't exist

## 许可证 | License

MIT License

## 贡献 | Contributing

欢迎提交 Issue 和 Pull Request。

Issues and Pull Requests are welcome.
