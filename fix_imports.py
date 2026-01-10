"""
Auto-fix import statements in all route files
Run from project root: python fix_imports.py
"""
import os
import re
from pathlib import Path

# Define incorrect and correct import patterns
IMPORT_FIXES = [
    # Fix database imports
    (r'^from database import', 'from backend.database import'),
    (r'^import database', 'import backend.database as database'),
    
    # Fix models imports
    (r'^from models import', 'from backend.models import'),
    (r'^import models', 'import backend.models as models'),
    
    # Fix auth imports
    (r'^from auth\.routes import', 'from backend.auth.dependencies import'),
    (r'^from auth import', 'from backend.auth.dependencies import'),
]

# Additional specific fixes
SPECIFIC_FIXES = [
    ('from auth.routes import get_current_user', 'from backend.auth.dependencies import get_current_user'),
    ('Depends(get_current_user)', 'Depends(get_current_user)'),
    ('current = Depends', 'current_user: User = Depends'),
]

def fix_file_imports(file_path):
    """Fix imports in a single file"""
    print(f"\nProcessing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        changes_made = 0
        
        for line in lines:
            fixed_line = line
            
            # Apply regex-based fixes
            for pattern, replacement in IMPORT_FIXES:
                if re.match(pattern, line.strip()):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        print(f"  ✓ Fixed: {line.strip()}")
                        print(f"       → {new_line.strip()}")
                        fixed_line = new_line
                        changes_made += 1
            
            # Apply specific string replacements
            for old, new in SPECIFIC_FIXES:
                if old in fixed_line and old != new:
                    fixed_line = fixed_line.replace(old, new)
            
            fixed_lines.append(fixed_line)
        
        new_content = '\n'.join(fixed_lines)
        
        if new_content != original_content:
            # Create backup
            backup_path = str(file_path) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"  📁 Backup created: {backup_path}")
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ File updated with {changes_made} changes")
            return True
        else:
            print(f"  ℹ️  No changes needed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
        return False


def find_route_files(base_path):
    """Find all routes.py files in backend modules"""
    route_files = []
    backend_path = Path(base_path) / 'backend'
    
    if not backend_path.exists():
        print(f"❌ Backend path not found: {backend_path}")
        return route_files
    
    # Look for routes.py in subdirectories
    for module_dir in backend_path.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('__'):
            routes_file = module_dir / 'routes.py'
            if routes_file.exists():
                route_files.append(routes_file)
    
    return route_files


def main():
    print("=" * 70)
    print("SPMS Import Fixer")
    print("=" * 70)
    print()
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Working directory: {current_dir}")
    print()
    
    # Find all route files
    route_files = find_route_files(current_dir)
    
    if not route_files:
        print("❌ No route files found!")
        print("\nMake sure you're running this from the project root directory.")
        print("Expected structure:")
        print("  project_root/")
        print("  ├── backend/")
        print("  │   ├── households/")
        print("  │   │   └── routes.py")
        print("  │   ├── programmes/")
        print("  │   │   └── routes.py")
        print("  │   └── ...")
        return
    
    print(f"Found {len(route_files)} route file(s):")
    for f in route_files:
        print(f"  - {f.relative_to(current_dir)}")
    print()
    
    # Ask for confirmation
    response = input("Proceed with fixing imports? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print("=" * 70)
    print("Processing files...")
    print("=" * 70)
    
    # Process each file
    fixed_count = 0
    for route_file in route_files:
        if fix_file_imports(route_file):
            fixed_count += 1
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total files processed: {len(route_files)}")
    print(f"Files modified: {fixed_count}")
    print(f"Files unchanged: {len(route_files) - fixed_count}")
    print()
    
    if fixed_count > 0:
        print("✅ Import fixes applied successfully!")
        print()
        print("Next steps:")
        print("1. Review the changes in your files")
        print("2. Restart your server:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        print("3. Check http://localhost:8000/docs")
        print()
        print("📁 Backup files created with .backup extension")
        print("   You can restore them if needed")
    else:
        print("ℹ️  All files are already up to date!")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()