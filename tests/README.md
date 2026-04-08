# tests 目录说明

当前测试采用 Python 内置 `unittest`，不依赖 `pytest`。

## 运行方式

在项目根目录执行：

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## 当前覆盖范围

- Markdown 表格输出
- 列表输出
- 图片 Markdown 输出
- 安全文件名处理
- 非标准标题规则识别

## 说明

当前测试以“纯函数 / 轻逻辑”优先，先覆盖最容易回归出错的核心规则。

后续建议继续补：

1. 真实 `.docx` 文件集成测试
2. 批量目录转换测试
3. 图片抽取测试
4. 复杂表格测试
