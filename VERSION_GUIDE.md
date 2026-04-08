# Version Guide

为了减少仓库中 `v1 ~ v6` 入口带来的混淆，当前约定如下：

## 推荐使用

请优先使用稳定入口：

- `main_stable.py`

它当前内部指向：

- `cli_stable.py`
- `converter_v6.py`

也就是说：

**stable = 当前已验证推荐链路 = v6**

---

## 各版本定位

### v1
最早的最小可运行版本，只支持基础段落和标题。

### v2
补了基础表格 / 列表支持，但整体链路不完整。

### v3
修正了段落与表格的混排顺序，是从“玩具版本”到“可用版本”的关键一步。

### v4
增加了启发式非标准标题识别，并支持目录批量处理。

### v5
增加了图片抽取，但图片主要是统一导出和追加引用。

### v6
在 v5 基础上继续增强，支持图片近似按原文位置插入，是当前推荐稳定链路。

---

## 当前建议

### 普通使用者
只需要知道：

```bash
python main_stable.py convert --input ./docs --output ./output --split-by-heading --recursive --extract-image
```

### 开发者
需要知道：

- `main_stable.py` 是统一入口
- `converter_v6.py` 是当前稳定转换链路
- `parser_v5.py` 是当前稳定解析链路
- `markdown_writer_v3.py` 是当前稳定 Markdown 输出链路
- `splitter_v2.py` 是当前稳定拆分链路

---

## 后续收敛原则

从现在开始，不再建议继续新增 `main_v7.py / main_v8.py` 这种入口。

后续如果有增强，建议遵循以下原则：

1. 优先在稳定链路上演进
2. 新实验能力可以放在独立模块中
3. 验证通过后，再并入 stable
4. 对外只保留一个推荐入口

---

## 一句话结论

当前仓库请这样理解：

- `main_stable.py`：给人用的
- `v1 ~ v6`：演进历史与实现过程
