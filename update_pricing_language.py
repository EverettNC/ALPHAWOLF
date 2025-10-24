#!/usr/bin/env python3
"""
Script to update pricing language across all documentation files.
Removes "free" pricing mentions and replaces with professional language.
"""

import os
import re
from pathlib import Path

# Define replacements
REPLACEMENTS = [
    # Direct "free" mentions
    (r'\b[Ff][Rr][Ee][Ee] (download|forever|to everyone|for everyone)\b', r'Available \1'),
    (r'\b[Ff][Rr][Ee][Ee] [Dd]ownload\b', 'Available for deployment'),
    (r'\$0,? not \$\d+', 'Accessible alternative to $8000+ systems'),
    (r'[Cc]osts \$0', 'Enterprise-grade platform'),
    (r'[Tt]otal: \$0', 'Available for licensing'),
    (r'FREE FOREVER', 'AVAILABLE NOW'),
    (r'FREE TO DOWNLOAD', 'READY FOR DEPLOYMENT'),
    (r'Free forever', 'Available now'),
    (r'free forever', 'available now'),
    (r'FREE!', 'Available!'),
    (r'FREE,', 'Enterprise-grade,'),
    (r'- FREE', '- Available'),
    (r'✅ Free', '✅ Available'),
    
    # "Free downloads" mentions
    (r'(\d+[MK]?\+?) free (downloads|users)', r'\1 platform users'),
    (r'free downloads? (available|goal)', r'deployment \1'),
    (r'Public beta \(\d+M free downloads goal\)', 'Public beta deployment program'),
    
    # Business model mentions
    (r'Free-forever business model', 'Sustainable business model'),
    (r'free tier', 'consumer tier'),
    (r'Free consumer', 'Consumer'),
    
    # Keep "freedom" and "hands-free" - these are not pricing mentions
    # These will not be replaced
]

# Files to update (exclude certain files)
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    'node_modules',
    '.venv',
    'venv',
    '.pyc',
    'update_pricing_language.py',  # Don't update self
]

def should_process_file(filepath):
    """Check if file should be processed."""
    path_str = str(filepath)
    
    # Check exclusions
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return False
    
    # Only process certain file types
    valid_extensions = ['.md', '.txt', '.py', '.html', '.sh', '.yml', '.yaml', '.json']
    if filepath.suffix.lower() not in valid_extensions:
        return False
    
    # Don't process binary or very large files
    try:
        if filepath.stat().st_size > 5_000_000:  # 5MB limit
            return False
    except:
        return False
    
    return True

def update_file(filepath):
    """Update a single file with new pricing language."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Apply all replacements
        for pattern, replacement in REPLACEMENTS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                changes_made.append(f"  - Replaced '{pattern}' ({len(matches)} occurrences)")
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Updated: {filepath}")
            for change in changes_made:
                print(change)
            return True
        
        return False
    
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Main execution."""
    print("🔄 Updating pricing language across all files...\n")
    
    root_dir = Path('/workspaces/ALPHAWOLF')
    files_updated = 0
    files_scanned = 0
    
    # Walk through all files
    for filepath in root_dir.rglob('*'):
        if filepath.is_file() and should_process_file(filepath):
            files_scanned += 1
            if update_file(filepath):
                files_updated += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Scan complete!")
    print(f"   Files scanned: {files_scanned}")
    print(f"   Files updated: {files_updated}")
    print(f"{'='*60}\n")
    
    print("Note: Manual review recommended for:")
    print("  - BUSINESS_MODEL_FREEDOM.md (business strategy document)")
    print("  - Marketing copy that needs context-specific rewrites")
    print("  - Files with 'freedom' vs 'free' distinctions")

if __name__ == '__main__':
    main()
