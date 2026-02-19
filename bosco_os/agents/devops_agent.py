"""
Bosco Core - DevOps Agent
Specialized agent for DevOps, infrastructure management, and container orchestration
"""

import os
import subprocess
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from bosco_os.agents.base_agent import BaseAgent, AgentTask, AgentStatus, TaskPriority


class DevOpsAgent(BaseAgent):
    """
    Specialized DevOps agent for:
    - Docker container management
    - Kubernetes operations
    - Infrastructure deployment
    - CI/CD pipeline management
    - System monitoring
    - Log analysis
    """
    
    def __init__(self, llm_client=None):
        super().__init__(
            agent_id="devops_agent",
            name="DevOps Agent",
            description="Infrastructure management and DevOps automation",
            capabilities=[
                "docker_management",
                "container_operations",
                "image_management",
                "kubernetes_ops",
                "deployment",
                "infrastructure_status",
                "log_analysis",
                "performance_monitoring",
                "backup_operations"
            ],
            llm_client=llm_client
        )
        
        self.config.update({
            "docker_timeout": 60,
            "default_registry": "docker.io",
            "max_containers": 50
        })
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this agent can handle the task"""
        devops_types = [
            "docker", "container", "kubernetes", "k8s",
            "deployment", "infrastructure", "ci_cd",
            "backup", "monitoring", "logs", "performance"
        ]
        return task.task_type in devops_types or any(t in task.task_type.lower() for t in devops_types)
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a DevOps task"""
        self.log(f"Executing DevOps task: {task.task_type}")
        
        task_type = task.task_type.lower()
        
        if "docker" in task_type or "container" in task_type:
            return await self._docker_operation(task)
        elif "kubernetes" in task_type or "k8s" in task_type:
            return await self._kubernetes_operation(task)
        elif "deploy" in task_type:
            return await self._deployment_operation(task)
        elif "backup" in task_type:
            return await self._backup_operation(task)
        elif "monitor" in task_type or "performance" in task_type:
            return await self._monitoring(task)
        elif "log" in task_type:
            return await self._log_analysis(task)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}
    
    async def _docker_operation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle Docker operations"""
        action = task.context.get("action", "list")
        
        if action == "list" or action == "ps":
            return await self._docker_list_containers(task)
        elif action == "start":
            return await self._docker_start_container(task)
        elif action == "stop":
            return await self._docker_stop_container(task)
        elif action == "remove" or action == "rm":
            return await self._docker_remove_container(task)
        elif action == "logs":
            return await self._docker_logs(task)
        elif action == "stats":
            return await self._docker_stats(task)
        elif action == "images":
            return await self._docker_images(task)
        elif action == "pull":
            return await self._docker_pull_image(task)
        elif action == "run":
            return await self._docker_run(task)
        elif action == "exec":
            return await self._docker_exec(task)
        elif action == "compose":
            return await self._docker_compose(task)
        else:
            return {"error": f"Unknown Docker action: {action}"}
    
    async def _docker_list_containers(self, task: AgentTask) -> Dict[str, Any]:
        """List Docker containers"""
        all_containers = task.context.get("all", False)
        
        cmd = "docker ps -a" if all_containers else "docker ps"
        cmd += " --format '{{json .}}'"
        
        result = await self._run_command(cmd)
        
        containers = []
        for line in result.get("output", "").split("\n"):
            if line.strip():
                try:
                    containers.append(json.loads(line))
                except:
                    pass
        
        return {
            "containers": containers,
            "count": len(containers),
            "running": len([c for c in containers if c.get("State") == "running"])
        }
    
    async def _docker_start_container(self, task: AgentTask) -> Dict[str, Any]:
        """Start a Docker container"""
        container = task.context.get("container", "")
        if not container:
            return {"error": "Container name or ID required"}
        
        cmd = f"docker start {container}"
        result = await self._run_command(cmd)
        
        return {
            "action": "start",
            "container": container,
            "success": result.get("success", False),
            "output": result.get("output", "")
        }
    
    async def _docker_stop_container(self, task: AgentTask) -> Dict[str, Any]:
        """Stop a Docker container"""
        container = task.context.get("container", "")
        if not container:
            return {"error": "Container name or ID required"}
        
        cmd = f"docker stop {container}"
        result = await self._run_command(cmd)
        
        return {
            "action": "stop",
            "container": container,
            "success": result.get("success", False),
            "output": result.get("output", "")
        }
    
    async def _docker_remove_container(self, task: AgentTask) -> Dict[str, Any]:
        """Remove a Docker container"""
        container = task.context.get("container", "")
        force = task.context.get("force", False)
        
        if not container:
            return {"error": "Container name or ID required"}
        
        cmd = f"docker rm {'-f' if force else ''} {container}"
        result = await self._run_command(cmd)
        
        return {
            "action": "remove",
            "container": container,
            "success": result.get("success", False),
            "output": result.get("output", "")
        }
    
    async def _docker_logs(self, task: AgentTask) -> Dict[str, Any]:
        """Get container logs"""
        container = task.context.get("container", "")
        lines = task.context.get("lines", 100)
        tail = task.context.get("tail", False)
        
        if not container:
            return {"error": "Container name or ID required"}
        
        if tail:
            cmd = f"docker logs --tail {lines} {container}"
        else:
            cmd = f"docker logs --tail {lines} {container} 2>&1"
        
        result = await self._run_command(cmd, timeout=30)
        
        return {
            "container": container,
            "lines": lines,
            "logs": result.get("output", "")[-5000:]  # Limit log size
        }
    
    async def _docker_stats(self, task: AgentTask) -> Dict[str, Any]:
        """Get container statistics"""
        container = task.context.get("container", "")
        
        if container:
            cmd = f"docker stats {container} --no-stream --format '{{json .}}'"
        else:
            cmd = "docker stats --no-stream --format '{{json .}}'"
        
        result = await self._run_command(cmd, timeout=10)
        
        stats = []
        for line in result.get("output", "").split("\n"):
            if line.strip():
                try:
                    stats.append(json.loads(line))
                except:
                    pass
        
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _docker_images(self, task: AgentTask) -> Dict[str, Any]:
        """List Docker images"""
        cmd = "docker images --format '{{json .}}'"
        
        result = await self._run_command(cmd)
        
        images = []
        for line in result.get("output", "").split("\n"):
            if line.strip():
                try:
                    images.append(json.loads(line))
                except:
                    pass
        
        return {
            "images": images,
            "count": len(images)
        }
    
    async def _docker_pull_image(self, task: AgentTask) -> Dict[str, Any]:
        """Pull a Docker image"""
        image = task.context.get("image", "")
        tag = task.context.get("tag", "latest")
        
        if not image:
            return {"error": "Image name required"}
        
        full_image = f"{image}:{tag}"
        cmd = f"docker pull {full_image}"
        
        result = await self._run_command(cmd, timeout=300)
        
        return {
            "image": full_image,
            "success": result.get("success", False),
            "output": result.get("output", "")
        }
    
    async def _docker_run(self, task: AgentTask) -> Dict[str, Any]:
        """Run a Docker container"""
        image = task.context.get("image", "")
        name = task.context.get("name", "")
        detach = task.context.get("detach", True)
        ports = task.context.get("ports", [])
        env = task.context.get("env", {})
        volumes = task.context.get("volumes", [])
        
        if not image:
            return {"error": "Image name required"}
        
        # Build command
        cmd_parts = ["docker run"]
        
        if detach:
            cmd_parts.append("-d")
        
        if name:
            cmd_parts.append(f"--name {name}")
        
        for port in ports:
            cmd_parts.append(f"-p {port}")
        
        for key, value in env.items():
            cmd_parts.append(f"-e {key}={value}")
        
        for vol in volumes:
            cmd_parts.append(f"-v {vol}")
        
        cmd_parts.append(image)
        
        cmd = " ".join(cmd_parts)
        result = await self._run_command(cmd, timeout=120)
        
        return {
            "action": "run",
            "image": image,
            "container_name": name,
            "success": result.get("success", False),
            "output": result.get("output", "").strip()
        }
    
    async def _docker_exec(self, task: AgentTask) -> Dict[str, Any]:
        """Execute command in container"""
        container = task.context.get("container", "")
        command = task.context.get("command", "/bin/sh")
        
        if not container:
            return {"error": "Container name or ID required"}
        
        cmd = f"docker exec {container} {command}"
        result = await self._run_command(cmd, timeout=30)
        
        return {
            "container": container,
            "command": command,
            "success": result.get("success", False),
            "output": result.get("output", ""),
            "error": result.get("error", "")
        }
    
    async def _docker_compose(self, task: AgentTask) -> Dict[str, Any]:
        """Docker Compose operations"""
        action = task.context.get("action", "up")
        project_dir = task.context.get("dir", ".")
        detach = task.context.get("detach", True)
        
        cmd = f"cd {project_dir} && docker-compose {action}"
        if detach and action in ["up", "start"]:
            cmd += " -d"
        
        result = await self._run_command(cmd, timeout=180)
        
        return {
            "action": action,
            "directory": project_dir,
            "success": result.get("success", False),
            "output": result.get("output", "")
        }
    
    async def _kubernetes_operation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle Kubernetes operations"""
        action = task.context.get("action", "status")
        
        if action == "pods":
            return await self._k8s_pods(task)
        elif action == "services" or action == "svc":
            return await self._k8s_services(task)
        elif action == "deployments":
            return await self._k8s_deployments(task)
        elif action == "status":
            return await self._k8s_status(task)
        else:
            return {"error": f"Unknown k8s action: {action}"}
    
    async def _k8s_pods(self, task: AgentTask) -> Dict[str, Any]:
        """Get Kubernetes pods"""
        namespace = task.context.get("namespace", "default")
        
        cmd = f"kubectl get pods -n {namespace} -o json"
        result = await self._run_command(cmd, timeout=30)
        
        try:
            data = json.loads(result.get("output", "{}"))
            pods = [
                {
                    "name": p["metadata"]["name"],
                    "status": p["status"]["phase"],
                    "ready": f"{sum([cs == 'True' for cs in p['status'].get('containerStatuses', [])])}/{len(p['status'].get('containerStatuses', []))}",
                    "age": p["metadata"].get("creationTimestamp", "")
                }
                for p in data.get("items", [])
            ]
            return {"pods": pods, "namespace": namespace}
        except:
            return {"error": "Failed to parse kubectl output", "raw": result.get("output", "")}
    
    async def _k8s_services(self, task: AgentTask) -> Dict[str, Any]:
        """Get Kubernetes services"""
        namespace = task.context.get("namespace", "default")
        
        cmd = f"kubectl get svc -n {namespace} -o json"
        result = await self._run_command(cmd, timeout=30)
        
        try:
            data = json.loads(result.get("output", "{}"))
            services = [
                {
                    "name": s["metadata"]["name"],
                    "type": s["spec"]["type"],
                    "cluster_ip": s["spec"].get("clusterIP", ""),
                    "ports": [p["port"] for p in s["spec"].get("ports", [])]
                }
                for s in data.get("items", [])
            ]
            return {"services": services, "namespace": namespace}
        except:
            return {"error": "Failed to parse kubectl output"}
    
    async def _k8s_deployments(self, task: AgentTask) -> Dict[str, Any]:
        """Get Kubernetes deployments"""
        namespace = task.context.get("namespace", "default")
        
        cmd = f"kubectl get deployments -n {namespace} -o json"
        result = await self._run_command(cmd, timeout=30)
        
        try:
            data = json.loads(result.get("output", "{}"))
            deployments = [
                {
                    "name": d["metadata"]["name"],
                    "ready": d["status"].get("readyReplicas", 0),
                    "desired": d["spec"].get("replicas", 0),
                    "age": d["metadata"].get("creationTimestamp", "")
                }
                for d in data.get("items", [])
            ]
            return {"deployments": deployments, "namespace": namespace}
        except:
            return {"error": "Failed to parse kubectl output"}
    
    async def _k8s_status(self, task: AgentTask) -> Dict[str, Any]:
        """Get Kubernetes cluster status"""
        cmd = "kubectl cluster-info"
        result = await self._run_command(cmd, timeout=30)
        
        return {
            "cluster_info": result.get("output", ""),
            "connected": result.get("success", False)
        }
    
    async def _deployment_operation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle deployment operations"""
        deployment_type = task.context.get("type", "docker")
        
        if deployment_type == "docker-compose":
            return await self._docker_compose(task)
        elif deployment_type == "kubernetes":
            return await self._kubernetes_operation(task)
        else:
            return {"error": f"Unknown deployment type: {deployment_type}"}
    
    async def _backup_operation(self, task: AgentTask) -> Dict[str, Any]:
        """Handle backup operations"""
        backup_type = task.context.get("backup_type", "files")
        destination = task.context.get("destination", "/backup")
        source = task.context.get("source", "/data")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if backup_type == "files":
            cmd = f"tar -czf {destination}/backup_{timestamp}.tar.gz {source}"
            result = await self._run_command(cmd, timeout=300)
            
            return {
                "type": "files",
                "source": source,
                "destination": f"{destination}/backup_{timestamp}.tar.gz",
                "success": result.get("success", False)
            }
        
        elif backup_type == "docker":
            # Export all containers
            cmd = "docker ps -aq | xargs -I {} docker commit {} backup:{}".format(timestamp)
            result = await self._run_command(cmd, timeout=300)
            
            return {
                "type": "docker",
                "timestamp": timestamp,
                "success": result.get("success", False)
            }
        
        else:
            return {"error": f"Unknown backup type: {backup_type}"}
    
    async def _monitoring(self, task: AgentTask) -> Dict[str, Any]:
        """System monitoring"""
        target = task.context.get("target", "system")
        
        if target == "system":
            return await self._system_stats(task)
        elif target == "docker":
            return await self._docker_stats(task)
        elif target == "network":
            return await self._network_stats(task)
        else:
            return {"error": f"Unknown monitoring target: {target}"}
    
    async def _system_stats(self, task: AgentTask) -> Dict[str, Any]:
        """Get system statistics"""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _network_stats(self, task: AgentTask) -> Dict[str, Any]:
        """Get network statistics"""
        import psutil
        
        net_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _log_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze logs"""
        log_path = task.context.get("path", "/var/log")
        pattern = task.context.get("pattern", "")
        lines = task.context.get("lines", 100)
        
        if pattern:
            cmd = f"tail -n {lines} {log_path} | grep -i '{pattern}'"
        else:
            cmd = f"tail -n {lines} {log_path}"
        
        result = await self._run_command(cmd, timeout=30)
        
        log_lines = result.get("output", "").split("\n")
        
        # Simple analysis
        errors = [l for l in log_lines if "error" in l.lower()]
        warnings = [l for l in log_lines if "warn" in l.lower()]
        
        return {
            "log_path": log_path,
            "pattern": pattern,
            "total_lines": len(log_lines),
            "errors": len(errors),
            "warnings": len(warnings),
            "sample_lines": log_lines[-20:]
        }
    
    async def _run_command(self, cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a shell command"""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                return {
                    "success": proc.returncode == 0,
                    "output": stdout.decode(),
                    "error": stderr.decode(),
                    "returncode": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "success": False,
                    "output": "",
                    "error": "Command timed out",
                    "returncode": -1
                }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1
            }


# Global instance
_devops_agent: Optional[DevOpsAgent] = None


def get_devops_agent(llm_client=None) -> DevOpsAgent:
    """Get the DevOps agent instance"""
    global _devops_agent
    if _devops_agent is None:
        _devops_agent = DevOpsAgent(llm_client)
    return _devops_agent


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing DevOps Agent ===\n")
    
    async def test():
        agent = DevOpsAgent()
        
        # Test Docker images
        task = AgentTask(
            description="List Docker images",
            task_type="docker_images",
            context={}
        )
        
        result = await agent.run(task)
        print("Docker Images Result:")
        print(f"  Images: {result.get('result', {}).get('count', 0)}")
    
    asyncio.run(test())

