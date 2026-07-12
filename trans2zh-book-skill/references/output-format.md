# Per-Chapter Output Format

Give every chapter agent this exact template so the book reads as one coherent
voice rather than 17 disconnected translations. The headings are fixed; the depth
adapts to the source lecture.

```markdown
# 第N章: 中文标题 (English Title)
> 原课程: <Course>, <Institution>, <Term>
> 主讲: <Instructor>
> 本章基于 Lecture X, slides + 阅读论文 [Paper Title]

## 一、本章概要 (Overview)
- 核心问题与动机
- 与前后章节的逻辑关系

## 二、核心概念与数学基础 (Core Concepts & Math)
- 关键定义 (中英对照)
- 完整数学推导 (LaTeX, 从第一性原理出发)
- 物理直觉与几何解释

## 三、论文精读 (Paper Deep Dive)
- 方法论逐段解读
- 关键公式展开推导
- 实验设计与结果分析

## 四、算法与代码实现 (Algorithm & Code)
- 伪代码 → PyTorch/Python 实现
- 关键代码逐行注释
- 训练技巧与工程细节

## 五、核心 Takeaway 与延伸阅读 (Takeaways)
- 3-5 个核心洞察
- 开放问题与研究方向
- 推荐延伸阅读

## 六、练习与思考 (Exercises)
- 基于本章内容的思考题
```

## Chapter Navigation (REQUIRED — add at end of every chapter)

Every chapter MUST end with a prev/next navigation block. This is critical for
reader experience on GitHub Pages. Use this exact HTML (copy-paste, filling in
the filenames and chapter labels):

```html


---

<!-- chapter-nav -->
<div style="display:flex; justify-content:space-between; align-items:center; padding:1em 0;">
  <div><a href="chXX_prev.md">← 第XX章 上一章标题</a></div>
  <div><a href="index.md">↑ 目录</a></div>
  <div><a href="chXX_next.md">第XX章 下一章标题 →</a></div>
</div>
```

**Boundary rules**:
- **First chapter** (ch00 or ch01): left `<div></div>` is **empty** (no prev link).
- **Last chapter**: right `<div></div>` is **empty** (no next link).
- The horizontal rule `---` before the nav separates chapter content from
  navigation visually and semantically.

**Why HTML and not Markdown?** GitHub Pages themes (especially Cayman) render
Markdown links inside `<div>` inconsistently. Raw HTML links are reliable across
all Jekyll themes.

## Conventions that keep the book consistent

- **Language**: translate to Chinese, but keep core technical terms in English on
  first use, `中文 (English)`, for citability. Maintain these mappings in
  `glossary.md` and reuse them verbatim across chapters.
- **Math**: author in the kramdown-safe dialect from the start — every formula in
  `$$...$$`, no single `$`, no bare `|` inside math. See `math-rendering.md`.
  Skipping this means a painful retrofit across the whole book.
- **Code**: fenced ```python blocks, PyTorch-flavored. Math/pipe rules do NOT
  apply inside code fences — kramdown and MathJax both skip them — so a literal
  `$` or `|` in a code sample is fine and should be left as-is.
- **Citations**: reference papers as `[Author et al., Venue, Year]` inline.
- **Filenames**: `docs/chXX_<中文标题>.md`, zero-padded, one chapter per file,
  one agent per file (disjoint ownership prevents clobbering).

## Site assembly files

- `docs/index.md` — course homepage: overview, chapter table, paper list.
- `docs/_sidebar.md` — ordered chapter navigation.
- `docs/glossary.md` — 中英术语对照表, the terminology source of truth.
- `docs/_config.yml` — Jekyll config (see `math-rendering.md` §2 for the math part).
- `docs/_includes/head-custom.html` — MathJax 3 loader (see `math-rendering.md` §6).
