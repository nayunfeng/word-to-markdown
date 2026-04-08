# word-to-markdown

一个基于 Python 的 Word 转 Markdown 工具，目标是把 `.docx` 文档转换为结构化 Markdown，并支持按标题拆分输出，便于知识库入库、文档迁移和后续 AI 检索。

## 目标能力

- 读取 `.docx` 文件
- 提取段落、标题、列表、表格
- 转成 Markdown
- 按标题层级拆分为多个 Markdown 文件
- 输出图片资源目录
- 支持批量处理

## 当前版本

当前仓库已提供第一版可运行骨架，包含：

- 命令行入口
- 文档解析
- Markdown 生成
- 按一级/二级标题拆分
- 输出目录管理

## 项目结构

```text
word-to-markdown/
├─ README.md
├─ requirements.txt
├─ main.py
└─ src/
   └─ word_to_markdown/
      ├─ __init__.py
      ├─ cli.py
      ├─ converter.py
      ├─ markdown_writer.py
      ├─ models.py
      ├─ parser.py
      └─ splitter.py
```

## 安装

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## 使用方式

### 1. 转换单个文件

```bash
python main.py convert --input ./example/demo.docx --output ./output
```

### 2. 转换并按标题拆分

```bash
python main.py convert --input ./example/demo.docx --output ./output --split-by-heading
```

### 3. 指定拆分层级

```bash
python main.py convert --input ./example/demo.docx --output ./output --split-by-heading --heading-level 2
```

## 输出示例

```text
output/
├─ full.md
└─ sections/
   ├─ 001-项目背景.md
   ├─ 002-系统设计.md
   └─ 003-接口说明.md
```

## 设计说明

第一版优先解决“能跑、可扩展、目录清晰”三个问题。

后续可以继续增强：

- 图片抽取
- 更精细的表格转 Markdown
- 样式映射（加粗、斜体、代码）
- 页眉页脚、脚注处理
- 批量目录扫描
- front matter 输出
- 与向量库/知识库系统集成

## 后续建议

这个项目适合继续补充：

1. `examples/` 示例文档
2. `tests/` 自动化测试
3. 图片导出与引用
4. 更强的标题识别规则
5. Windows 下的一键启动脚本
