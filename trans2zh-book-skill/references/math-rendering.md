# GitHub Pages Math Rendering: The Complete Minefield

This is the authoritative reference for getting LaTeX math to render on a Jekyll /
GitHub Pages site. Every item here was diagnosed by rendering real content with
the exact kramdown engine GitHub Pages runs — not guessed. Read it before writing
formula-heavy chapters; it is far cheaper to author correctly than to fix later.

## Table of contents
1. How the pipeline actually works (and where it breaks)
2. Root cause #1: the markdown engine config
3. Root cause #2: kramdown only recognizes `$$`
4. Root cause #3: bare `|` inside math → phantom tables
5. Edge cases: currency, prose pipes, backtick-quotes, multi-line blocks
6. The MathJax 3 head include
7. Verifying locally without root / full Jekyll
8. Why each fix is what it is

## 1. How the pipeline actually works

```
your .md  ──kramdown(GFM)──▶  HTML with \(...\) / \[...\]  ──MathJax 3 (browser)──▶  rendered math
```

Two independent processors touch your math, and either can corrupt it:
- **kramdown** runs at build time on GitHub's servers. It parses Markdown,
  including math, BEFORE MathJax ever sees the page.
- **MathJax 3** runs in the browser, scanning the final HTML for `\(...\)` and
  `\[...\]` (and optionally `$...$`) delimiters.

The trap: if kramdown doesn't *recognize* a span as math, it treats the LaTeX as
ordinary Markdown and mangles it (underscores → italics, pipes → table cells).
By the time MathJax runs, the formula is already destroyed. So the goal is to
write math that kramdown reliably recognizes and passes through untouched.

## 2. Root cause #1: the markdown engine config

GitHub Pages accepts only two markdown processors: `kramdown` and `CommonMark`.
A value like `markdown: GFM` is **invalid** — Jekyll silently falls back to
default kramdown, so you think you changed something but didn't.

Correct `_config.yml`:
```yaml
markdown: kramdown
kramdown:
  input: GFM
  math_engine: mathjax
```

- `input: GFM` gives you GitHub-flavored Markdown (fenced code, tables, etc.)
  while keeping kramdown's math handling.
- `math_engine: mathjax` (the default on kramdown ≥ 2.3, which GitHub Pages uses)
  converts `$$...$$` into `\(...\)` for inline math and `\[...\]` for display
  math — exactly the delimiters MathJax 3 reads natively.
- **Do NOT set `math_engine: nil`.** Intuitively "nil = leave my math alone," but
  in practice kramdown wraps nil-engine math in a `<pre>` block, and MathJax's
  default `skipHtmlTags` includes `pre` — so the math silently never renders.
  There's also a Jekyll bug where YAML `nil` is read as the string `"nil"`.

Historical note: kramdown ≤ 2.1 emitted `<script type="math/tex">` tags, which
MathJax **2** consumed but MathJax **3** ignores. If you're on an old stack and
see raw-looking math, that mismatch is why — upgrade to MathJax 3 + kramdown ≥ 2.3.

## 3. Root cause #2: kramdown only recognizes `$$`

kramdown's math delimiter is **double dollar** `$$`, used for BOTH inline and
display. It does **not** treat single `$` as math at all.

So `$\mathbf{x}_i$` is, to kramdown, ordinary text containing underscores — and
in GFM, `}_i ... }_j` underscores flank into emphasis. Real example from a
robotics book, rendered through GitHub's kramdown:

```
source:   $[\omega]_{3,2}, [\omega]_{1,3}$
kramdown: [\omega]<em>{3,2}, [\omega]</em>{1,3}      ← subscripts destroyed
```

MathJax then receives `[\omega]<em>{3,2}` and renders garbage. This pattern
(`]_{...}`, `}_{...}` subscripts) is everywhere in technical writing, so single-`$`
math breaks pervasively, not occasionally.

**Fix:** use `$$...$$` for every formula, inline and display. kramdown treats the
content as opaque math and emits clean `\(...\)` / `\[...\]`:

```
source:   $$[\omega]_{3,2}, [\omega]_{1,3}$$
kramdown: \([\omega]_{3,2}, [\omega]_{1,3}\)         ← intact, MathJax renders it
```

Inline vs display is decided by position, not delimiter: a `$$...$$` span sharing
a line with text → inline `\(...\)`; a `$$...$$` that is its own paragraph (or a
multi-line block) → display `\[...\]`. This is exactly what you want.

Run `scripts/promote_inline_math.py` to convert an existing book. It protects
existing `$$`, skips fenced code blocks, and asserts even single-`$` parity per
segment so a stray literal `$` can't silently mispair the whole file.

## 4. Root cause #3: bare `|` inside math → phantom tables

This one is subtle and brutal. kramdown's GFM parser treats **any line containing
a `|`** as a table row — even a plain prose sentence. If a `|` lives inside an
*inline* math span, the line gets split into table cells, tearing the `$$...$$`
pair apart.

