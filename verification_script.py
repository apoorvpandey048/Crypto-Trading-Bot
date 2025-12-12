"""
Final verification script before GitHub push
Checks for sensitive information in the repository
"""

import os
import re
from pathlib import Path

# Sensitive patterns to check for
SENSITIVE_PATTERNS = {
    'API Keys (real)': r'[A-Za-z0-9]{64,}',  # Long alphanumeric strings (potential API keys)
    'Email addresses': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'IP addresses': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    'Passwords': r'password\s*=\s*["\'][^"\']{6,}["\']',
}

# Files to skip
SKIP_PATTERNS = [
    'venv',
    'node_modules',
    '.git',
    '__pycache__',
    '.db',
    '.log',
    'verification_script.py',  # This file
]

# Extensions to check
CHECK_EXTENSIONS = ['.py', '.js', '.jsx', '.json', '.env', '.md', '.txt']

def should_skip(file_path):
    """Check if file should be skipped"""
    return any(pattern in str(file_path) for pattern in SKIP_PATTERNS)

def is_placeholder(text):
    """Check if detected value is a placeholder"""
    placeholders = [
        'your_',
        'example',
        'test',
        'placeholder',
        'change_this',
        'replace_with',
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
    ]
    return any(placeholder in text.lower() for placeholder in placeholders)

def scan_file(file_path):
    """Scan a file for sensitive information"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    matched_text = match.group(0)
                    
                    # Skip if it's a placeholder
                    if is_placeholder(matched_text):
                        continue
                    
                    # Skip common false positives
                    if pattern_name == 'API Keys (real)':
                        # Skip if it's in a comment or documentation
                        if 'your_' in matched_text or 'example' in matched_text:
                            continue
                    
                    if pattern_name == 'Email addresses':
                        # Skip example emails
                        if 'example.com' in matched_text or 'test.com' in matched_text:
                            continue
                    
                    issues.append({
                        'file': file_path,
                        'type': pattern_name,
                        'value': matched_text,
                        'line': content[:match.start()].count('\n') + 1
                    })
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues

def main():
    """Main verification function"""
    print("=" * 70)
    print("REPOSITORY SECURITY VERIFICATION")
    print("=" * 70)
    
    root_dir = Path(__file__).parent
    all_issues = []
    files_scanned = 0
    
    # Scan all files
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and not should_skip(file_path):
            if file_path.suffix in CHECK_EXTENSIONS:
                files_scanned += 1
                issues = scan_file(file_path)
                all_issues.extend(issues)
    
    print(f"\n✓ Scanned {files_scanned} files\n")
    
    if all_issues:
        print("⚠️  POTENTIAL ISSUES FOUND:\n")
        for issue in all_issues:
            print(f"  File: {issue['file']}")
            print(f"  Type: {issue['type']}")
            print(f"  Line: {issue['line']}")
            print(f"  Value: {issue['value'][:50]}...")
            print()
        
        print(f"Total issues: {len(all_issues)}")
        print("\n⚠️  Please review these findings before pushing to GitHub!")
    else:
        print("✅ No sensitive information detected!")
        print("\nRepository appears safe to push to GitHub.")
        print("\nFinal checklist:")
        print("  ✓ No API keys found")
        print("  ✓ No real email addresses found")  
        print("  ✓ No real IP addresses found")
        print("  ✓ No passwords found")
    
    # Check for required files
    print("\n" + "=" * 70)
    print("REQUIRED FILES CHECK")
    print("=" * 70)
    
    required_files = [
        '.gitignore',
        'README.md',
        'SETUP_GUIDE.md',
        'backend/.env.example',
        'backend/requirements.txt',
        'frontend/package.json',
    ]
    
    for req_file in required_files:
        file_path = root_dir / req_file
        if file_path.exists():
            print(f"  ✓ {req_file}")
        else:
            print(f"  ✗ {req_file} - MISSING!")
    
    # Check for files that should NOT be committed
    print("\n" + "=" * 70)
    print("FILES THAT SHOULD NOT BE COMMITTED")
    print("=" * 70)
    
    forbidden_files = [
        'backend/.env',
        'backend/crypto_trading.db',
        'backend/*.log',
        'backend/venv',
        'frontend/node_modules',
    ]
    
    found_forbidden = False
    for forbidden in forbidden_files:
        if '*' in forbidden:
            # Handle wildcards
            pattern = forbidden.replace('*', '')
            parent = root_dir / os.path.dirname(forbidden)
            if parent.exists():
                matches = list(parent.glob(os.path.basename(forbidden)))
                if matches:
                    found_forbidden = True
                    print(f"  ⚠️  {forbidden} - Found {len(matches)} file(s)")
        else:
            file_path = root_dir / forbidden
            if file_path.exists():
                found_forbidden = True
                print(f"  ⚠️  {forbidden} - EXISTS (should be in .gitignore)")
    
    if not found_forbidden:
        print("  ✓ No forbidden files found in working directory")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
    if not all_issues and not found_forbidden:
        print("\n🎉 Repository is READY for GitHub!")
        print("\nNext steps:")
        print("  1. git add .")
        print("  2. git commit -m 'Initial commit - Crypto Trading Bot'")
        print("  3. git push origin main")
    else:
        print("\n⚠️  Please fix the issues above before pushing!")

if __name__ == "__main__":
    main()
