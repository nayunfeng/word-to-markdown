# word-to-markdown

一个基于 Python 的 Word `.docx` 转 Markdown 工具，面向企业内部文档迁移、知识库入库、AI 检索预处理等场景。

当前推荐使用 **v6** 链路，已支持：

- 段落转 Markdown
- 标题识别（含部分非标准标题）
- 列表转 Markdown
- 表格转 Markdown
- 按标题拆分输出
- 批量处理目录
- 图片抽取到 `media/`
- 图片近似按原文位置插入 Markdown

---

## 1. 项目定位

这个工具不是简单把 Word 文本导出来，而是尽量把 Word 文档转换成适合后续处理的结构化 Markdown，便于：

- 文档迁移到 Git / Wiki / 知识库
- 喂给本地模型或向量库
- 做章节级切分
- 做批量归档和后续检索

---

## 2. 当前推荐入口

请优先使用：

- `main_v6.py`

对应主链路：

- `src/word_to_markdown/cli_v6.py`
- `src/word_to_markdown/converter_v6.py`
- `src/word_to_markdown/parser_v5.py`
- `src/word_to_markdown/markdown_writer_v3.py`
- `src/word_to_markdown/image_extractor_v2.py`
- `src/word_to_markdown/splitter_v2.py`

---

## 3. 项目结构

```text
word-to-markdown/
├─ README.md
├─ README_V6.md
├─ requirements.txt
├─ main.py
├─ main_v2.py
├─ main_v3.py
├─ main_v4.py
├─ main_v5.py
├─ main_v6.py
├─ docs/
│  └─ QUICKSTART_V6.md
├─ examples/
│  └─ README.md
├─ scripts/
│  └─ run_v6.bat
└─ src/
   └─ word_to_markdown/
      ├─ cli.py
      ├─ cli_v2.py
      ├─ cli_v3.py
      ├─ cli_v4.py
      ├─ cli_v5.py
      ├─ cli_v6.py
      ├─ converter.py
      ├─ converter_v2.py
      ├─ converter_v3.py
      ├─ converter_v4.py
      ├─ converter_v5.py
      ├─ converter_v6.py
      ├─ image_extractor_v1.py
      ├─ image_extractor_v2.py
      ├─ markdown_writer.py
      ├─ markdown_writer_v2.py
      ├─ markdown_writer_v3.py
      ├─ parser.py
      ├─ parser_v2.py
      ├─ parser_v3.py
      ├─ parser_v4.py
      ├─ parser_v5.py
      ├─ splitter.py
      └─ splitter_v2.py
```

---

## 4. 安装

### 4.1 创建虚拟环境

```bash
python -m venv .venv
```

### 4.2 激活虚拟环境

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4.3 安装依赖

```bash
pip install -r requirements.txt
```

---

## 5. 使用方式

### 5.1 转换单个 Word 文件

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output
```

### 5.2 按标题拆分

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output --split-by-heading
```

### 5.3 指定拆分层级

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output --split-by-heading --heading-level 2
```

### 5.4 抽取图片并插入 Markdown

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output --split-by-heading --extract-image
```

### 5.5 批量处理目录

```bash
python main_v6.py convert --input ./docs --output ./output --split-by-heading --recursive --extract-image
```

### 5.6 Windows 一键运行

```bat
scripts\run_v6.bat examples output
```

---

## 6. 输出结果

典型输出目录如下：

```text
output/
├─ full.md
├─ media/
│  ├─ image_001.png
│  └─ image_002.jpg
└─ sections/
   ├─ 001-项目背景.md
   ├─ 002-系统设计.md
   └─ 003-接口说明.md
```

说明：

- `full.md`：整篇文档的 Markdown 结果
- `media/`：抽取出的图片资源
- `sections/`：按标题拆分后的 Markdown 文件

---

## 7. 当前支持能力

### 7.1 标题识别

支持两类标题：

1. 标准 Word Heading 样式
2. 启发式识别的非标准标题，例如：
   - `第一章`
   - `一、`
   - `（一）`
   - `1.`
   - `1.1`
   - `（1）`

### 7.2 列表

支持基础列表识别：

- `•`
- `-`
- `*`
- Word 列表样式

### 7.3 表格

支持基础二维表格转 Markdown 表格。

### 7.4 图片

支持抽取 Word 中嵌入图片，并在 Markdown 中尽量按原文流位置插入图片引用。

### 7.5 批量处理

输入路径可以是：

- 单个 `.docx` 文件
- 包含多个 `.docx` 的目录

支持 `--recursive` 递归扫描子目录。

---

## 8. 当前限制

这部分必须看，不然你会对工具有错误预期。

### 8.1 复杂表格

以下场景仍可能失真：

- 合并单元格
- 多级表头
- 复杂跨行跨列
- 表格中深度嵌套内容

### 8.2 图片位置

当前是“近似按原文位置插入”，不是 Word 像素级还原。

### 8.3 非标准标题识别

当前属于启发式判断，不保证所有企业文档都准确。

### 8.4 样式保真度

当前优先保证结构，不追求 Word 样式的 1:1 还原。

---

## 9. 推荐使用策略

如果你要处理企业内部一批 Word 文档，建议这样做：

### 第一步：批量转换

```bash
python main_v6.py convert --input ./docs --output ./output --split-by-heading --recursive --extract-image
```

### 第二步：抽检结果

重点看四件事：

1. 标题拆分是否正确
2. 表格是否失真
3. 图片位置是否可接受
4. 文件名是否符合预期

### 第三步：再做知识库入库

建议把 `sections/` 下拆分后的 Markdown 作为后续知识库入库的基础粒度。

---

## 10. 示例文档建议

建议在 `examples/` 下准备以下几类测试文档：

- 标准标题文档
- 非标准标题文档
- 表格文档
- 图片文档
- 综合混合文档

具体说明见：

- `examples/README.md`

---

## 11. 快速文档

补充说明见：

- `docs/QUICKSTART_V6.md`

---

## 12. 后续可继续增强

这个项目后续最值得继续做的方向：

1. 复杂表格处理
2. 更精细的图片位置还原
3. 图片标题 / 图注识别
4. tests 自动化测试
5. 统一清理旧版入口，收敛到稳定版
6. 增加 front matter / metadata 输出
7. 增加知识库切分策略

---

## 13. 一句话总结

当前这版已经能作为：

**企业 Word 文档 → 结构化 Markdown → 知识库/AI 预处理入口**

来使用，但复杂文档仍建议人工抽检。