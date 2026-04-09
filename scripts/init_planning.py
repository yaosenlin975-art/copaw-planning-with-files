#!/usr/bin/env python3
"""
Initialize planning files for a new project.
Creates project directory under planning/ with task_plan.md, findings.md, progress.md.
Updates planning/index.md with the new project.
"""

import os
import sys
from datetime import datetime

def create_file_from_template(template_path, output_path, replacements):
    """Create a file from a template with replacements."""
    if not os.path.exists(template_path):
        print(f"Warning: Template {template_path} not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for key, value in replacements.items():
        content = content.replace(key, value)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {output_path}")
    return True

def update_index(planning_dir, project_name, directory_name):
    """Update planning/index.md with the new project."""
    index_path = os.path.join(planning_dir, "index.md")
    
    # Create index if it doesn't exist
    if not os.path.exists(index_path):
        index_content = f"""# Planning Index

**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}

## Active Projects

| Directory | Project Name | Status | Last Updated | Notes |
|-----------|--------------|--------|--------------|-------|
| [{directory_name}] | {project_name} | Not Started | {datetime.now().strftime("%Y-%m-%d")} | |

## Completed Projects

| Directory | Project Name | Completed | Archived To |
|-----------|--------------|-----------|-------------|
| | | | |

## How to Use This Index

1. **New Project**: Create directory under `planning/`, add row to Active Projects
2. **Switch Project**: `cd planning/[directory-name]`
3. **Complete Project**: Move to Completed, archive files
4. **Clean Up**: Remove old completed projects periodically
"""
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"Created: {index_path}")
        return
    
    # Read existing index
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Active Projects section and add new project
    lines = content.split('\n')
    new_lines = []
    in_active_section = False
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Look for "## Active Projects"
        if line.strip() == "## Active Projects":
            in_active_section = True
            continue
        
        # If we're in active section and find a table row, add after it
        if in_active_section and line.strip().startswith('|') and not line.startswith('|---'):
            # Check if this is the last row before next section
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if not next_line.strip().startswith('|'):
                # Insert new row before the empty line
                new_row = f"| [{directory_name}] | {project_name} | Not Started | {datetime.now().strftime('%Y-%m-%d')} | |"
                new_lines.insert(-1, new_row)
                added = True
                in_active_section = False
    
    # If we didn't find a place to insert, add after "## Active Projects"
    if not added:
        for i, line in enumerate(new_lines):
            if line.strip() == "## Active Projects":
                # Add table header and new row
                new_lines.insert(i + 1, "")
                new_lines.insert(i + 2, "| Directory | Project Name | Status | Last Updated | Notes |")
                new_lines.insert(i + 3, "|-----------|--------------|--------|--------------|-------|")
                new_lines.insert(i + 4, f"| [{directory_name}] | {project_name} | Not Started | {datetime.now().strftime('%Y-%m-%d')} | |")
                added = True
                break
    
    # Update "Last Updated" date
    final_lines = []
    for line in new_lines:
        if line.startswith("**Last Updated:**"):
            final_lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
        else:
            final_lines.append(line)
    
    # Write back
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))
    
    print(f"Updated: {index_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python init_planning.py <project_name> [directory_name]")
        print("  project_name: Name of the project")
        print("  directory_name: Optional directory name (default: derived from project name)")
        print("\nExample:")
        print("  python init_planning.py 'Auth System Refactor'")
        print("  python init_planning.py 'UI Redesign' session-9f090aa7")
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    # Derive directory name from project name if not provided
    if len(sys.argv) > 2:
        directory_name = sys.argv[2]
    else:
        # Convert to lowercase, replace spaces with hyphens
        directory_name = project_name.lower().replace(' ', '-')
        # Remove special characters
        directory_name = ''.join(c for c in directory_name if c.isalnum() or c == '-')
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
    planning_dir = os.path.join(workspace_dir, "planning")
    
    # Create planning directory if it doesn't exist
    if not os.path.exists(planning_dir):
        os.makedirs(planning_dir)
        print(f"Created planning directory: {planning_dir}")
    
    # Create project directory
    project_dir = os.path.join(planning_dir, directory_name)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        print(f"Created project directory: {project_dir}")
    else:
        print(f"Project directory already exists: {project_dir}")
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Template replacements
    replacements = {
        "[Project Name]": project_name,
        "[Date]": current_date,
        "[Not Started | In Progress | Completed | On Hold]": "Not Started",
        "[Session ID]": directory_name if directory_name.startswith('session-') else "",
        "[Directory]": f"planning/{directory_name}/",
        "[One sentence describing what this project aims to achieve]": f"Goals for {project_name}",
        "[2-3 sentences about the approach and key decisions]": "To be defined",
        "[Technology 1]": "To be determined",
        "[Technology 2]": "To be determined",
        "[Phase Name]": "Planning",
        "[What this phase accomplishes]": "Define project scope and requirements",
        "[Time estimate]": "1 hour",
        "[Task description]": "Define project requirements",
        "[Files to create/modify]": "requirements.md",
        "[How to know it's done]": "Requirements document completed",
        "[Any additional context]": "",
        "[External dependency 1]": "None identified",
        "[Risk 1 and mitigation]": "Scope creep - define clear requirements",
        "[What you were doing]": "Project initialization",
        "[What you discovered]": "Starting new project",
        "[How this affects the project]": "Sets foundation for all work",
        "[What needs to be done]": "Define project plan",
        "[One sentence describing where we are now]": "Just started",
        "[Step description]": "Project initialized",
        "[Next action 1]": "Define project requirements",
        "[Blocker 1 and status]": "None",
        "[X hours]": "0",
        "[Estimated Y hours]": "1",
        "[Brief Title]": "Project Start",
        "[Link to related project in planning/index.md]": "",
        "[Cross-reference to other planning directories]": ""
    }
    
    # Templates directory
    templates_dir = os.path.join(script_dir, '..', 'templates')
    
    # Create files
    template_files = [
        ("task_plan.md", "task_plan.md"),
        ("findings.md", "findings.md"),
        ("progress.md", "progress.md")
    ]
    
    for template_name, output_name in template_files:
        template_path = os.path.join(templates_dir, template_name)
        output_path = os.path.join(project_dir, output_name)
        create_file_from_template(template_path, output_path, replacements)
    
    # Update index
    update_index(planning_dir, project_name, directory_name)
    
    print(f"\n[OK] Planning files created for '{project_name}'")
    print(f"[DIR] Location: planning/{directory_name}/")
    print(f"[INDEX] Index updated: planning/index.md")
    print("\nNext steps:")
    print("1. Review and customize task_plan.md")
    print("2. Define phases and tasks")
    print("3. Start working on Phase 1")
    print("4. Update progress.md after each step")
    print("5. Log findings in findings.md")
    print("\nTo list all projects: python list_projects.py")

if __name__ == "__main__":
    main()