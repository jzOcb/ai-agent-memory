---
name: memory-management
version: 1.0.0
description: |
  Guidelines for managing AI agent memory. Use when deciding what to write
  to MEMORY.md, how to organize memory files, or when reviewing memory health.
  Includes Q1/Q2/Q3 decision framework and common mistakes to avoid.
allowed-tools:
  - Read
  - Write
  - Edit
  - exec
---

# Memory Management

## Q1/Q2/Q3 判断流程

每次要记录信息时，问自己三个问题：

```
Q1: 下次醒来不看这条，会做错事吗？
    → Yes: MEMORY.md [P0]

Q2: 某天可能需要查这条吗？
    → Yes: memory/archive/ [P1]

Q3: 以上都不是？
    → 留在 daily log，不处理
```

### 对应 Priority 标签

| 判断 | Priority | TTL | 位置 |
|------|----------|-----|------|
| Q1=Yes | `[P0]` | 永不过期 | MEMORY.md |
| Q2=Yes | `[P1][YYYY-MM-DD]` | 90天 | MEMORY.md → archive |
| Q3 | `[P2][YYYY-MM-DD]` | 30天 | MEMORY.md → archive |

### 例子

| 信息 | Q1 | Q2 | 去向 |
|------|----|----|------|
| "用户时区是 US Eastern" | ✅ | - | MEMORY.md [P0] |
| "2月8日买反了方向" | ❌ | ✅ | archive [P1] |
| "今天跑了扫描" | ❌ | ❌ | daily log |

## 硬性限制

```
MEMORY.md ≤ 150 行 — 硬约束，不是建议
AGENTS.md ≤ 200 行 — 同样是硬约束
```

超过就必须精简，没有例外。

## 常见误区

### ❌ 热记忆误区 (MEMORY.md)

**把项目细节写进热记忆**
```
例: "项目X客户叫王总，电话138-xxxx"
问题: 项目结束后这条就没用了
```

**把每日任务写进热记忆**
```
例: "今天要写完xxx功能"
问题: 一次性的，不该沉淀
```

**把所有教训都塞进热记忆**
```
例: "今天学到了xxx"
问题: 不是每条都值得，等复盘再决定
```

**把调试过程写进热记忆**
```
例: "试了A方案不行，换B方案"
问题: 这是过程，不是结论
```

### ❌ 冷记忆误区 (archive)

**归档后从来不查**
```
问题: 归档是为了能查到，不查就没意义
解决: 用 memory_search 召回
```

**标题写得不清楚**
```
❌ "2026-02.md"
✅ "2026-02 交易教训和决策"
```

### ❌ 日志误区 (daily log)

**当天就删日志**
```
问题: 日志是保命用的，出问题要回放
```

**日志写太详细（小作文）**
```
❌ "今天下午2:15分，我和技术顾问讨论了..."
✅ 记关键点就行，不是写日记
```

## 自动化工具

### memory-janitor.py

每日 4 AM UTC 自动运行：
- 检查 P1/P2 条目的 TTL
- 过期条目 → 移到 archive
- 警告无标签条目

```bash
# 手动运行
python3 memory-janitor.py

# 检查状态
python3 memory-janitor.py --dry-run
```

## 写入检查清单

每次写 MEMORY.md 前：

```
□ 跑过 Q1/Q2/Q3 判断
□ 打了 Priority 标签
□ 检查当前行数 (wc -l MEMORY.md)
□ 不是项目细节/每日任务/调试过程
```
