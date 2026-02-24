# AI Agent Memory Management System

A file-based memory system for AI Agents with automatic TTL, LLM compression, and multi-agent sharing.

## Why File System?

| Solution | Complexity | Cost | Debuggability |
|----------|------------|------|---------------|
| Mem0 | High | Paid | Black box |
| Vector DB | High | Medium | Need tools |
| This | Low | Free | Open files directly |

Vector databases are great for large-scale semantic search. But for personal AI agents with hundreds of memories, file system is simpler, cheaper, and easier to debug.

## Quick Start

### 1. Basic Setup (Minimum Viable)

```
MEMORY.md              ← Long-term memory (read on every startup)
memory/YYYY-MM-DD.md   ← Daily logs (raw material)
SESSION-STATE.md       ← Work buffer (survives compression)
```

Copy `templates/MEMORY.md` and start using it.

### 2. Add Automation

```bash
# Run daily at 4 AM
python3 scripts/memory-janitor.py

# Options
python3 scripts/memory-janitor.py --dry-run  # Test without changes
```

### 3. Multi-Agent Sharing (Optional)

```
shared/
├── MEMORY.md       # Shared memory (all agents read/write)
├── SOUL-BASE.md    # Shared principles
└── lessons/        # Shared lessons
```

## Core Concepts

### P0/P1/P2 Priority + TTL

```markdown
- [P0] Timezone: US Eastern    ← Never expires
- [P1][2026-02-24] Current project ← Expires in 90 days
- [P2][2026-02-24] Temp note   ← Expires in 30 days
```

### L0/L1/L2 Hierarchy

| Layer | Location | Content | When to Read |
|-------|----------|---------|--------------|
| L0 | .abstract | Directory overview | Always first |
| L1 | insights/, lessons/ | Distilled patterns | On demand |
| L2 | YYYY-MM-DD.md | Full daily logs | Deep dive only |

90% of queries need only L0 + L1. Saves tokens.

### Q1/Q2/Q3 Decision Framework

Before writing to MEMORY.md, ask:

- **Q1:** Will I make mistakes if I don't see this next time? → P0
- **Q2:** Might I need to look this up someday? → P1
- **Q3:** Neither? → Keep in daily log, not MEMORY.md

## Files

```
├── scripts/
│   ├── memory-janitor.py       # TTL auto-cleanup
│   ├── memory-compounding.py   # Logs → Insights
│   └── memory-abstract-gen.py  # Generate .abstract files
├── templates/
│   ├── MEMORY.md               # Memory template
│   ├── SOUL-BASE.md            # Shared principles template
│   └── lessons/                # Lessons structure
├── SKILL.md                    # Q1/Q2/Q3 decision framework
└── README.md
```

## Scripts

### memory-janitor.py

Runs daily, does 3 things:
1. Scan P1/P2 entries in MEMORY.md
2. Move expired entries to archive/
3. Warn if MEMORY.md exceeds 150 lines

### memory-compounding.py

Inspired by Stanford Generative Agents "reflection":
- Read recent daily logs
- LLM extracts patterns
- Write to insights/YYYY-MM.md

Logs can be deleted, insights stay.

## Credits

- [Stanford Generative Agents](https://arxiv.org/abs/2304.03442) - Reflection mechanism
- [OpenViking (ByteDance)](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/OpenViking) - L0/L1/L2 hierarchy
- [@lijiuer92](https://x.com/lijiuer92) - Memory deep dive

## Author

Open source contribution. Feel free to fork and improve.
