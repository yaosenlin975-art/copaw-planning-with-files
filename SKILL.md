---
name: planning-with-files
description: Use when user needs to create task plans, track progress, or record findings for complex multi-step projects. Provides file-based task organization and progress tracking using persistent markdown files. Triggers include "create a plan", "track progress", "log findings", "multi-step project", "task organization", "planning", "implementation plan", "project tracking", or any request involving structured task management with persistent context.
---

# Planning with Files

## Overview

Use persistent markdown files as your "working memory on disk" for complex multi-step projects. All planning files are organized under a central `planning/` directory with subdirectories for each project/session.

## File Organization (NEW DESIGN)

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

## planning/index.md Template

```markdown
# Planning Index

**Last Updated:** [Date]

## Active Projects

| Directory | Project Name | Status | Last Updated | Notes |
|-----------|--------------|--------|--------------|-------|
| [project-auth-refactor] | Auth System Refactor | In Progress | 2026-04-08 | Phase 2 of 3 |
| [session-9f090aa7] | UI Redesign | Not Started | 2026-04-08 | Session-based |

## Completed Projects

| Directory | Project Name | Completed | Archived To |
|-----------|--------------|-----------|-------------|
| [old-project] | Legacy Migration | 2026-03-15 | archive/2026-03/ |

## How to Use This Index

1. **New Project**: Create directory under `planning/`, add row to Active Projects
2. **Switch Project**: `cd planning/[directory-name]`
3. **Complete Project**: Move to Completed, archive files
4. **Clean Up**: Remove old completed projects periodically
```

## When to Use This Skill

- User requests a plan for a complex project with multiple steps
- User needs to track progress across multiple sessions
- User wants to log findings and errors systematically
- User mentions "planning", "tracking", "progress", "findings", or "multi-step"
- User asks to create an implementation plan or project roadmap

## 🪝 Auto-Trigger Hook (Copaw)

This skill includes a lightweight post_reply hook that automatically detects planning-related keywords:

**Keywords detected (partial match, not exact phrases):**

| Category | English | Chinese |
|----------|---------|---------|
| Core Planning | plan, planning, schedule, roadmap | 规划, 计划, 排期, 日程 |
| Progress | track progress, status update, checkpoint | 跟踪进度, 进度更新, 进展 |
| Tasks | task, todo, backlog, sprint | 任务, 待办, 待办事项 |
| Project | project, multi-step, phase, milestone | 项目, 多步骤, 阶段, 里程碑 |
| Timeline | timeline, deadline, ETA, estimate | 时间线, 截止日期, 工期, 预估 |
| Documentation | findings, retrospective, lessons learned | 记录发现, 复盘, 总结 |
| Verbs | organize, track, monitor | 整理, 梳理, 安排, 分解 |
| Phrases | create a plan, implementation plan | 帮我规划, 制定计划, 怎么安排 |

**Examples that trigger:**
- "我想**规划**一下" → 匹配"规划"
- "帮我做个**计划**" → 匹配"计划"
- "这个**任务**怎么**安排**" → 匹配"任务"和"安排"
- "项目**进度**怎么样了" → 匹配"进度"
- "需要**拆分**一下" → 匹配"拆分"

**How it works:**
1. Hook runs after each user message
2. Detects planning/completion/discovery keywords
3. Marks planning context for skill system
4. Skill triggers automatically if keywords found
5. **Auto-updates files** when completion/discovery detected

### 🪝 Auto-Update Features

| Keyword Type | Triggers | Action |
|--------------|----------|--------|
| **Completion** | 完成了, done, fixed, 实现了, 上线了 | Auto-append to `progress.md` |
| **Discovery** | 发现, 遇到, bug, error, 问题 | Auto-append to `findings.md` |
| **Planning** | 规划, 计划, task, 里程碑 | Mark context for skill |

**Examples:**
- "我完成了登录模块" → Auto-updates `progress.md`
- "发现API有限流问题" → Auto-logs to `findings.md`
- "帮我规划一下" → Triggers planning skill

**Hook location:** `skills/planning-with-files/hooks/planning_detector.py`

## FIRST: Restore Context

**Before doing anything else**, check for existing planning context:

1. **Check planning/index.md** - List all active projects
2. **Ask user which project** to work on (or create new)
3. **If only one active project**, assume that's the one
4. **Read the project's files**: `task_plan.md`, `progress.md`, `findings.md`

### Auto-Detection Logic

```python
# Pseudocode for context restoration
if planning/index.md exists:
    projects = parse_index()
    if len(projects.active) == 1:
        # Only one active project, use it
        load_project(projects.active[0])
    elif len(projects.active) > 1:
        # Multiple projects, ask user
        ask_user("Which project? " + projects.active_names)
    else:
        # No active projects, create new
        create_new_project()
else:
    # First time, initialize planning directory
    init_planning_directory()
```

