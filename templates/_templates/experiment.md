---
id: {{ID}}
# Title rules:
#   - Title states what's being tested as a claim or comparison. "Does X improve Y?" / "X vs Y on Z" — not just "X experiment".
#   - Self-contained: readable from the index alone.
title: {{TITLE}}
date: {{DATE}}
status: planned
tags: []
related: []
source-journal: null
# The four content fields below are ONE-LINE machine summaries, for scanning
# entities without loading bodies. The body sections own the full prose — never
# the reverse. validate.py rejects any value here over 300 chars, and rejects
# bodies that say "见 frontmatter" / "see frontmatter" instead of their content.
hypothesis: null   # one falsifiable sentence
config: {}         # key params only, short scalar values
result: {}         # key numbers only
artifacts: []
conclusion: null   # one- or two-sentence verdict
---

# {{TITLE}}

## Hypothesis
<!-- ONE SENTENCE, falsifiable, self-contained. This sentence gets pulled into the orient summary. -->

## Setup
<!-- 数据集、对照组、关键超参 -->

## Run log
<!-- 实验过程的关键事件，按日期 -->

## Result
<!-- 关键数字、图表链接、原始 artifact 路径 -->

## Conclusion
<!-- 主张是否验证、下一步。完整写出 —— 正文是正本，不许用一句指针把读者指回上方的字段 -->