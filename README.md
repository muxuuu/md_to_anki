# Markdown 笔记转 Anki 卡片

这个程序可以将 Markdown 格式的读书笔记批量转换为 Anki 卡片。

## 前置要求

1. 安装 Python 3.6 或更高版本
2. 安装 Anki
3. 安装 [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件
4. 确保 Anki 正在运行且 AnkiConnect 插件已启用

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 确保你的 Anki 中已创建名为 "Reading" 的笔记类型，包含以下字段：
   - Context（正文）
   - Book（书名）
   - Chapter（章节）
   - Notes（笔记）

2. 运行程序：
```bash
python md_to_anki.py <markdown文件路径> <牌组名称>
```

例如：
```bash
python md_to_anki.py my_notes.md "读书笔记"
```

## Markdown 格式要求

你的 Markdown 文件需要遵循以下格式：

```markdown
# 书名

## 章节一

- 正文一。
  * 笔记一

- 正文二。

## 章节二

- 正文三。

- 正文四。
  * 笔记四
```

- 使用一级标题 (#) 表示书名
- 使用二级标题 (##) 表示章节
- 使用无序列表 (-) 表示正文
- 使用缩进的无序列表 (* ) 表示笔记（可选） 