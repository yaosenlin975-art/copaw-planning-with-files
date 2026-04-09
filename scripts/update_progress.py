#!/usr/bin/env python3
"""
Update progress.md with a completed step.
Usage: python update_progress.py <step_description> [progress_file]
"""

import sys
import os
from datetime import datetime

def update_progress(step_description, progress_file="progress.md"):
    """Update progress.md with a completed step."""
    if not os.path.exists(progress_file):
        print(f"Error: {progress_file} not found")
        return False
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Find the "Completed Steps" section and add the new step
    lines = content.split('\n')
    new_lines = []
    in_completed_section = False
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Look for "## Completed Steps"
        if line.strip() == "## Completed Steps":
            in_completed_section = True
            continue
        
        # If we're in the completed section and find the next section, add before it
        if in_completed_section and line.startswith("## ") and "Completed Steps" not in line:
            # Insert the new step before this line
            new_lines.insert(-1, f"- {current_date} - {step_description}")
            added = True
            in_completed_section = False
        
        # If we find an existing completed step, add after it
        if in_completed_section and line.strip().startswith("- ") and not added:
            # We'll add after the last existing step
            pass
    
    # If we didn't find a place to insert, add at the end of completed steps
    if not added:
        # Find the line number of "## Completed Steps"
        for i, line in enumerate(new_lines):
            if line.strip() == "## Completed Steps":
                # Insert after this line
                new_lines.insert(i + 1, f"- {current_date} - {step_description}")
                added = True
                break
    
    if not added:
        # Just append at the end
        new_lines.append(f"- {current_date} - {step_description}")
    
    # Update "Last Updated" date
    final_lines = []
    for line in new_lines:
        if line.startswith("**Last Updated:**"):
            final_lines.append(f"**Last Updated:** {current_date}")
        else:
            final_lines.append(line)
    
    # Write back
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))
    
    print(f"Updated {progress_file} with: {step_description}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_progress.py <step_description> [progress_file]")
        print("  step_description: Description of the completed step")
        print("  progress_file: Path to progress.md (default: progress.md)")
        sys.exit(1)
    
    step_description = sys.argv[1]
    progress_file = sys.argv[2] if len(sys.argv) > 2 else "progress.md"
    
    update_progress(step_description, progress_file)

if __name__ == "__main__":
    main()