## Creating a New Plan

### Step 1: Create Project Directory

```bash
# Create project directory
mkdir planning/[project-name-or-session-id]

# Update index
echo "| [project-name] | [Project Name] | Not Started | $(date) | |" >> planning/index.md
```

### Step 2: Initialize Files

Use templates in `skills/planning-with-files/templates/`:

```bash
# Copy templates to project directory
cp skills/planning-with-files/templates/task_plan.md planning/[project-name]/
cp skills/planning-with-files/templates/findings.md planning/[project-name]/
cp skills/planning-with-files/templates/progress.md planning/[project-name]/
```

### Step 3: Populate with Project Info

Edit the three files with project-specific content.

## Workflow During Execution

### Before Starting Work
1. **Read index.md** to understand project landscape
2. **Read current project's task_plan.md** for phase/task
3. **Read progress.md** for completed steps
4. **Read findings.md** for relevant context

### After Each Step
1. **Update progress.md** - Mark complete, add to history
2. **Update findings.md** - Log discoveries
3. **Update task_plan.md** - Check off tasks
4. **Update index.md** - Refresh "Last Updated" timestamp

### Before Major Decisions
1. **Re-read task_plan.md** for alignment
2. **Check findings.md** for lessons
3. **Update progress.md** with rationale

## Context Recovery Across Sessions

### Session Start Protocol

1. **Check if planning/ exists**
   - If no, ask: "Should I create a planning directory for project tracking?"
   
2. **Read planning/index.md**
   - List active projects
   - Ask user which to continue (if multiple)

3. **Load selected project's files**
   - Read task_plan.md, progress.md, findings.md
   - Summarize current status

4. **Ask continuation question**
   - "I found project [X] with status [Y]. Continue from where we left off?"

### Session ID vs Project Name

**Use Session ID when:**
- User doesn't specify a project name
- Quick, one-off planning task
- Experimental/temporary work

**Use Project Name when:**
- User specifies a project name
- Long-term, ongoing project
- Multiple related sessions expected

## Integration with Copaw Memory

This skill complements Copaw's memory system:

| Memory Type | Location | Purpose |
|-------------|----------|---------|
| **Long-term Memory** | MEMORY.md | Key decisions, preferences, lessons |
| **Daily Notes** | memory/YYYY-MM-DD.md | Raw logs, daily events |
| **Project Plans** | planning/[project]/ | Structured task management |

**Flow:**
- Planning files → Extract key lessons → MEMORY.md
- MEMORY.md → Inform planning decisions
- Daily notes → Reference planning status

## Completion & Archival

### Project Completion

1. **Update all files:**
   - task_plan.md: Status = "Completed"
   - progress.md: Final summary
   - findings.md: Retrospective

2. **Update index.md:**
   - Move from Active to Completed
   - Add completion date

3. **Archive (optional):**
   ```bash
   mkdir -p planning/archive/$(date +%Y-%m)
   mv planning/[project-name] planning/archive/$(date +%Y-%m)/
   ```

4. **Extract lessons:**
   - Review findings.md
   - Update MEMORY.md with key insights

## Helper Scripts

Located in `skills/planning-with-files/scripts/`:

### init_planning.py
```bash
# Initialize new project
python scripts/init_planning.py "Project Name" [session-id]
```

### update_progress.py
```bash
# Update progress in current project
python scripts/update_progress.py "Completed task description"
```

### log_finding.py
```bash
# Log a finding
python scripts/log_finding.py "Title" "Context" "Finding" "Impact" "Action"
```

### list_projects.py (NEW)
```bash
# List all active projects
python scripts/list_projects.py
```

## Tips for Success

1. **Always use planning/ directory** - Never scatter files in workspace root
2. **Update index.md** - Keep project list current
3. **Choose meaningful names** - Project names > random session IDs
4. **Archive completed projects** - Keep planning/ clean
5. **Cross-reference** - Link related projects in index.md

## Example Workflow

**User:** "I need to plan a game UI refactor"

**Assistant:** "I'll use the planning-with-files skill. Let me check existing projects..."

[Reads planning/index.md]

**Assistant:** "I found 2 active projects. Should I create a new one called 'game-ui-refactor' or continue with an existing project?"

**User:** "New project"

**Assistant:** "Creating planning/game-ui-refactor/ with task_plan.md, findings.md, progress.md. I've also updated planning/index.md. The plan includes three phases: analysis, redesign, implementation. Ready to start Phase 1?"

## Customization

- Add more phases/tasks as needed
- Include design decisions, API contracts, etc.
- Adjust templates for specific project types
- Add custom metadata fields

The key is **consistency within a project** and **organization across projects**.