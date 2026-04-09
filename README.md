# Planning with Files Skill for Copaw

A Copaw skill for file-based task organization and progress tracking for complex multi-step projects.

## Overview

This skill creates and maintains three persistent markdown files **organized under a central `planning/` directory** to preserve context across sessions:

- **task_plan.md** - Master plan with phases, tasks, and acceptance criteria
- **findings.md** - Log of discoveries, errors, and insights during execution  
- **progress.md** - Current status, completed steps, and next actions

## File Organization (NEW DESIGN)

All planning files are organized under a central `planning/` directory:

```
workspace/
└── planning/                      # Central planning directory
    ├── index.md                   # Project index (lists all projects)
    ├── project-auth-refactor/     # Project 1 (by name)
    │   ├── task_plan.md
    │   ├── findings.md
    │   └── progress.md
    ├── session-9f090aa7/          # Project 2 (by session ID)
    │   ├── task_plan.md
    │   ├── findings.md
    │   └── progress.md
    └── game-ui/                   # Project 3
        ├── task_plan.md
        ├── findings.md
        └── progress.md
```

### Key Principles

1. **Central Location**: All plans live under `planning/`
2. **Project Isolation**: Each project gets its own subdirectory
3. **Naming Convention**: Use project name or session ID as directory name
4. **Index File**: `planning/index.md` tracks all active projects

## Installation

This skill is already installed in your Copaw workspace. No additional installation is required.

## Usage

### Automatic Triggering

The skill automatically triggers when you mention:
- "create a plan", "track progress", "log findings"
- "multi-step project", "task organization", "planning"
- "implementation plan", "project tracking"
- Any request involving structured task management with persistent context

### 🪝 Auto-Detection Hook

A lightweight post_reply hook automatically detects planning keywords:
- **English**: plan, planning, track progress, multi-step, roadmap, milestone, phase, timeline
- **Chinese**: 规划, 计划, 跟踪进度, 多步骤, 路线图, 里程碑, 阶段, 排期

When keywords are detected, the skill is automatically invoked.

### Manual Usage

You can also manually invoke the skill by saying:
- "Use the planning-with-files skill to create a plan for..."
- "I need to track progress on this project using planning files"

## Workflow

### 1. Create a New Plan

When starting a new project, the skill will:
1. Create a project directory under `planning/`
2. Create three markdown files (task_plan.md, findings.md, progress.md)
3. Update `planning/index.md` with the new project
4. Populate files with project-specific information

### 2. Track Progress

As you work:
1. Update progress.md after completing each step
2. Log findings and errors in findings.md
3. Check off completed tasks in task_plan.md
4. Update index.md with latest status

### 3. Restore Context

When starting a new session:
1. Read `planning/index.md` to see all active projects
2. Ask user which project to continue (if multiple)
3. Load the selected project's files
4. Summarize current status and continue

## Helper Scripts

Scripts in the `scripts/` directory:

### Initialize Planning Files
```bash
# Create new project under planning/
python scripts/init_planning.py "My Project"

# Create with custom directory name
python scripts/init_planning.py "UI Redesign" session-9f090aa7
```

### List All Projects
```bash
# Show all active and completed projects
python scripts/list_projects.py
```

### Update Progress
```bash
# Update progress in current project
python scripts/update_progress.py "Completed authentication module"
```

### Log a Finding
```bash
# Log a finding
python scripts/log_finding.py "API Rate Limiting" "Testing API calls" "Rate limit is 100 requests/minute" "Need to implement backoff" "Add exponential backoff"
```

## Integration with Copaw Memory

This skill complements Copaw's existing memory system:

| Memory Type | Location | Purpose |
|-------------|----------|---------|
| **Long-term Memory** | MEMORY.md | Key decisions, preferences, lessons |
| **Daily Notes** | memory/YYYY-MM-DD.md | Raw logs, daily events |
| **Project Plans** | planning/[project]/ | Structured task management |

**Flow:**
- Planning files → Extract key lessons → MEMORY.md
- MEMORY.md → Inform planning decisions
- Daily notes → Reference planning status

## Project Management

### Active Projects
- Listed in `planning/index.md` under "Active Projects"
- Each has its own directory with three files
- Can be worked on across multiple sessions

### Completed Projects
- Moved to "Completed Projects" section in index.md
- Can be archived to `planning/archive/` directory
- Key lessons extracted to MEMORY.md

### Session-based Projects
- Use session ID as directory name: `session-9f090aa7`
- Good for quick, one-off planning tasks
- Can be converted to named projects later

## Example

**User:** "I need to plan a refactor of our authentication system"

**Assistant:** "I'll use the planning-with-files skill. Let me check existing projects..."

[Reads planning/index.md]

**Assistant:** "I found 2 active projects. Should I create a new one called 'auth-refactor' or continue with an existing project?"

**User:** "New project"

**Assistant:** "Creating planning/auth-refactor/ with task_plan.md, findings.md, progress.md. I've also updated planning/index.md. The plan includes three phases: analysis, implementation, testing. Ready to start Phase 1?"

## Tips for Success

1. **Always use planning/ directory** - Never scatter files in workspace root
2. **Update index.md** - Keep project list current
3. **Choose meaningful names** - Project names > random session IDs
4. **Archive completed projects** - Keep planning/ clean
5. **Cross-reference** - Link related projects in index.md

## Customization

You can customize the templates based on project needs:
- Add more phases or tasks
- Include additional sections (e.g., "Design Decisions", "API Contracts")
- Adjust the format of findings or progress tracking
- Add project-specific metadata

## Support

For issues or suggestions, please refer to the main Copaw documentation or create an issue in the skill repository.