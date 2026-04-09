#!/usr/bin/env python3
"""
Log a finding to findings.md.
Usage: python log_finding.py <title> <context> <finding> <impact> [action] [findings_file]
"""

import sys
import os
from datetime import datetime

def log_finding(title, context, finding, impact, action="", findings_file="findings.md"):
    """Log a finding to findings.md."""
    if not os.path.exists(findings_file):
        print(f"Error: {findings_file} not found")
        return False
    
    with open(findings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Create the new entry
    new_entry = f"""
### {current_date} - {title}
- **Context:** {context}
- **Finding:** {finding}
- **Impact:** {impact}
- **Action:** {action if action else "None required"}
"""
    
    # Find the "## Entries" section and add the new entry
    lines = content.split('\n')
    new_lines = []
    in_entries_section = False
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Look for "## Entries"
        if line.strip() == "## Entries":
            in_entries_section = True
            continue
        
        # If we're in the entries section and find the next section, add before it
        if in_entries_section and line.startswith("## ") and "Entries" not in line:
            # Insert the new entry before this line
            new_lines.insert(-1, new_entry.strip())
            added = True
            in_entries_section = False
    
    # If we didn't find a place to insert, add at the end
    if not added:
        new_lines.append(new_entry.strip())
    
    # Write back
    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Logged finding to {findings_file}: {title}")
    return True

def main():
    if len(sys.argv) < 5:
        print("Usage: python log_finding.py <title> <context> <finding> <impact> [action] [findings_file]")
        print("  title: Brief title for the finding")
        print("  context: What you were doing")
        print("  finding: What you discovered")
        print("  impact: How this affects the project")
        print("  action: What needs to be done (optional)")
        print("  findings_file: Path to findings.md (default: findings.md)")
        sys.exit(1)
    
    title = sys.argv[1]
    context = sys.argv[2]
    finding = sys.argv[3]
    impact = sys.argv[4]
    action = sys.argv[5] if len(sys.argv) > 5 else ""
    findings_file = sys.argv[6] if len(sys.argv) > 6 else "findings.md"
    
    log_finding(title, context, finding, impact, action, findings_file)

if __name__ == "__main__":
    main()