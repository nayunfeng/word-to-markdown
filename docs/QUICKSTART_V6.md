# Word to Markdown v6 快速使用说明

当前推荐使用 v6 入口：`main_v6.py`

## 1. 安装依赖

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## 2. 单文件转换

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output
```

## 3. 按标题拆分

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output --split-by-heading
```

## 4. 抽取图片并尽量按原文位置插入

```bash
python main_v6.py convert --input ./demo/example.docx --output ./output --split-by-heading --extract-image
```

## 5. 批量处理目录

```bash
python main_v6.py convert --input ./docs --output ./output --split-by-heading --recursive --extract-image
```

## 6. 输出结果示例

```text
output/
├─ full.md
├─ media/
│  ├─ image_001.png
│  └─ image_002.jpg
└─ sections/
   ├─ 001-项目背景.md
   └─ 002-系统设计.md
```

## 7. 当前已支持能力

- 标题识别（含部分非标准标题）
- 段落转 Markdown
- 列表转 Markdown
- 表格转 Markdown
- 按标题拆分
- 批量处理目录
- 图片抽取
- 图片近似按原文位置插入

## 8. 当前限制

- 复杂表格（合并单元格、多级表头）仍可能不准
- 图片位置是近似还原，不是 Word 像素级还原
- 非标准标题识别仍是启发式，不保证所有文档都准确

## 9. 推荐使用策略

如果是企业内部文档迁移，建议优先这样跑：

```bash
python main_v6.py convert --input ./docs --output ./output --split-by-heading --recursive --extract-image
```

然后人工抽检：

1. 标题拆分是否正确
2. 表格是否失真
3. 图片位置是否可接受
4. 文件名是否符合预期
