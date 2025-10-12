#!/usr/bin/env python3
"""
The Christman AI Project - Module Inventory & Integration Analysis
Powered by LumaCognify AI

Analyzes the complete AI family architecture:
- AlphaWolf: ~100 modules (Cognitive Care & Dementia)
- Derek C: ~133 modules (Autonomous AI Architect)
- AlphaVox: ~144 modules (Nonverbal Communication)
- LumaCognify: ~300+ modules (Foundation Platform)

Total: 677+ modules of ethical AI technology
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

class ChristmanAIInventory:
    """Comprehensive module inventory and analysis for The Christman AI Project."""
    
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.inventory = {
            'alphawolf': [],
            'derek': [],
            'alphavox': [],
            'lumacognify': [],
            'shared': []
        }
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'imports': defaultdict(int),
            'dependencies': defaultdict(set)
        }
    
    def scan_directory(self, directory=None):
        """Scan directory for Python modules."""
        if directory is None:
            directory = self.root_dir
        
        print(f"🔍 Scanning {directory}...")
        
        python_files = list(Path(directory).rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            self._analyze_file(file_path)
        
        return self.inventory
    
    def _should_skip(self, file_path):
        """Check if file should be skipped."""
        skip_patterns = [
            'venv', '__pycache__', '.git', 'node_modules',
            'build', 'dist', '.pytest_cache', '.mypy_cache'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path):
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count lines
            lines = content.count('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            except SyntaxError:
                functions = []
                classes = []
                imports = []
            
            # Determine project
            project = self._determine_project(file_path, content)
            
            # Create module info
            module_info = {
                'path': str(file_path.relative_to(self.root_dir)),
                'name': file_path.stem,
                'lines': lines,
                'functions': len(functions),
                'classes': len(classes),
                'imports': len(imports),
                'size_kb': file_path.stat().st_size / 1024,
                'project': project
            }
            
            # Extract docstring for purpose
            if content.strip().startswith('"""') or content.strip().startswith("'''"):
                docstring = content.split('"""')[1] if '"""' in content else content.split("'''")[1]
                module_info['purpose'] = docstring.split('\n')[0][:100]
            
            # Add to inventory
            self.inventory[project].append(module_info)
            
            # Update stats
            self.stats['total_files'] += 1
            self.stats['total_lines'] += lines
            self.stats['total_functions'] += len(functions)
            self.stats['total_classes'] += len(classes)
            
            # Track imports
            for imp in imports:
                if isinstance(imp, ast.ImportFrom) and imp.module:
                    self.stats['imports'][imp.module] += 1
            
        except Exception as e:
            print(f"  ⚠️  Error analyzing {file_path}: {e}")
    
    def _determine_project(self, file_path, content):
        """Determine which project a file belongs to."""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # Check path and content for project indicators
        if 'alphawolf' in path_str or 'alphawolf' in content_lower[:500]:
            return 'alphawolf'
        elif 'derek' in path_str or 'derek' in content_lower[:500]:
            return 'derek'
        elif 'alphavox' in path_str or 'alphavox' in content_lower[:500]:
            return 'alphavox'
        elif 'lumacognify' in path_str or 'lumacognify' in content_lower[:500]:
            return 'lumacognify'
        else:
            return 'shared'
    
    def generate_report(self):
        """Generate comprehensive inventory report."""
        report = []
        
        report.append("╔══════════════════════════════════════════════════════════════════════════╗")
        report.append("║                                                                          ║")
        report.append("║              THE CHRISTMAN AI PROJECT - MODULE INVENTORY                 ║")
        report.append("║                    Powered by LumaCognify AI                             ║")
        report.append("║                                                                          ║")
        report.append("╚══════════════════════════════════════════════════════════════════════════╝")
        report.append("")
        report.append(f"📊 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("="*76)
        report.append("PROJECT BREAKDOWN")
        report.append("="*76)
        report.append("")
        
        # Project summaries
        projects = {
            'alphawolf': '🐺 AlphaWolf - Cognitive Care & Dementia Support',
            'derek': '🤖 Derek C - Autonomous AI Architect',
            'alphavox': '🗣️  AlphaVox - Nonverbal Communication',
            'lumacognify': '🌟 LumaCognify - Foundation Platform',
            'shared': '🔗 Shared/Core Components'
        }
        
        total_modules = 0
        
        for project_key, project_name in projects.items():
            modules = self.inventory[project_key]
            count = len(modules)
            total_modules += count
            
            if count == 0:
                continue
            
            total_lines = sum(m['lines'] for m in modules)
            total_functions = sum(m['functions'] for m in modules)
            total_classes = sum(m['classes'] for m in modules)
            
            report.append(f"{project_name}")
            report.append(f"  Modules:   {count:>6}")
            report.append(f"  Lines:     {total_lines:>6,}")
            report.append(f"  Functions: {total_functions:>6}")
            report.append(f"  Classes:   {total_classes:>6}")
            report.append("")
        
        report.append("="*76)
        report.append("OVERALL STATISTICS")
        report.append("="*76)
        report.append("")
        report.append(f"Total Modules:      {total_modules:>6}")
        report.append(f"Total Lines of Code: {self.stats['total_lines']:>6,}")
        report.append(f"Total Functions:    {self.stats['total_functions']:>6,}")
        report.append(f"Total Classes:      {self.stats['total_classes']:>6,}")
        report.append("")
        
        # Top imports
        if self.stats['imports']:
            report.append("="*76)
            report.append("TOP DEPENDENCIES")
            report.append("="*76)
            report.append("")
            
            sorted_imports = sorted(self.stats['imports'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
            
            for module, count in sorted_imports:
                report.append(f"  {module:<40} {count:>4} imports")
            report.append("")
        
        # Module complexity analysis
        report.append("="*76)
        report.append("COMPLEXITY ANALYSIS")
        report.append("="*76)
        report.append("")
        
        all_modules = []
        for modules in self.inventory.values():
            all_modules.extend(modules)
        
        if all_modules:
            # Largest modules
            largest = sorted(all_modules, key=lambda x: x['lines'], reverse=True)[:5]
            report.append("📏 Largest Modules (by lines):")
            for i, mod in enumerate(largest, 1):
                report.append(f"  {i}. {mod['path']:<50} {mod['lines']:>5} lines")
            report.append("")
            
            # Most complex (by functions)
            complex_modules = sorted(all_modules, key=lambda x: x['functions'], reverse=True)[:5]
            report.append("🧩 Most Complex Modules (by functions):")
            for i, mod in enumerate(complex_modules, 1):
                report.append(f"  {i}. {mod['path']:<50} {mod['functions']:>3} functions")
            report.append("")
        
        # Integration opportunities
        report.append("="*76)
        report.append("INTEGRATION OPPORTUNITIES")
        report.append("="*76)
        report.append("")
        report.append("🔗 Recommended Integration Points:")
        report.append("")
        report.append("  1. Unified Memory System")
        report.append("     - Consolidate memory_engine implementations")
        report.append("     - Share context across AlphaWolf, Derek, and AlphaVox")
        report.append("")
        report.append("  2. Shared NLP Pipeline")
        report.append("     - Common conversation engine for all projects")
        report.append("     - Unified intent recognition")
        report.append("")
        report.append("  3. Cross-Project Learning")
        report.append("     - Derek learns from AlphaVox interactions")
        report.append("     - AlphaWolf benefits from Derek's research")
        report.append("")
        report.append("  4. Unified Authentication & User Management")
        report.append("     - Single sign-on across all platforms")
        report.append("     - Shared user profiles and preferences")
        report.append("")
        
        # Footer
        report.append("="*76)
        report.append("")
        report.append("💙 'How can we help you love yourself more?'")
        report.append("🚀 The Christman AI Project - AI from the margins, for the world")
        report.append("")
        
        return "\n".join(report)
    
    def export_json(self, output_file="christman_ai_inventory.json"):
        """Export inventory as JSON."""
        output = {
            'generated': datetime.now().isoformat(),
            'project': 'The Christman AI Project',
            'inventory': self.inventory,
            'statistics': {
                'total_files': self.stats['total_files'],
                'total_lines': self.stats['total_lines'],
                'total_functions': self.stats['total_functions'],
                'total_classes': self.stats['total_classes'],
            },
            'top_dependencies': dict(sorted(
                self.stats['imports'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:20])
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"📄 Inventory exported to {output_file}")
    
    def find_duplicates(self):
        """Find potential duplicate functionality."""
        print("\n🔍 Analyzing for duplicate functionality...")
        
        # Group by similar names
        name_groups = defaultdict(list)
        
        for project, modules in self.inventory.items():
            for module in modules:
                # Normalize name
                base_name = module['name'].lower()
                base_name = re.sub(r'(_engine|_service|_module|_handler)$', '', base_name)
                name_groups[base_name].append({
                    'project': project,
                    'path': module['path'],
                    'name': module['name']
                })
        
        duplicates = {k: v for k, v in name_groups.items() if len(v) > 1}
        
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} potential duplicates:")
            for base_name, instances in list(duplicates.items())[:10]:
                print(f"\n  📦 {base_name}:")
                for inst in instances:
                    print(f"     - {inst['project']}: {inst['path']}")
        else:
            print("✅ No obvious duplicates found")
        
        return duplicates


def main():
    """Run the inventory analysis."""
    print("="*76)
    print("THE CHRISTMAN AI PROJECT - MODULE INVENTORY SYSTEM")
    print("="*76)
    print()
    
    inventory = ChristmanAIInventory()
    
    # Scan current directory
    inventory.scan_directory()
    
    # Generate report
    print()
    report = inventory.generate_report()
    print(report)
    
    # Export JSON
    inventory.export_json()
    
    # Find duplicates
    duplicates = inventory.find_duplicates()
    
    # Save report to file
    with open('CHRISTMAN_AI_INVENTORY.txt', 'w') as f:
        f.write(report)
    
    print()
    print("="*76)
    print("✅ Inventory complete!")
    print(f"📊 Report saved to: CHRISTMAN_AI_INVENTORY.txt")
    print(f"📄 JSON data saved to: christman_ai_inventory.json")
    print("="*76)


if __name__ == "__main__":
    main()
