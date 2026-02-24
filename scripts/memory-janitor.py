#!/usr/bin/env python3
"""
memory-janitor.py — Auto-archive expired P1/P2 entries from MEMORY.md

Run daily at 4 AM UTC via launchd.

Priority TTLs:
  P0 = never expires
  P1 = 90 days
  P2 = 30 days

Usage:
  python3 memory-janitor.py             # Execute
  python3 memory-janitor.py --dry-run   # Report only, no changes
"""

import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Configure these paths for your setup
MEMORY_PATH = Path(os.environ.get("MEMORY_PATH", os.path.expanduser("~/MEMORY.md")))
ARCHIVE_DIR = Path(os.environ.get("ARCHIVE_DIR", os.path.expanduser("~/memory/archive")))
MAX_LINES = 150

TTL_DAYS = {
    "P1": 90,
    "P2": 30,
}

# Match lines like: - [P1][2026-02-05] some text
PRIORITY_RE = re.compile(r"^(\s*-\s+)\[(P[12])\]\[(\d{4}-\d{2}-\d{2})\]\s*(.*)")

def main():
    dry_run = "--dry-run" in sys.argv
    now = datetime.utcnow()
    
    if not MEMORY_PATH.exists():
        print(f"❌ MEMORY.md not found at {MEMORY_PATH}")
        return 1

    lines = MEMORY_PATH.read_text().splitlines(keepends=True)
    
    kept = []
    expired = []
    
    for line in lines:
        m = PRIORITY_RE.match(line.rstrip("\n"))
        if m:
            prefix, priority, date_str, content = m.groups()
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                ttl = TTL_DAYS.get(priority, 90)
                age_days = (now - entry_date).days
                
                if age_days > ttl:
                    expired.append({
                        "priority": priority,
                        "date": date_str,
                        "content": content,
                        "age_days": age_days,
                        "ttl": ttl,
                        "raw": line,
                    })
                    continue
            except ValueError:
                pass  # Bad date format, keep the line
        
        kept.append(line)
    
    # Report
    print(f"📋 Memory Janitor — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Results:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Expired: {len(expired)}")
    print(f"  Kept: {len(kept)}")
    
    if expired:
        print(f"\n🗑️ Expired entries:")
        for e in expired:
            print(f"  [{e['priority']}][{e['date']}] ({e['age_days']}d > {e['ttl']}d TTL) {e['content'][:60]}")
    
    # Line count check
    kept_count = len([l for l in kept if l.strip()])
    if kept_count > MAX_LINES:
        print(f"\n⚠️ WARNING: MEMORY.md has {kept_count} non-empty lines (limit: {MAX_LINES})")
    
    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return 0
    
    if not expired:
        print("\n✅ Nothing to archive.")
        return 0
    
    # Backup before modifying
    backup_path = MEMORY_PATH.with_suffix(".md.bak")
    shutil.copy2(MEMORY_PATH, backup_path)
    print(f"\n💾 Backup: {backup_path}")
    
    # Archive expired entries
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_file = ARCHIVE_DIR / f"expired-{now.strftime('%Y-%m')}.md"
    
    with open(archive_file, "a") as f:
        f.write(f"\n## Archived {now.strftime('%Y-%m-%d')} by memory-janitor\n")
        for e in expired:
            f.write(e["raw"] if e["raw"].endswith("\n") else e["raw"] + "\n")
    
    print(f"📦 Archived to: {archive_file}")
    
    # Write back
    MEMORY_PATH.write_text("".join(kept))
    print(f"✅ MEMORY.md updated ({len(lines)} → {len(kept)} lines)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
