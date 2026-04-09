#!/usr/bin/env python3
"""
List all active projects from planning/index.md.
Usage: python list_projects.py [planning_dir]
"""

import sys
import os
import re

def parse_index(index_path):
    """Parse planning/index.md and extract project information."""
    if not os.path.exists(index_path):
        print(f"No index file found at {index_path}")
        return [], []
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    active_projects = []
    completed_projects = []
    
    # Find Active Projects section
    active_section = re.search(r'## Active Projects\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if active_section:
        lines = active_section.group(1).strip().split('\n')
        for line in lines:
            if '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    active_projects.append({
                        'directory': parts[1].strip('[]'),
                        'name': parts[2],
                        'status': parts[3],
                        'last_updated': parts[4],
                        'notes': parts[5] if len(parts) > 5 else ''
                    })
    
    # Find Completed Projects section
    completed_section = re.search(r'## Completed Projects\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if completed_section:
        lines = completed_section.group(1).strip().split('\n')
        for line in lines:
            if '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    completed_projects.append({
                        'directory': parts[1].strip('[]'),
                        'name': parts[2],
                        'completed': parts[3],
                        'archived_to': parts[4] if len(parts) > 4 else ''
                    })
    
    return active_projects, completed_projects

def list_projects(planning_dir="planning"):
    """List all projects in the planning directory."""
    index_path = os.path.join(planning_dir, "index.md")
    
    if not os.path.exists(planning_dir):
        print(f"Planning directory not found: {planning_dir}")
        print("Run init_planning.py to create the planning structure.")
        return
    
    active, completed = parse_index(index_path)
    
    print(f"Planning Directory: {planning_dir}/")
    print(f"Index File: {index_path}")
    print()
    
    if active:
        print("=== ACTIVE PROJECTS ===")
        for i, project in enumerate(active, 1):
            print(f"{i}. {project['name']}")
            print(f"   Directory: {project['directory']}")
            print(f"   Status: {project['status']}")
            print(f"   Last Updated: {project['last_updated']}")
            if project['notes']:
                print(f"   Notes: {project['notes']}")
            print()
    else:
        print("No active projects found.")
        print()
    
    if completed:
        print("=== COMPLETED PROJECTS ===")
        for i, project in enumerate(completed, 1):
            print(f"{i}. {project['name']}")
            print(f"   Directory: {project['directory']}")
            print(f"   Completed: {project['completed']}")
            if project['archived_to']:
                print(f"   Archived To: {project['archived_to']}")
            print()
    
    # Also list directories that might not be in index
    if os.path.exists(planning_dir):
        dirs = [d for d in os.listdir(planning_dir) 
                if os.path.isdir(os.path.join(planning_dir, d)) 
                and d != 'archive' 
                and not d.startswith('.')]
        
        if dirs:
            print("=== DIRECTORIES ON DISK ===")
            for d in sorted(dirs):
                # Check if directory is in active or completed lists
                in_active = any(p['directory'] == d for p in active)
                in_completed = any(p['directory'] == d for p in completed)
                
                status = ""
                if not in_active and not in_completed:
                    status = " [NOT IN INDEX]"
                elif in_active:
                    status = " [ACTIVE]"
                elif in_completed:
                    status = " [COMPLETED]"
                
                print(f"  - {d}{status}")

def main():
    planning_dir = sys.argv[1] if len(sys.argv) > 1 else "planning"
    list_projects(planning_dir)

if __name__ == "__main__":
    main()