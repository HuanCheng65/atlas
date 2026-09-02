---
id: 40
title: A PostToolUse hook may only report what that tool call changed
date: 2026-09-03
type: memory
tags: [hooks, agent-behavior]
---

# A PostToolUse hook may only report what that tool call changed

The channel says "what you just did caused this". Anything else it reports is
an accusation the reader cannot check, aimed at whoever happened to type a
command. Two rules follow, and both were learned by breaking them
([[039-store-validated-by-a-post-write-hook]]):

**A state found is not a state caused.** Compare against a baseline recorded
at session start, and when there is no baseline, record one and stay silent.
Treating "unknown" as "changed" makes the first tool call in every project
report whatever was already wrong.

**Report only conditions of this channel.** A store in an older format is a
condition of the project; session start says so once, in words that fit it.
Repeating it from a write hook attaches it to an unrelated command and drags
along a paragraph about links that has nothing to do with the problem.

Observed on a project whose store was still v1: typing `hi` produced a
blocking hook error about link resolution.
