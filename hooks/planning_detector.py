# -*- coding: utf-8 -*-
"""Planning detector hook for automatic skill triggering and progress updates.

This hook detects planning-related keywords in user messages,
automatically triggers the planning-with-files skill,
and updates progress/findings files when completion/discovery keywords are detected.
"""

import logging
import re
import os
import time
import subprocess
from typing import TYPE_CHECKING, Any

from agentscope.agent import ReActAgent
from agentscope.message import Msg

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ============================================================================
# Keyword Patterns
# ============================================================================

# Planning-related keywords (triggers skill)
PLANNING_KEYWORDS = [
    # === English Keywords ===
    # Core planning words
    r'\bplan\b', r'\bplanning\b', r'\bplanned\b', r'\bplanner\b',
    r'\bschedule\b', r'\bscheduling\b', r'\broadmap\b',
    
    # Progress tracking
    r'\btrack progress\b', r'\bprogress tracking\b', r'\bstatus update\b',
    r'\bcheckpoint\b', r'\bstandup\b', r'\bdaily report\b',
    
    # Task management
    r'\btask\b', r'\btasks\b', r'\btodo\b', r'\btodo list\b',
    r'\baction items\b', r'\bbacklog\b', r'\bsprint\b',
    
    # Project terms
    r'\bproject\b', r'\bprojects\b', r'\bmulti-step\b', r'\bphase\b', r'\bphases\b',
    r'\bmilestone\b', r'\bmilestones\b', r'\bdeliverable\b',
    
    # Timeline & deadlines
    r'\btimeline\b', r'\bdeadline\b', r'\bdue date\b', r'\bdue\b',
    r'\beta\b', r'\bestimate\b', r'\bestimation\b',
    
    # Documentation
    r'\blog findings\b', r'\bfindings\b', r'\bretrospective\b',
    r'\bpostmortem\b', r'\blessons learned\b',
    
    # Common phrases
    r'\bimplementation plan\b', r'\bproject tracking\b', r'\btask organization\b',
    r'\bgantt\b', r'\bkanban\b', r'\bwork breakdown\b', r'\bwbs\b',
    
    # Verbs
    r'\borganize\b', r'\borganising\b', r'\borganizing\b',
    r'\btrack\b', r'\btracking\b', r'\bmonitor\b', r'\bmonitoring\b',
    
    # === Chinese Keywords ===
    # Core planning
    r'规划', r'计划', r'排期', r'排成', r'日程', r'时间表',
    
    # Progress tracking
    r'跟踪进度', r'进度跟踪', r'进度更新', r'状态更新', r'进展',
    
    # Task management
    r'任务', r'待办', r'待办事项', r'工作项', r' backlog',
    
    # Project terms
    r'项目', r'多步骤', r'阶段', r'里程碑', r'交付物',
    
    # Timeline & deadlines
    r'时间线', r'截止日期', r'截止时间', r'工期', r'预估',
    
    # Documentation
    r'记录发现', r'复盘', r'总结', r'经验教训',
    
    # Common phrases
    r'实现计划', r'项目跟踪', r'任务组织', r'甘特图', r'看板',
    
    # Verbs
    r'整理', r'梳理', r'安排', r'分解', r'拆分',
    
    # === Common Phrases (multi-word) ===
    r'create a plan', r'make a plan', r'develop a plan', r'draft a plan',
    r'帮我规划', r'制定计划', r'创建计划', r'做个计划', r'做个排期',
    r'怎么安排', r'如何安排', r'怎么规划', r'如何规划',
    r'分解任务', r'拆解任务', r'拆分任务',
]

# Completion keywords (triggers progress.md update)
COMPLETION_KEYWORDS = [
    # English
    r'\bcompleted\b', r'\bdone\b', r'\bfinished\b', r'\bimplemented\b',
    r'\bsolved\b', r'\bfixed\b', r'\bresolved\b', r'\bshipped\b',
    r'\bdelivered\b', r'\breleased\b', r'\bdeployed\b',
    
    # Chinese
    r'完成了', r'做好了', r'搞定了', r'做完了', r'完工',
    r'实现了', r'解决了', r'修复了', r'搞定了', r'上线了',
    r'部署了', r'交付了', r'发布了',
    
    # Phrases
    r'just finished', r'just completed', r'just shipped',
    r'刚完成', r'刚做完', r'刚搞定',
]

# Discovery/issue keywords (triggers findings.md update)
DISCOVERY_KEYWORDS = [
    # English
    r'\bfound\b', r'\bdiscovered\b', r'\bnoticed\b', r'\brealized\b',
    r'\bissue\b', r'\bbug\b', r'\berror\b', r'\bproblem\b',
    r'\bblocker\b', r'\bobstacle\b', r'\blimitation\b',
    r'\brate limit\b', r'\btimeout\b', r'\bcrash\b',
    
    # Chinese
    r'发现', r'遇到', r'碰到', r'注意到', r'意识到',
    r'问题', r'bug', r'错误', r'报错', r'异常',
    r'阻塞', r'阻碍', r'限制', r'限制',
    r'超时', r'崩溃', r'闪退',
    
    # Phrases
    r'ran into', r'came across', r'hit a wall',
    r'遇到了', r'碰到了', r'踩坑',
]

