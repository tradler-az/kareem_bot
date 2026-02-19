"""
Bosco Core - Agents Package
Multi-agent orchestration system for specialized AI agents
"""

from bosco_os.agents.base_agent import (
    BaseAgent,
    AgentTask,
    AgentStatus,
    TaskPriority,
    AgentRegistry,
    get_agent_registry,
    create_task,
    run_task_with_agent
)

from bosco_os.agents.security_agent import (
    SecurityAgent,
    get_security_agent
)

from bosco_os.agents.devops_agent import (
    DevOpsAgent,
    get_devops_agent
)

from bosco_os.agents.research_agent import (
    ResearchAgent,
    get_research_agent
)

from bosco_os.agents.orchestrator import (
    AgentOrchestrator,
    Workflow,
    WorkflowState,
    get_orchestrator
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentTask", 
    "AgentStatus",
    "TaskPriority",
    "AgentRegistry",
    "get_agent_registry",
    "create_task",
    "run_task_with_agent",
    
    # Specialized Agents
    "SecurityAgent",
    "get_security_agent",
    "DevOpsAgent", 
    "get_devops_agent",
    "ResearchAgent",
    "get_research_agent",
    
    # Orchestrator
    "AgentOrchestrator",
    "Workflow",
    "WorkflowState",
    "get_orchestrator"
]

