#!/usr/bin/env python3
"""
Single-run script to add mission-aligned license headers to all Python files.
This ensures one clean commit instead of hundreds of individual file commits.

Usage:
    python3 add_license_headers.py

This will:
1. Scan all .py files in the project
2. Skip files that already have the header
3. Skip vendor/library files (alphawolf/layer/python/*)
4. Add the standardized header to the top of each file
5. Report what was changed

After running, review changes and commit once:
    git add .
    git commit -m "Add mission-aligned license headers to all Python files"
"""

import os
import sys
from pathlib import Path

# The standardized license header
LICENSE_HEADER = """# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com

"""

# Signature to detect if header already exists
HEADER_SIGNATURE = "© 2025 The Christman AI Project. All rights reserved."

# Directories to skip (vendor code, dependencies)
SKIP_DIRS = [
    'alphawolf/layer/python',  # AWS Lambda layer dependencies
    '__pycache__',
    '.git',
    'node_modules',
    'venv',
    'env',
    '.venv',
    'attached_assets/vosk-model-small-en-us-0.15',  # Third-party model
]

# Files already updated (skip these)
ALREADY_UPDATED = {
    'app.py',
    'alphawolf_brain.py',
    'derek_controller.py',
    'models.py',
    'memory_lane_api.py',
    'extensions.py',
    'core/memory_engine.py',
    'core/conversation_engine.py',
    'services/polly_tts_engine.py',
    'services/tts_engine.py',
    'add_license_headers.py',  # Don't update self
}


def should_skip_file(filepath: Path, project_root: Path) -> bool:
    """Determine if a file should be skipped."""
    rel_path = str(filepath.relative_to(project_root))
    
    # Check if already updated
    if rel_path in ALREADY_UPDATED:
        return True
    
    # Check if in skip directories
    for skip_dir in SKIP_DIRS:
        if skip_dir in rel_path:
            return True
    
    return False


def has_header(content: str) -> bool:
    """Check if file already has the license header."""
    return HEADER_SIGNATURE in content


def add_header_to_file(filepath: Path) -> bool:
    """
    Add license header to a Python file.
    Returns True if file was modified, False otherwise.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Skip if already has header
        if has_header(original_content):
            return False
        
        # Handle shebang (#!/usr/bin/env python3) if present
        lines = original_content.split('\n')
        new_content = []
        
        # Preserve shebang at the very top
        if lines and lines[0].startswith('#!'):
            new_content.append(lines[0])
            new_content.append('')
            remaining = '\n'.join(lines[1:])
        else:
            remaining = original_content
        
        # Add license header
        new_content.append(LICENSE_HEADER.rstrip())
        
        # Add original content
        if remaining.strip():
            new_content.append(remaining)
        
        final_content = '\n'.join(new_content)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Main execution."""
    project_root = Path(__file__).parent
    print(f"🐺 AlphaWolf License Header Updater")
    print(f"📁 Project root: {project_root}")
    print(f"=" * 70)
    print()
    
    # Find all Python files
    python_files = list(project_root.rglob('*.py'))
    print(f"📊 Found {len(python_files)} total Python files")
    print()
    
    # Process files
    updated_count = 0
    skipped_count = 0
    already_has_header = 0
    
    for filepath in sorted(python_files):
        rel_path = filepath.relative_to(project_root)
        
        # Skip vendor/dependency files
        if should_skip_file(filepath, project_root):
            skipped_count += 1
            continue
        
        # Check if already has header
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if has_header(f.read()):
                    already_has_header += 1
                    print(f"  ✓ Already protected: {rel_path}")
                    continue
        except:
            pass
        
        # Add header
        if add_header_to_file(filepath):
            updated_count += 1
            print(f"  ✅ Updated: {rel_path}")
        else:
            print(f"  ⏭️  Skipped: {rel_path}")
    
    # Summary
    print()
    print(f"=" * 70)
    print(f"📊 Summary:")
    print(f"  ✅ Updated: {updated_count} files")
    print(f"  ✓ Already protected: {already_has_header} files")
    print(f"  ⏭️  Skipped (vendor/deps): {skipped_count} files")
    print(f"  📦 Total processed: {len(python_files)} files")
    print()
    
    if updated_count > 0:
        print(f"🎉 Successfully added license headers to {updated_count} files!")
        print()
        print(f"📝 Next steps:")
        print(f"  1. Review changes: git diff")
        print(f"  2. Stage all: git add .")
        print(f"  3. Commit once: git commit -m 'Add mission-aligned license headers to all Python files'")
        print(f"  4. Push: git push")
    else:
        print(f"✨ All files already protected!")
    
    print()
    print(f"💙 The Christman AI Project - Mission Protected")


if __name__ == '__main__':
    main()
