#!/usr/bin/env python3
"""
memory-compounding.py — Memory reflection and insight extraction

基于斯坦福 Generative Agents 的反思机制：
- 琐碎记忆 → LLM 提炼洞察 → 存入 insights/

用法：
    python3 memory-compounding.py                     # 标记昨天
    python3 memory-compounding.py --date 2026-02-05   # 标记指定日期
    python3 memory-compounding.py --list              # 列出待处理
    python3 memory-compounding.py --process           # 处理所有 pending (输出指令)
    python3 memory-compounding.py --extract DATE      # 提取指定日期的洞察

Cron Integration:
    3 AM: memory-compounding.py --mark-pending        # 标记
    4 AM: cron dispatcher triggers sub-agent          # 处理
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys
import re

# Configure this path for your setup
MEMORY_DIR = Path(os.environ.get("MEMORY_DIR", os.path.expanduser("~/memory")))
PENDING_DIR = MEMORY_DIR / ".pending"
INSIGHTS_DIR = MEMORY_DIR / "insights"

# 洞察提取 prompt (基于 Stanford Generative Agents)
REFLECTION_PROMPT = """You are extracting insights from a daily memory log.

## Task
Read the log and extract a STRUCTURED summary with these MANDATORY sections.
Each section MUST be present even if the content is minimal.

## Output Format (ALL sections required)
```markdown
## {DATE} Insights

### Session Intent
[What was the main focus today? 1-2 sentences max]

### Files Modified
[List ALL files that were created/edited/deleted. If none mentioned, write "None recorded"]
- path/to/file: what changed

### Decisions Made
[Important choices with rationale]
- Decision: [what] — Reason: [why]

### Lessons Learned
[Mistakes → fixes, what went wrong and how to avoid]
- **问题**: [what went wrong]
- **原因**: [root cause]
- **修复**: [how to prevent]

### Patterns
[Recurring solutions or workflows that worked]
- **[pattern name]**: [description with concrete example]

### Open Items
[Unfinished tasks, things to follow up]
- [ ] item

### Statistics
- Log length: {chars} chars
- Decisions: N
- Lessons: N
- Files modified: N
```

