"""
Bosco Core - Multi-Agent Orchestration System
Base agent framework for specialized AI agents
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import uuid


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AgentTask:
    """
    Represents a task to be executed by an agent
    """
    
    def __init__(
        self,
        description: str,
        task_type: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        context: Optional[Dict] = None,
        callback: Optional[Callable] = None
    ):
        self.id = f"task_{uuid.uuid4().hex[:8]}"
        self.description = description
        self.task_type = task_type
        self.priority = priority
        self.context = context or {}
        self.callback = callback
        
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.completed_at = None
        self.agent_id = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "agent_id": self.agent_id
        }


class BaseAgent(ABC):
    """
    Abstract base class for all Bosco agents
    Provides common interfaces for task execution, state management, and handoff
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str],
        llm_client=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.llm_client = llm_client
        
        # State management
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.working_memory: Dict[str, Any] = {}
        
        # Configuration
        self.config = {
            "max_retries": 3,
            "timeout_seconds": 120,
            "verbose": True
        }
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent
        Must be implemented by subclasses
        
        Args:
            task: The task to execute
            
        Returns:
            Result dictionary with status and output
        """
        pass
    
    @abstractmethod
    def can_handle(self, task: AgentTask) -> bool:
        """
        Check if this agent can handle the given task
        Based on capabilities and current state
        
        Args:
            task: The task to check
            
        Returns:
            True if agent can handle, False otherwise
        """
        pass
    
    async def run(self, task: AgentTask) -> Dict[str, Any]:
        """
        Run a task with error handling and state management
        
        Args:
            task: The task to run
            
        Returns:
            Result dictionary
        """
        self.current_task = task
        task.agent_id = self.agent_id
        task.status = "running"
        
        try:
            self.status = AgentStatus.THINKING
            task.status = "thinking"
            
            # Check if we can handle
            if not self.can_handle(task):
                return {
                    "success": False,
                    "error": f"Agent {self.name} cannot handle task type: {task.task_type}",
                    "task_id": task.id
                }
            
            # Execute the task
            self.status = AgentStatus.ACTING
            task.status = "acting"
            
            result = await self.execute_task(task)
            
            # Store result
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now()
            self.status = AgentStatus.COMPLETED
            
            # Run callback if exists
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    print(f"[{self.name}] Callback error: {e}")
            
            return {
                "success": True,
                "result": result,
                "agent": self.name,
                "task_id": task.id
            }
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = datetime.now()
            self.status = AgentStatus.ERROR
            
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "task_id": task.id
            }
        
        finally:
            self.task_history.append(task)
            self.current_task = None
    
    def update_memory(self, key: str, value: Any):
        """Update working memory"""
        self.working_memory[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
    
    def get_memory(self, key: str) -> Optional[Any]:
        """Get from working memory"""
        if key in self.working_memory:
            entry = self.working_memory[key]
            # Check expiration (5 minutes)
            if (datetime.now() - entry["timestamp"]).seconds < 300:
                return entry["value"]
        return None
    
    def clear_memory(self):
        """Clear working memory"""
        self.working_memory.clear()
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task.id if self.current_task else None,
            "tasks_completed": len([t for t in self.task_history if t.status == "completed"]),
            "capabilities": self.capabilities
        }
    
    def log(self, message: str):
        """Log a message"""
        if self.config.get("verbose", True):
            print(f"[{self.name}] {message}")


class AgentRegistry:
    """
    Registry for managing available agents
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
    
    def register(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        print(f"[Registry] Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            print(f"[Registry] Unregistered agent: {agent.name}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def find_agent(self, task: AgentTask) -> Optional[BaseAgent]:
        """Find the best agent to handle a task"""
        for agent in self.agents.values():
            if agent.can_handle(task):
                return agent
        return None
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Get agents with a specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]
    
    def add_task(self, task: AgentTask):
        """Add a task to the queue"""
        self.task_queue.append(task)
        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
    
    def get_next_task(self) -> Optional[AgentTask]:
        """Get the next task from queue"""
        if self.task_queue:
            return self.task_queue.pop(0)
        return None
    
    def get_status(self) -> Dict:
        """Get registry status"""
        return {
            "total_agents": len(self.agents),
            "queued_tasks": len(self.task_queue),
            "agents": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "status": a.status.value
                }
                for a in self.agents.values()
            ]
        }


# Global registry
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


# Convenience functions
def create_task(
    description: str,
    task_type: str,
    priority: TaskPriority = TaskPriority.NORMAL,
    context: Optional[Dict] = None
) -> AgentTask:
    """Create a new task"""
    return AgentTask(description, task_type, priority, context)


async def run_task_with_agent(task: AgentTask) -> Dict[str, Any]:
    """Run a task with automatic agent selection"""
    registry = get_agent_registry()
    agent = registry.find_agent(task)
    
    if not agent:
        return {
            "success": False,
            "error": f"No agent found to handle task type: {task.task_type}"
        }
    
    return await agent.run(task)


if __name__ == "__main__":
    # Test the agent system
    print("=== Testing Multi-Agent System ===\n")
    
    # Create a simple test agent
    class TestAgent(BaseAgent):
        async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
            self.log(f"Executing task: {task.description}")
            await asyncio.sleep(0.1)  # Simulate work
            return {
                "output": f"Task '{task.description}' completed",
                "type": task.task_type
            }
        
        def can_handle(self, task: AgentTask) -> bool:
            return task.task_type in self.capabilities
    
    # Create registry
    registry = get_agent_registry()
    
    # Create and register test agent
    test_agent = TestAgent(
        agent_id="test_agent",
        name="Test Agent",
        description="A test agent",
        capabilities=["test", "echo"]
    )
    registry.register(test_agent)
    
    # Create and run a task
    task = create_task("Test task", "test", TaskPriority.NORMAL)
    result = asyncio.run(test_agent.run(task))
    
    print(f"\nResult: {result}")
    print(f"\nRegistry Status: {registry.get_status()}")