```
source:   不确定性 $$\mathbf{P}_{t|t-1}$$ 源于两项。
renders:  <table><tr><td>不确定性 $$\mathbf{P}_{t</td><td>t-1}$$ 源于两项。</td></tr></table>
```

Two empirically-confirmed nuances:
- A **standalone display block** (`$$...$$` alone on its line, or a multi-line
  `$$ ... $$` block) is parsed as math *before* table detection, so a `|` inside
  it is safe. Only inline math (sharing a line with text) and table-cell math
  break.
- A backslash-escaped pipe `\|` is treated by kramdown as an *escaped* pipe, so
  it does NOT trigger a table. That's why norm bars `\|x\|` happen to survive.

**Fix:** never put a bare `|` inside math. Replace by meaning — all of these
render identically to `|` in MathJax but contain no pipe character:

| Intent | Bare (breaks) | Use |
|---|---|---|
| conditional / "given" | `P(x\|y)` | `P(x \mid y)` |
| absolute value | `\|x\|` | `\lvert x \rvert` |
| norm | `\|x\|` | `\lVert x \rVert` |
| cardinality | `\|S\|` | `\lvert S \rvert` |
| sized delimiter | `\left\|...\right\|` | `\left\lvert...\right\rvert` |

`scripts/fix_math_pipes.py` automates the safe, universal version: it replaces
every bare `|` inside math with `\vert` (which renders as `|`), correctly turning
`\left|` into `\left\vert` and leaving `\|` (norm) untouched. `\vert` is the
faithful "looks identical" choice; switch to `\mid`/`\lvert` by hand where the
spacing matters semantically.

## 5. Edge cases

- **Currency `$`** — a literal `$10` in prose can start a phantom math span (with
  MathJax's single-`$` inline enabled) or mispair during conversion. Escape it:
  `\$10`. In a table cell, `\$` stays literal and won't pair across cells.
- **Literal `|` in prose/titles** — e.g. a bold heading `**Model | Author 2026**`
  becomes a phantom 1-row table. Escape as `\\|` (renders as `|`, no table).
- **Backtick-quotes in math** — LaTeX open-quotes `` `` `` inside `$$\text{``x''}$$`
  are safe once wrapped in `$$` (kramdown treats math content as opaque). They are
  NOT safe in single-`$`, another reason to use `$$`.
- **Multi-line display blocks** — `$$\begin{aligned}...\\...\end{aligned}$$`
  spanning several source lines render as one `\[...\]`. The `\\` line breaks and
  `|` inside are safe here. Don't "fix" pipes in these unless a tool does it
  uniformly (harmless, since `\vert` renders identically).

## 6. The MathJax 3 head include

Most GitHub Pages themes (e.g. Cayman) include `_includes/head-custom.html` in
their `<head>`. Add MathJax 3 there:

```html
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true
  }
};
</script>
<script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
```

The config script must come *before* the async loader (the loader reads the
global `MathJax` object). Because kramdown converts all `$$` to `\(`/`\[`, MathJax
mostly sees those; the `$`/`$$` entries are harmless fallbacks. `processEscapes`
makes `\$` render as a literal dollar. Leave `<pre>`/`<code>` in MathJax's default
`skipHtmlTags` so currency in code samples isn't treated as math.

## 7. Verifying locally without root / full Jekyll

You typically can't build full Jekyll on a locked-down box: no root → no
`ruby.h` → native gems (`eventmachine`, `ffi`, `commonmarker`, `sass-embedded`)
fail to compile, and `github-pages` pulls all of them. You don't need them. The
only thing that can go wrong is the math conversion, and that lives entirely in
pure-Ruby kramdown:

```bash
GEM_HOME=/tmp/ghp-gems gem install --no-document 'kramdown:2.4.0' kramdown-parser-gfm rexml
cd docs
GEM_HOME=/tmp/ghp-gems ruby /path/to/scripts/verify_math_kramdown.rb
```

The verifier renders each chapter with `input: GFM` (same as GitHub Pages) and
reports, per file and in total:
- **leaked `$`** outside code → a span kramdown didn't recognize as math
  (expect 0, except intentional escaped currency),
- **`<em>`/`<strong>` inside `\(...\)`/`\[...\]`** → emphasis corruption (expect 0),
- **headerless `<table>`** → a phantom table from a stray `|` (expect 0).

This catches every failure mode in this document in seconds, before you push.

## 8. Why each fix is what it is (so you can adapt)

- We use `$$` everywhere rather than switching engines because CommonMark (the
  only other GitHub Pages option) *also* processes emphasis and, worse, eats
  `\\` and `\{` in display math. kramdown + `$$` is the one combination that
  protects both inline and display content.
- We prefer `\vert`/`\mid` over escaping pipes as `\|` inside math because `\|`
  means "norm" in LaTeX — overloading it would change rendering. Named macros
  remove the pipe character without changing meaning.
- We verify with real kramdown, not a regex or our editor's preview, because the
  whole problem is that kramdown's parsing differs from what you'd assume. The
  only trustworthy oracle is the engine itself.
