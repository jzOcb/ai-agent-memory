#!/usr/bin/env python3
"""
L0 Abstract Generator for Memory System
Generates .abstract files for memory directories based on content.

Usage:
    python3 memory-abstract-gen.py [--dir PATH] [--force]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configure this path for your setup
MEMORY_ROOT = Path(os.environ.get("MEMORY_ROOT", os.path.expanduser("~/memory")))

def get_file_summary(filepath: Path) -> str:
    """Get a one-line summary of a file."""
    try:
        content = filepath.read_text()
        lines = content.strip().split('\n')
        
        # For markdown, get first heading or first non-empty line
        for line in lines[:10]:
            if line.startswith('# '):
                return line[2:].strip()
            elif line.strip() and not line.startswith('<!--'):
                return line.strip()[:80]
        return f"({len(lines)} lines)"
    except Exception as e:
        return f"(error reading: {e})"

def get_jsonl_summary(filepath: Path) -> str:
    """Get summary of JSONL file."""
    try:
        lines = filepath.read_text().strip().split('\n')
        count = len([l for l in lines if l.strip()])
        
        # Get categories if present
        categories = set()
        for line in lines[:20]:
            if line.strip():
                try:
                    data = json.loads(line)
                    if 'category' in data:
                        categories.add(data['category'])
                except:
                    pass
        
        cat_str = f" ({', '.join(sorted(categories))})" if categories else ""
        return f"{count} entries{cat_str}"
    except Exception as e:
        return f"(error: {e})"

def generate_dir_abstract(dirpath: Path, force: bool = False) -> bool:
    """Generate .abstract for a directory."""
    abstract_path = dirpath / ".abstract"
    
    # Skip if exists and not forcing
    if abstract_path.exists() and not force:
        print(f"  [skip] {dirpath.name}/.abstract exists")
        return False
    
    # Gather directory contents
    files = []
    subdirs = []
    
    for item in sorted(dirpath.iterdir()):
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            subdirs.append(item.name)
        elif item.is_file():
            if item.suffix == '.md':
                files.append(f"- {item.name}: {get_file_summary(item)}")
            elif item.suffix == '.jsonl':
                files.append(f"- {item.name}: {get_jsonl_summary(item)}")
    
    # Generate abstract content
    dir_name = dirpath.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    content = f"""# {dir_name}/ L0 Abstract
<!-- Auto-generated: {timestamp} -->

"""
    
    if files:
        content += "**Files:**\n" + "\n".join(files) + "\n\n"
    
    if subdirs:
        content += "**Subdirectories:** " + ", ".join(subdirs) + "\n"
    
    abstract_path.write_text(content)
    print(f"  [generated] {dirpath.name}/.abstract")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=Path, default=MEMORY_ROOT)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    
    root = args.dir
    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)
    
    print(f"Generating L0 abstracts in {root}")
    
    # Generate for root
    generate_dir_abstract(root, args.force)
    
    # Generate for subdirectories
    for item in root.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            generate_dir_abstract(item, args.force)
    
    print("Done!")

if __name__ == "__main__":
    main()
