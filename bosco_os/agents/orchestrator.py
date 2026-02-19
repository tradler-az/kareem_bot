"""
Bosco Core - Multi-Agent Orchestrator
Coordinates multiple specialized agents for complex tasks
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid

from bosco_os.agents.base_agent import (
    BaseAgent, AgentTask, AgentStatus, TaskPriority,
    AgentRegistry, get_agent_registry, create_task
)
from bosco_os.agents.security_agent import SecurityAgent, get_security_agent
from bosco_os.agents.devops_agent import DevOpsAgent, get_devops_agent
from bosco_os.agents.research_agent import ResearchAgent, get_research_agent


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Workflow:
    """
    Represents a multi-step workflow that may involve multiple agents
    """
    
    def __init__(self, name: str, description: str = ""):
        self.id = f"workflow_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.steps: List[Dict] = []
        self.state = WorkflowState.PENDING
        self.results: List[Dict] = []
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def add_step(self, agent_type: str, task: AgentTask, dependencies: List[str] = None):
        """Add a step to the workflow"""
        self.steps.append({
            "id": f"step_{len(self.steps)}",
            "agent_type": agent_type,
            "task": task,
            "dependencies": dependencies or [],
            "status": "pending",
            "result": None
        })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "steps": [
                {
                    "id": s["id"],
                    "agent_type": s["agent_type"],
                    "task_description": s["task"].description,
                    "status": s["status"]
                }
                for s in self.steps
            ],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AgentOrchestrator:
    """
    Main orchestrator for multi-agent coordination
    Manages agent registry, workflows, and task handoffs
    """
    
    def __init__(self):
        self.registry = get_agent_registry()
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_history: List[Workflow] = []
        
        # Initialize default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize and register default agents"""
        # Security Agent
        security_agent = SecurityAgent()
        self.registry.register(security_agent)
        
        # DevOps Agent
        devops_agent = DevOpsAgent()
        self.registry.register(devops_agent)
        
        # Research Agent
        research_agent = ResearchAgent()
        self.registry.register(research_agent)
        
        print(f"[Orchestrator] Initialized with {len(self.registry.agents)} agents")
    
    def register_agent(self, agent: BaseAgent):
        """Register a custom agent"""
        self.registry.register(agent)
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task with automatic agent selection
        
        Args:
            task: The task to execute
            
        Returns:
            Result dictionary with agent response
        """
        # Find best agent
        agent = self.registry.find_agent(task)
        
        if not agent:
            return {
                "success": False,
                "error": f"No agent found to handle task type: {task.task_type}",
                "available_agents": [a.name for a in self.registry.get_all_agents()]
            }
        
        # Execute with agent
        self.log(f"Routing task to {agent.name}")
        result = await agent.run(task)
        
        return result
    
    async def execute_parallel(self, tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of results
        """
        self.log(f"Executing {len(tasks)} tasks in parallel")
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[self.execute_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Convert exceptions to error dicts
        processed_results = []
        for r in results:
            if isinstance(r, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(r)
                })
            else:
                processed_results.append(r)
        
        return processed_results
    
    async def execute_sequential(self, tasks: List[AgentTask]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks sequentially
        
        Args:
            tasks: List of tasks to execute in order
            
        Returns:
            List of results
        """
        self.log(f"Executing {len(tasks)} tasks sequentially")
        
        results = []
        for i, task in enumerate(tasks):
            self.log(f"Step {i+1}/{len(tasks)}: {task.description}")
            result = await self.execute_task(task)
            results.append(result)
            
            # Stop if task failed
            if not result.get("success", False):
                self.log(f"Task {i+1} failed, stopping sequence")
                break
        
        return results
    
    async def create_and_run_workflow(
        self,
        name: str,
        steps: List[Dict],
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Create and execute a multi-step workflow
        
        Args:
            name: Workflow name
            steps: List of step definitions
            context: Shared context for workflow
            
        Returns:
            Workflow execution results
        """
        workflow = Workflow(name)
        self.active_workflows[workflow.id] = workflow
        
        self.log(f"Starting workflow: {name}")
        
        # Shared context between steps
        shared_context = context or {}
        
        try:
            workflow.state = WorkflowState.RUNNING
            
            for i, step_def in enumerate(steps):
                step_id = f"step_{i}"
                agent_type = step_def.get("agent_type")
                task_type = step_def.get("task_type")
                task_description = step_def.get("description", "")
                
                # Merge shared context with step-specific context
                step_context = {**shared_context, **step_def.get("context", {})}
                
                # Use result from previous step if applicable
                if i > 0 and workflow.results:
                    previous_result = workflow.results[-1].get("result", {})
                    step_context["previous_result"] = previous_result
                
                # Create task
                task = AgentTask(
                    description=task_description,
                    task_type=task_type,
                    priority=step_def.get("priority", TaskPriority.NORMAL),
                    context=step_context
                )
                
                # Find agent
                agent = self.registry.get_agent(agent_type)
                if not agent:
                    # Try to find by capability
                    task_temp = AgentTask("", task_type)
                    agent = self.registry.find_agent(task_temp)
                
                if not agent:
                    return {
                        "success": False,
                        "error": f"No agent found for step {i+1}: {agent_type}"
                    }
                
                # Execute step
                self.log(f"Executing step {i+1}/{len(steps)}: {task_description}")
                result = await agent.run(task)
                
                workflow.results.append({
                    "step_id": step_id,
                    "agent": agent.name,
                    "result": result
                })
                
                # Update shared context
                if result.get("success"):
                    shared_context.update(result.get("result", {}))
                
                # Check for failure
                if not result.get("success", False) and step_def.get("critical", True):
                    workflow.state = WorkflowState.FAILED
                    return {
                        "success": False,
                        "workflow": workflow.to_dict(),
                        "error": f"Step {i+1} failed: {result.get('error')}"
                    }
            
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.now()
            
            return {
                "success": True,
                "workflow": workflow.to_dict(),
                "results": workflow.results
            }
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            return {
                "success": False,
                "error": str(e),
                "workflow": workflow.to_dict()
            }
        
        finally:
            # Move to history
            self.workflow_history.append(workflow)
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
    
    # ============ Predefined Complex Workflows ============
    
    async def pentest_workflow(self, target: str) -> Dict[str, Any]:
        """
        Complete penetration testing workflow:
        1. Network scan → 2. Vulnerability scan → 3. Exploit research → 4. Report
        """
        steps = [
            {
                "agent_type": "security_agent",
                "task_type": "network_scan",
                "description": f"Scan target {target}",
                "context": {"target": target, "scan_type": "full"},
                "critical": False
            },
            {
                "agent_type": "security_agent",
                "task_type": "vulnerability_scan",
                "description": f"Vulnerability scan on {target}",
                "context": {"target": target},
                "critical": False
            },
            {
                "agent_type": "security_agent",
                "task_type": "exploit_search",
                "description": "Search for relevant exploits",
                "context": {},  # Will use previous results
                "critical": False
            },
            {
                "agent_type": "security_agent",
                "task_type": "remediation",
                "description": "Generate remediation advice",
                "context": {},
                "critical": False
            }
        ]
        
        return await self.create_and_run_workflow(
            name="Penetration Test",
            steps=steps,
            context={"target": target}
        )
    
    async def research_and_analyze_workflow(self, topic: str) -> Dict[str, Any]:
        """
        Research workflow:
        1. Search → 2. Codebase analysis → 3. Summarize
        """
        steps = [
            {
                "agent_type": "research_agent",
                "task_type": "web_search",
                "description": f"Research {topic}",
                "context": {"query": topic}
            },
            {
                "agent_type": "research_agent",
                "task_type": "codebase_analysis",
                "description": "Analyze related code",
                "context": {"target": topic}
            },
            {
                "agent_type": "research_agent",
                "task_type": "summarize",
                "description": "Summarize findings",
                "context": {}
            }
        ]
        
        return await self.create_and_run_workflow(
            name="Research & Analysis",
            steps=steps,
            context={"topic": topic}
        )
    
    async def infrastructure_audit_workflow(self) -> Dict[str, Any]:
        """
        Infrastructure audit workflow:
        1. Docker status → 2. Security scan → 3. Performance → 4. Report
        """
        steps = [
            {
                "agent_type": "devops_agent",
                "task_type": "docker",
                "description": "Check Docker containers",
                "context": {"action": "list"}
            },
            {
                "agent_type": "devops_agent",
                "task_type": "docker",
                "description": "Get container stats",
                "context": {"action": "stats"}
            },
            {
                "agent_type": "security_agent",
                "task_type": "security_audit",
                "description": "Run security audit",
                "context": {}
            },
            {
                "agent_type": "devops_agent",
                "task_type": "monitoring",
                "description": "Get performance metrics",
                "context": {"target": "system"}
            }
        ]
        
        return await self.create_and_run_workflow(
            name="Infrastructure Audit",
            steps=steps
        )
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "agents": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "status": a.status.value,
                    "capabilities": a.capabilities
                }
                for a in self.registry.get_all_agents()
            ],
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.workflow_history)
        }
    
    def log(self, message: str):
        """Log a message"""
        print(f"[Orchestrator] {message}")