# Compiled patterns for efficiency
PLANNING_PATTERN = re.compile('|'.join(PLANNING_KEYWORDS), re.IGNORECASE)
COMPLETION_PATTERN = re.compile('|'.join(COMPLETION_KEYWORDS), re.IGNORECASE)
DISCOVERY_PATTERN = re.compile('|'.join(DISCOVERY_KEYWORDS), re.IGNORECASE)

# Compiled pattern for efficiency
PLANNING_PATTERN = re.compile('|'.join(PLANNING_KEYWORDS), re.IGNORECASE)


class PlanningDetectorHook:
    """Hook for detecting planning keywords and triggering skill.

    This hook runs after each assistant reply to check if the
    user's message contains planning-related keywords.
    """

    def __init__(self, workspace_dir: str):
        """Initialize planning detector hook.

        Args:
            workspace_dir: The workspace directory
        """
        self.workspace_dir = workspace_dir

    async def __call__(
        self,
        agent: ReActAgent,
        kwargs: dict[str, Any],
        output: Msg,
    ) -> Msg | None:
        """Post-reply hook to detect planning keywords and auto-update files.

        Args:
            agent: The agent instance
            kwargs: The reply function arguments
            output: The output message from the agent

        Returns:
            None (doesn't modify the output message)
        """
        try:
            # Get the user message from kwargs
            user_msg = self._extract_user_message(kwargs)
            
            if not user_msg:
                return None
            
            # Check for completion keywords -> update progress.md
            if self._contains_completion_keywords(user_msg):
                logger.info(f"[PlanningHook] Completion detected: {user_msg[:50]}...")
                self._auto_update_progress(user_msg)
            
            # Check for discovery keywords -> update findings.md
            elif self._contains_discovery_keywords(user_msg):
                logger.info(f"[PlanningHook] Discovery detected: {user_msg[:50]}...")
                self._auto_log_finding(user_msg)
            
            # Check for planning keywords -> mark context for skill
            elif self._contains_planning_keywords(user_msg):
                logger.info(f"[PlanningHook] Planning keywords detected: {user_msg[:50]}...")
                self._mark_planning_context(agent, user_msg)
                
        except Exception as e:
            logger.warning(f"[PlanningHook] Error: {e}")

        return None

    def _extract_user_message(self, kwargs: dict[str, Any]) -> str | None:
        """Extract user message from kwargs.

        Args:
            kwargs: The reply function arguments

        Returns:
            The user message content or None
        """
        try:
            # The user message is typically in kwargs['msg']
            if 'msg' in kwargs:
                msg = kwargs['msg']
                if isinstance(msg, Msg):
                    return str(msg.content) if msg.content else None
                elif isinstance(msg, dict) and 'content' in msg:
                    return str(msg['content'])
                elif isinstance(msg, str):
                    return msg
            return None
        except Exception as e:
            logger.debug(f"[PlanningHook] Error extracting message: {e}")
            return None

    def _contains_planning_keywords(self, message: str) -> bool:
        """Check if message contains planning-related keywords."""
        if not message:
            return False
        return bool(PLANNING_PATTERN.search(message))

    def _contains_completion_keywords(self, message: str) -> bool:
        """Check if message contains completion keywords."""
        if not message:
            return False
        return bool(COMPLETION_PATTERN.search(message))

    def _contains_discovery_keywords(self, message: str) -> bool:
        """Check if message contains discovery/issue keywords."""
        if not message:
            return False
        return bool(DISCOVERY_PATTERN.search(message))

    def _mark_planning_context(self, agent: ReActAgent, message: str) -> None:
        """Mark that planning context is needed."""
        try:
            if not hasattr(agent, '_planning_context'):
                agent._planning_context = {}
            
            agent._planning_context['detected'] = True
            agent._planning_context['message'] = message
            agent._planning_context['timestamp'] = time.time()
            
            logger.debug("[PlanningHook] Context marked for skill invocation")
            
        except Exception as e:
            logger.debug(f"[PlanningHook] Error marking context: {e}")

    def _auto_update_progress(self, message: str) -> None:
        """Automatically update progress.md when completion is detected."""
        try:
            planning_dir = self._get_planning_dir()
            
            # Find active project
            project_dir = self._find_active_project(planning_dir)
            if not project_dir:
                logger.debug("[PlanningHook] No active project found, skipping progress update")
                return
            
            progress_file = os.path.join(project_dir, 'progress.md')
            if not os.path.exists(progress_file):
                logger.debug(f"[PlanningHook] Progress file not found: {progress_file}")
                return
            
            # Extract meaningful description from message
            description = self._extract_completion_description(message)
            
            # Update progress.md
            self._append_to_progress(progress_file, description)
            logger.info(f"[PlanningHook] Auto-updated progress: {description}")
            
        except Exception as e:
            logger.warning(f"[PlanningHook] Error auto-updating progress: {e}")

    def _auto_log_finding(self, message: str) -> None:
        """Automatically log to findings.md when discovery is detected."""
        try:
            planning_dir = self._get_planning_dir()
            
            # Find active project
            project_dir = self._find_active_project(planning_dir)
            if not project_dir:
                logger.debug("[PlanningHook] No active project found, skipping findings log")
                return
            
            findings_file = os.path.join(project_dir, 'findings.md')
            if not os.path.exists(findings_file):
                logger.debug(f"[PlanningHook] Findings file not found: {findings_file}")
                return
            
            # Extract meaningful description from message
            title, context = self._extract_discovery_info(message)
            
            # Log to findings.md
            self._append_to_findings(findings_file, title, context)
            logger.info(f"[PlanningHook] Auto-logged finding: {title}")
            
        except Exception as e:
            logger.warning(f"[PlanningHook] Error auto-logging finding: {e}")

    def _find_active_project(self, planning_dir: str) -> str | None:
        """Find the most recently updated project directory."""
        try:
            if not os.path.exists(planning_dir):
                return None
            
            # Get all subdirectories
            projects = []
            for item in os.listdir(planning_dir):
                item_path = os.path.join(planning_dir, item)
                if os.path.isdir(item_path) and item != 'archive':
                    # Check if it has planning files
                    if os.path.exists(os.path.join(item_path, 'progress.md')):
                        projects.append(item_path)
            
            if not projects:
                return None
            
            # Return the most recently modified one
            projects.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return projects[0]
            
        except Exception as e:
            logger.debug(f"[PlanningHook] Error finding active project: {e}")
            return None

    def _extract_completion_description(self, message: str) -> str:
        """Extract a clean description from completion message."""
        # Remove common prefixes
        message = re.sub(r'^(我|我们|已经|刚|刚刚)\s*', '', message)
        message = re.sub(r'^(I|We|Just)\s+(have |)\s*', '', message, flags=re.IGNORECASE)
        
        # Truncate if too long
        if len(message) > 100:
            message = message[:97] + '...'
        
        return message

    def _extract_discovery_info(self, message: str) -> tuple[str, str]:
        """Extract title and context from discovery message."""
        # Use first sentence as title
        title = message.split('。')[0].split('.')[0].split('，')[0]
        if len(title) > 50:
            title = title[:47] + '...'
        
        # Full message as context
        context = message[:200] if len(message) > 200 else message
        
        return title, context

    def _append_to_progress(self, progress_file: str, description: str) -> None:
        """Append a completion entry to progress.md."""
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find "## Completed Steps" section
            lines = content.split('\n')
            new_lines = []
            found_section = False
            
            date_str = time.strftime('%Y-%m-%d %H:%M')
            entry = f"- {date_str} - {description}"
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                if line.strip() == '## Completed Steps':
                    found_section = True
                elif found_section and line.strip().startswith('- '):
                    # Insert before existing entries
                    if i == len(lines) - 1 or not lines[i+1].strip().startswith('- '):
                        new_lines.insert(-1, entry)
                        found_section = False
            
            if found_section and not any(l.strip().startswith('- ') for l in lines):
                # No existing entries, add after header
                new_lines.append(entry)
            
            # Update "Last Updated" date
            final_lines = []
            for line in new_lines:
                if line.startswith('**Last Updated:**'):
                    final_lines.append(f'**Last Updated:** {date_str.split(" ")[0]}')
                else:
                    final_lines.append(line)
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(final_lines))
                
        except Exception as e:
            logger.warning(f"[PlanningHook] Error appending to progress: {e}")

    def _append_to_findings(self, findings_file: str, title: str, context: str) -> None:
        """Append a finding entry to findings.md."""
        try:
            with open(findings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            date_str = time.strftime('%Y-%m-%d %H:%M')
            entry = f"""
### {date_str} - {title}
- **Context:** Auto-detected from conversation
- **Finding:** {context}
- **Impact:** To be assessed
- **Action:** Review and update if needed
"""
            
            # Find "## Entries" section and append
            lines = content.split('\n')
            new_lines = []
            found_section = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                if line.strip() == '## Entries':
                    found_section = True
                elif found_section and not line.strip().startswith('###') and line.strip() != '':
                    # Found first non-header, non-empty line - insert before it
                    if i > 0:
                        new_lines.insert(-1, entry.strip())
                        found_section = False
            
            if found_section:
                # No entries yet, add at end
                new_lines.append(entry.strip())
            
            with open(findings_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
                
        except Exception as e:
            logger.warning(f"[PlanningHook] Error appending to findings: {e}")


def create_planning_hook(workspace_dir: str) -> PlanningDetectorHook:
    """Factory function to create planning detector hook.

    Args:
        workspace_dir: The workspace directory

    Returns:
        PlanningDetectorHook instance
    """
    return PlanningDetectorHook(workspace_dir)