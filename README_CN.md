# AI Agent 记忆管理系统

[English](README.md)

基于文件系统的 AI Agent 记忆方案，支持自动 TTL 过期、LLM 压缩、多 Agent 共享。

## 为什么选文件系统？

| 方案 | 复杂度 | 成本 | 可调试性 |
|------|--------|------|----------|
| Mem0 | 高 | 付费 | 黑盒 |
| 向量数据库 | 高 | 中等 | 需要工具 |
| 本方案 | 低 | 免费 | 直接打开文件看 |

向量数据库适合大规模语义搜索。但对于个人 AI Agent（几百条记忆），文件系统更简单、更便宜、更好调试。

## 快速开始

### 1. 基础配置（最小可用）

```
MEMORY.md              ← 长期记忆（每次启动必读）
memory/YYYY-MM-DD.md   ← 每日日志（原始素材）
SESSION-STATE.md       ← 工作缓冲（防压缩丢失）
```

复制 `templates/MEMORY.md` 开始使用。

### 2. 添加自动化

```bash
# 每天 4 AM 运行
python3 scripts/memory-janitor.py

# 选项
python3 scripts/memory-janitor.py --dry-run  # 测试，不修改
```

### 3. 多 Agent 共享（可选）

```
shared/
├── MEMORY.md       # 共享记忆（所有 agent 读写）
├── SOUL-BASE.md    # 共享原则
└── lessons/        # 共享教训
```

## 核心概念

### P0/P1/P2 优先级 + TTL

```markdown
- [P0] 时区：US Eastern    ← 永不过期
- [P1][2026-02-24] 当前项目 ← 90 天后过期
- [P2][2026-02-24] 临时备注 ← 30 天后过期
```

### L0/L1/L2 分层

| 层级 | 位置 | 内容 | 何时读取 |
|------|------|------|----------|
| L0 | .abstract | 目录概览 | 每次先读 |
| L1 | insights/, lessons/ | 提炼的模式 | 按需召回 |
| L2 | YYYY-MM-DD.md | 完整日志 | 深挖时读 |

90% 的查询只需要 L0 + L1，省 token。

### Q1/Q2/Q3 决策框架

写入 MEMORY.md 前，问自己：

- **Q1:** 下次醒来不看这条，会做错事吗？→ P0
- **Q2:** 某天可能需要查这条吗？→ P1
- **Q3:** 以上都不是？→ 留日志，不进 MEMORY.md

## 文件结构

```
├── scripts/
│   ├── memory-janitor.py       # TTL 自动清理
│   ├── memory-compounding.py   # 日志 → 洞察
│   └── memory-abstract-gen.py  # 生成 .abstract 文件
├── templates/
│   ├── MEMORY.md               # 记忆模板
│   ├── SOUL-BASE.md            # 共享原则模板
│   └── lessons/                # 教训结构
├── SKILL.md                    # Q1/Q2/Q3 决策框架
└── README.md
```

## 脚本说明

### memory-janitor.py

每天运行，做 3 件事：
1. 扫描 MEMORY.md 中的 P1/P2 条目
2. 过期的移到 archive/
3. 超过 150 行发警告

### memory-compounding.py

灵感来自斯坦福 Generative Agents 的 "reflection"：
- 读取近期日志
- LLM 提取模式
- 写入 insights/YYYY-MM.md

日志可以删，洞察留下来。

## 参考资料

- [Stanford Generative Agents](https://arxiv.org/abs/2304.03442) - Reflection 机制
- [OpenViking (字节)](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/OpenViking) - L0/L1/L2 分层
- [@lijiuer92](https://x.com/lijiuer92) - Memory 深度分享

## 环境变量配置

```bash
export MEMORY_PATH=~/your-workspace/MEMORY.md
export MEMORY_DIR=~/your-workspace/memory
export ARCHIVE_DIR=~/your-workspace/memory/archive
```