# Global instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


# Convenience functions
async def run_security_task(task: AgentTask) -> Dict[str, Any]:
    """Quick run a security task"""
    orchestrator = get_orchestrator()
    return await orchestrator.execute_task(task)


async def run_devops_task(task: AgentTask) -> Dict[str, Any]:
    """Quick run a DevOps task"""
    orchestrator = get_orchestrator()
    return await orchestrator.execute_task(task)


async def run_research_task(task: AgentTask) -> Dict[str, Any]:
    """Quick run a research task"""
    orchestrator = get_orchestrator()
    return await orchestrator.execute_task(task)


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing Agent Orchestrator ===\n")
    
    async def test():
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        print("Orchestrator Status:")
        status = orchestrator.get_status()
        print(f"  Agents: {len(status['agents'])}")
        for agent in status['agents']:
            print(f"    - {agent['name']}: {agent['status']}")
        
        print("\n--- Testing Single Task ---")
        
        # Test a single task
        task = create_task(
            "Check Docker images",
            "docker_images",
            TaskPriority.NORMAL,
            {}
        )
        
        result = await orchestrator.execute_task(task)
        print(f"Result: {result.get('success')}")
        
        print("\n--- Testing Parallel Execution ---")
        
        # Test parallel execution
        tasks = [
            create_task("List containers", "docker", TaskPriority.NORMAL, {"action": "list"}),
            create_task("List images", "docker", TaskPriority.NORMAL, {"action": "images"}),
            create_task("Docker stats", "docker", TaskPriority.NORMAL, {"action": "stats"})
        ]
        
        results = await orchestrator.execute_parallel(tasks)
        print(f"Parallel results: {len(results)} completed")
        
        print("\n--- Testing Infrastructure Audit Workflow ---")
        
        # Test workflow
        workflow_result = await orchestrator.infrastructure_audit_workflow()
        print(f"Workflow success: {workflow_result.get('success')}")
        print(f"Steps completed: {len(workflow_result.get('results', []))}")
    
    asyncio.run(test())