## Extraction Rules
- Compress 10:1 (1000 chars log → ~100 chars insight)
- Keep [P0] markers for permanent rules
- Include concrete commands/paths/code when mentioned
- Skip trivial chatter, focus on learnings
- Output in the language of the log content
- **Files Modified is CRITICAL** — scan for any path like ~/*, /Users/*, *.py, *.sh, *.md

## Daily Log to Process
{log_content}
"""

def get_yesterday():
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def is_compounded(filepath):
    """Check if file has compounded marker."""
    try:
        content = filepath.read_text()
        return "<!-- compounded" in content
    except:
        return False

def mark_pending(date_str=None):
    """Mark a daily log as pending for LLM processing."""
    date_str = date_str or get_yesterday()
    log_file = MEMORY_DIR / f"{date_str}.md"
    
    print(f"📅 Checking {date_str}...")
    
    if not log_file.exists():
        print(f"❌ 文件不存在: {log_file}")
        return False
    
    if is_compounded(log_file):
        print(f"⏭️ 已处理过")
        return False
    
    content = log_file.read_text()
    if len(content.strip()) < 100:
        print(f"⏭️ 内容太少 ({len(content)} chars)")
        return False
    
    # Check if already pending
    PENDING_DIR.mkdir(exist_ok=True)
    pending_file = PENDING_DIR / f"{date_str}.pending"
    
    if pending_file.exists():
        print(f"⏭️ 已在待处理队列")
        return False
    
    # Create pending marker
    pending_file.write_text(json.dumps({
        "date": date_str,
        "file": str(log_file),
        "chars": len(content),
        "created": datetime.now().isoformat()
    }))
    
    print(f"✅ 标记待处理: {pending_file.name}")
    return True

def list_pending():
    """List all pending files."""
    if not PENDING_DIR.exists():
        return []
    return sorted(PENDING_DIR.glob("*.pending"))

def get_pending_info():
    """Get info about pending files."""
    pending = list_pending()
    result = []
    for p in pending:
        try:
            data = json.loads(p.read_text())
            result.append(data)
        except:
            pass
    return result

def prepare_extraction(date_str):
    """Prepare extraction prompt for a specific date."""
    log_file = MEMORY_DIR / f"{date_str}.md"
    
    if not log_file.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return None
    
    content = log_file.read_text()
    
    # Truncate if too long (keep most recent)
    max_chars = 15000
    if len(content) > max_chars:
        content = f"[...truncated...]\n\n{content[-max_chars:]}"
    
    prompt = REFLECTION_PROMPT.replace("{DATE}", date_str).replace("{log_content}", content)
    return prompt

def save_insights(date_str, insights_text):
    """Save extracted insights to the monthly insights file."""
    INSIGHTS_DIR.mkdir(exist_ok=True)
    
    # Determine monthly file
    month = date_str[:7]  # 2026-02
    insights_file = INSIGHTS_DIR / f"{month}.md"
    
    # Read existing or create header
    if insights_file.exists():
        existing = insights_file.read_text()
    else:
        existing = f"# Insights - {datetime.strptime(month, '%Y-%m').strftime('%B %Y')}\n\n"
    
    # Append new insights
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_content = existing + f"\n{insights_text}\n\n*LLM 提取于 {timestamp}*\n\n---\n"
    
    insights_file.write_text(new_content)
    print(f"✅ 洞察已保存到 {insights_file}")
    return True

def mark_compounded(date_str):
    """Mark a log file as compounded."""
    log_file = MEMORY_DIR / f"{date_str}.md"
    
    if not log_file.exists():
        return False
    
    content = log_file.read_text()
    
    # Add compounded marker at the top
    marker = f"<!-- compounded: {datetime.now().strftime('%Y-%m-%d')} -->\n"
    if not content.startswith("<!--"):
        content = marker + content
    else:
        # Insert after existing front matter
        content = marker + content
    
    log_file.write_text(content)
    
    # Remove pending file
    pending_file = PENDING_DIR / f"{date_str}.pending"
    if pending_file.exists():
        pending_file.unlink()
    
    print(f"✅ 已标记 {date_str} 为已处理")
    return True

def generate_process_instructions():
    """Generate instructions for sub-agent to process pending files."""
    pending = get_pending_info()
    
    if not pending:
        print("📭 无待处理文件")
        return None
    
    print(f"📋 找到 {len(pending)} 个待处理文件:")
    for p in pending:
        print(f"  - {p['date']} ({p['chars']} chars)")
    
    # Generate sub-agent task
    dates = [p['date'] for p in pending]
    task = f"""Memory Reflection Task:

处理以下日期的日志:
{chr(10).join(f'- {d}' for d in dates)}

对每个日期执行:
1. 运行: python3 memory-compounding.py --extract {dates[0]}
2. 根据输出的 prompt 提取洞察 (3-7 条)
3. 将洞察写入 memory/insights/YYYY-MM.md
4. 运行: python3 memory-compounding.py --done {dates[0]}

规则:
- 10:1 压缩比
- 保留 [P0] 标记
- 包含具体命令/代码
- 使用日志的语言 (中/英)
"""
    print("\n" + "="*50)
    print("📤 Sub-agent Task:")
    print("="*50)
    print(task)
    return task

def main():
    parser = argparse.ArgumentParser(description="Memory reflection and insight extraction")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD (默认昨天)")
    parser.add_argument("--list", action="store_true", help="列出待处理文件")
    parser.add_argument("--mark-pending", action="store_true", help="标记待处理 (默认行为)")
    parser.add_argument("--process", action="store_true", help="生成处理指令")
    parser.add_argument("--extract", metavar="DATE", help="输出指定日期的提取 prompt")
    parser.add_argument("--done", metavar="DATE", help="标记指定日期为已处理")
    parser.add_argument("--batch-mark", type=int, metavar="DAYS", help="批量标记过去 N 天")
    args = parser.parse_args()
    
    if args.list:
        pending = list_pending()
        if pending:
            print("📋 待处理文件:")
            for p in pending:
                data = json.loads(p.read_text())
                print(f"  - {data['date']} ({data['chars']} chars)")
        else:
            print("📭 无待处理")
        return
    
    if args.process:
        generate_process_instructions()
        return
    
    if args.extract:
        prompt = prepare_extraction(args.extract)
        if prompt:
            print(prompt)
        return
    
    if args.done:
        mark_compounded(args.done)
        return
    
    if args.batch_mark:
        print(f"📅 批量标记过去 {args.batch_mark} 天...")
        marked = 0
        for i in range(1, args.batch_mark + 1):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if mark_pending(date_str):
                marked += 1
        print(f"\n✅ 标记了 {marked} 个文件")
        return
    
    # Default: mark yesterday (or specified date)
    mark_pending(args.date)

if __name__ == "__main__":
    main()
