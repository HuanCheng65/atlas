# Project: <填项目名>

<!--
This file is the project's constitution: background, long-term goals,
hard constraints, and shared vocabulary. Read by agents at session start
(via CLAUDE.md). Keep it stable — short-term plans go in docs/atlas/ROADMAP.md.

Authoring tip — the session-start hook extracts this file, so write
for extraction: lead each prose section with a self-contained first sentence
(it becomes the headline), and keep Non-goals / Hard constraints /
Working rules as short bullet lists (those are inlined in full — they're
the guardrails). Keep "Current stage" to a single lifecycle word; the live
milestone lives in ROADMAP.md, so don't restate it here or it goes stale.
-->

## Background

<!-- 这个项目要解决什么问题？为什么是现在做？ -->

## Long-term goals

<!-- 一年/几年尺度的目标。可能只有一个，也可能分主目标和次目标。
     和 ROADMAP.md 的区别：这里写"要去哪"，roadmap 写"下一步怎么走"。 -->

## Non-goals

<!-- 显式说明不打算做什么。避免 scope creep，agent 也别瞎建议。 -->

## Hard constraints

<!-- 不可妥协的技术、时间、资源约束。
     例：必须在 H100 上跑通；必须在 SoCC 2026 deadline 前完成 main results。 -->

## Working rules

<!-- Rules in force that no mechanism enforces. A rule belongs here exactly
     when nothing stops the agent from violating it: if a script, hook or
     validator can catch it, write the check instead. One line per rule,
     ending with a link to the record that justifies it. Authored by hand —
     nothing is promoted here automatically. Starts empty.
     Keep it curated and bounded — line count here is a budget, not a log. -->

## Glossary

<!-- 项目内部的术语、缩写。给 agent 的 vocabulary，减少误解。
     例：
     - HSTU = Hierarchical Sequential Transduction Units
     - SLA  = Semi-Local Attention
     - k*   = optimal split-K factor in the cost model
-->

## Collaborators & stakeholders

<!-- 关键合作者、reviewer、用户。包括项目外但相关的人。 -->

## Current stage

<!-- prototype | research | writeup | shipping | maintenance
     当前阶段会影响 agent 的判断（比如 writeup 阶段优先保持 reproducibility）。 -->

## References

<!-- 关键 paper、prior art、benchmark、相关项目链接。
     按需添加，不强求完备。 -->