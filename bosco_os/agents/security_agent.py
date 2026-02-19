"""
Bosco Core - Security Agent
Specialized agent for security operations, vulnerability assessment, and penetration testing
"""

import os
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from bosco_os.agents.base_agent import BaseAgent, AgentTask, AgentStatus, TaskPriority


class SecurityAgent(BaseAgent):
    """
    Specialized security agent for:
    - Network scanning and reconnaissance
    - Vulnerability assessment
    - Exploit research
    - Security auditing
    - Penetration testing automation
    """
    
    def __init__(self, llm_client=None):
        super().__init__(
            agent_id="security_agent",
            name="Security Agent",
            description="Advanced security operations and vulnerability assessment",
            capabilities=[
                "network_scan",
                "vulnerability_scan",
                "exploit_research",
                "port_analysis",
                "service_enumeration",
                "security_audit",
                "threat_detection",
                "remediation_advice"
            ],
            llm_client=llm_client
        )
        
        # Security-specific configuration
        self.config.update({
            "nmap_args": "-sV -sC -O",
            "max_scan_targets": 10,
            "scan_timeout": 300,
            "exploit_db_path": "/usr/share/exploitdb"
        })
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this agent can handle the task"""
        security_types = [
            "network_scan", "vulnerability_scan", "exploit_search",
            "port_analysis", "security_audit", "penetration_test",
            "threat_detection", "remediation"
        ]
        return task.task_type in security_types
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a security task"""
        self.log(f"Executing security task: {task.task_type}")
        
        if task.task_type == "network_scan":
            return await self._network_scan(task)
        elif task.task_type == "vulnerability_scan":
            return await self._vulnerability_scan(task)
        elif task.task_type == "exploit_search":
            return await self._exploit_search(task)
        elif task.task_type == "port_analysis":
            return await self._port_analysis(task)
        elif task.task_type == "security_audit":
            return await self._security_audit(task)
        elif task.task_type == "threat_detection":
            return await self._threat_detection(task)
        elif task.task_type == "remediation":
            return await self._remediation_advice(task)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}
    
    async def _network_scan(self, task: AgentTask) -> Dict[str, Any]:
        """Perform network scanning"""
        target = task.context.get("target", "localhost")
        scan_type = task.context.get("scan_type", "basic")
        
        self.log(f"Scanning target: {target}")
        
        nmap_args = {
            "basic": "-sV",
            "quick": "-F",
            "stealth": "-sS -T stealth",
            "full": "-A -p-",
            " UDP": "-sU",
            "aggressive": "-sC -sV -O --script=vuln"
        }
        
        args = nmap_args.get(scan_type, "-sV")
        cmd = f"nmap {args} {target}"
        
        result = await self._run_command(cmd, timeout=self.config["scan_timeout"])
        
        # Parse results
        parsed = self._parse_nmap_output(result["output"])
        
        return {
            "target": target,
            "scan_type": scan_type,
            "raw_output": result["output"],
            "parsed_results": parsed,
            "open_ports": parsed.get("open_ports", []),
            "services": parsed.get("services", []),
            "os_guess": parsed.get("os_guess", "Unknown")
        }
    
    async def _vulnerability_scan(self, task: AgentTask) -> Dict[str, Any]:
        """Perform vulnerability scanning"""
        target = task.context.get("target", "localhost")
        
        self.log(f"Vulnerability scanning: {target}")
        
        # Run nmap with vuln scripts
        cmd = f"nmap --script=vuln -sV {target}"
        result = await self._run_command(cmd, timeout=self.config["scan_timeout"])
        
        # Parse vulnerabilities
        vulns = self._parse_vulnerabilities(result["output"])
        
        return {
            "target": target,
            "vulnerabilities": vulns,
            "severity_counts": {
                "critical": len([v for v in vulns if v.get("severity") == "critical"]),
                "high": len([v for v in vulns if v.get("severity") == "high"]),
                "medium": len([v for v in vulns if v.get("severity") == "medium"]),
                "low": len([v for v in vulns if v.get("severity") == "low"])
            },
            "raw_output": result["output"]
        }
    
    async def _exploit_search(self, task: AgentTask) -> Dict[str, Any]:
        """Search for exploits"""
        keyword = task.context.get("keyword", "")
        service = task.context.get("service", "")
        cve = task.context.get("cve", "")
        
        search_term = keyword or service or cve
        if not search_term:
            return {"error": "No search term provided"}
        
        self.log(f"Searching exploits for: {search_term}")
        
        # Try searchsploit
        cmd = f"searchsploit {search_term} --json"
        result = await self._run_command(cmd, timeout=30)
        
        exploits = []
        try:
            import json
            data = json.loads(result["output"])
            exploits = data.get("RESULTS", [])
        except:
            # Fallback to text parsing
            for line in result["output"].split("\n"):
                if "/" in line and "exploitdb" not in line.lower():
                    exploits.append({"description": line.strip()})
        
        return {
            "search_term": search_term,
            "exploits_found": len(exploits),
            "exploits": exploits[:10],  # Limit to top 10
            "has_cve": cve != ""
        }
    
    async def _port_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze open ports"""
        target = task.context.get("target", "localhost")
        
        # Quick port scan
        cmd = f"nmap -sV -p- {target}"
        result = await self._run_command(cmd, timeout=180)
        
        ports = self._parse_ports(result["output"])
        
        # Generate risk assessment
        risk_assessment = self._assess_port_risk(ports)
        
        return {
            "target": target,
            "open_ports": ports,
            "risk_assessment": risk_assessment,
            "recommendations": risk_assessment.get("recommendations", [])
        }
    
    async def _security_audit(self, task: AgentTask) -> Dict[str, Any]:
        """Perform comprehensive security audit"""
        self.log("Starting security audit...")
        
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # Check 1: Open ports
        cmd = "nmap -sV localhost"
        result = await self._run_command(cmd, timeout=60)
        audit_results["checks"].append({
            "name": "Open Ports",
            "status": "completed",
            "findings": self._parse_ports(result["output"])
        })
        
        # Check 2: Service versions
        audit_results["checks"].append({
            "name": "Service Analysis",
            "status": "completed",
            "findings": self._analyze_services(result["output"])
        })
        
        # Check 3: Common vulnerabilities
        cmd = "nmap --script=vuln localhost"
        result = await self._run_command(cmd, timeout=90)
        audit_results["checks"].append({
            "name": "Vulnerability Check",
            "status": "completed",
            "findings": self._parse_vulnerabilities(result["output"])
        })
        
        # Overall score
        audit_results["overall_score"] = self._calculate_security_score(audit_results["checks"])
        
        return audit_results
    
    async def _threat_detection(self, task: AgentTask) -> Dict[str, Any]:
        """Detect potential threats"""
        log_path = task.context.get("log_path", "/var/log")
        
        self.log("Analyzing system for threats...")
        
        threats = []
        
        # Check auth logs for failed attempts
        cmd = "sudo tail -100 /var/log/auth.log | grep -i failed"
        result = await self._run_command(cmd, timeout=10)
        failed_logins = result["output"].count("Failed")
        
        if failed_logins > 10:
            threats.append({
                "type": "brute_force",
                "severity": "high",
                "count": failed_logins,
                "message": f"Detected {failed_logins} failed login attempts"
            })
        
        # Check for suspicious processes
        cmd = "ps aux | grep -E '(nc|netcat|nmap|metasploit)'"
        result = await self._run_command(cmd, timeout=10)
        if result["output"]:
            threats.append({
                "type": "suspicious_process",
                "severity": "medium",
                "message": "Suspicious security tools running",
                "details": result["output"]
            })
        
        return {
            "threats_detected": len(threats),
            "threats": threats,
            "recommendations": self._generate_threat_recommendations(threats)
        }
    
    async def _remediation_advice(self, task: AgentTask) -> Dict[str, Any]:
        """Provide remediation advice"""
        vulnerability = task.context.get("vulnerability", {})
        
        # Generate advice based on vulnerability type
        advice = []
        
        vuln_type = vulnerability.get("type", "")
        
        if "outdated" in vuln_type.lower() or "version" in vuln_type.lower():
            advice.append({
                "priority": "high",
                "action": "Update software",
                "description": "Update to the latest version of the affected software"
            })
        
        if "open" in vuln_type.lower() and "port" in vuln_type.lower():
            advice.append({
                "priority": "high",
                "action": "Close unnecessary ports",
                "description": "Close ports that are not required for business operations"
            })
        
        if "weak" in vuln_type.lower() or "default" in vuln_type.lower():
            advice.append({
                "priority": "critical",
                "action": "Change credentials",
                "description": "Change default or weak passwords immediately"
            })
        
        # Default advice
        if not advice:
            advice.append({
                "priority": "medium",
                "action": "General hardening",
                "description": "Follow security best practices and keep systems updated"
            })
        
        return {
            "vulnerability": vulnerability,
            "remediation_steps": advice,
            "references": [
                "https://owasp.org/www-project-top-ten/",
                "https://nvd.nist.gov/"
            ]
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
    
    def _parse_nmap_output(self, output: str) -> Dict[str, Any]:
        """Parse nmap output"""
        result = {
            "open_ports": [],
            "services": [],
            "os_guess": "Unknown"
        }
        
        # Extract open ports
        for line in output.split("\n"):
            if "/tcp" in line or "/udp" in line:
                parts = line.split()
                if len(parts) >= 3:
                    port = parts[0]
                    state = parts[1]
                    if state == "open":
                        service = " ".join(parts[2:])
                        result["open_ports"].append(port)
                        result["services"].append({"port": port, "service": service})
        
        # OS detection
        if "OS details" in output:
            match = re.search(r"OS details: (.+)", output)
            if match:
                result["os_guess"] = match.group(1)
        
        return result
    
    def _parse_ports(self, output: str) -> List[Dict]:
        """Parse port information"""
        ports = []
        
        for line in output.split("\n"):
            if "/tcp" in line or "/udp" in line:
                parts = line.split()
                if len(parts) >= 3:
                    port = parts[0]
                    state = parts[1]
                    service = " ".join(parts[2:])
                    
                    ports.append({
                        "port": port,
                        "state": state,
                        "service": service,
                        "risk_level": self._get_port_risk(port)
                    })
        
        return ports
    
    def _parse_vulnerabilities(self, output: str) -> List[Dict]:
        """Parse vulnerability information"""
        vulns = []
        
        # Simple CVE pattern matching
        cve_pattern = r"CVE-\d{4}-\d{4,}"
        for match in re.finditer(cve_pattern, output):
            vulns.append({
                "type": "cve",
                "id": match.group(),
                "severity": "unknown"
            })
        
        # Check for known vuln patterns
        vuln_patterns = {
            "critical": [r"remote code execution", r"rce",r"sql injection"],
            "high": [r"xss", r"cross-site scripting", r"csrf"],
            "medium": [r"information disclosure", r"path traversal"],
            "low": [r"weak cipher", r"missing header"]
        }
        
        for line in output.split("\n"):
            for severity, patterns in vuln_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulns.append({
                            "type": "pattern",
                            "severity": severity,
                            "description": line.strip()
                        })
        
        return vulns
    
    def _analyze_services(self, output: str) -> List[Dict]:
        """Analyze running services"""
        services = []
        
        for line in output.split("\n"):
            if "open" in line and ("tcp" in line or "udp" in line):
                # Extract service info
                match = re.search(r"(\d+)/(tcp|udp)\s+\w+\s+(.+)", line)
                if match:
                    port, proto, service = match.groups()
                    services.append({
                        "port": port,
                        "protocol": proto,
                        "name": service,
                        "is_common": self._is_common_service(service)
                    })
        
        return services
    
    def _assess_port_risk(self, ports: List[Dict]) -> Dict[str, Any]:
        """Assess risk level of open ports"""
        high_risk_ports = [21, 23, 445, 3389, 5900]
        medium_risk_ports = [22, 80, 443, 8080, 3306, 5432]
        
        high_risk = []
        medium_risk = []
        low_risk = []
        
        for port_info in ports:
            port = int(port_info.get("port", "0").split("/")[0])
            
            if port in high_risk_ports:
                high_risk.append(port_info)
            elif port in medium_risk_ports:
                medium_risk.append(port_info)
            else:
                low_risk.append(port_info)
        
        recommendations = []
        
        if high_risk:
            recommendations.append("CRITICAL: Review and secure high-risk open ports")
        if medium_risk:
            recommendations.append("Consider restricting access to medium-risk ports")
        
        return {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "recommendations": recommendations
        }
    
    def _get_port_risk(self, port: str) -> str:
        """Get risk level for a port"""
        port_num = int(port.split("/")[0])
        
        high_risk = [21, 23, 445, 3389, 5900, 31337]
        medium_risk = [22, 23, 80, 443, 8080, 3306, 5432, 27017]
        
        if port_num in high_risk:
            return "high"
        elif port_num in medium_risk:
            return "medium"
        return "low"
    
    def _is_common_service(self, service: str) -> bool:
        """Check if service is commonly used"""
        common = ["http", "https", "ssh", "ftp", "smtp", "mysql", "postgres", "redis"]
        return any(c in service.lower() for c in common)
    
    def _calculate_security_score(self, checks: List[Dict]) -> int:
        """Calculate overall security score (0-100)"""
        score = 100
        
        for check in checks:
            findings = check.get("findings", [])
            
            if isinstance(findings, dict):
                # Count vulnerabilities
                if "vulnerabilities" in findings:
                    vulns = findings["vulnerabilities"]
                    score -= len(vulns) * 5
                elif "open_ports" in findings:
                    score -= len(findings["open_ports"]) * 2
        
        return max(0, min(100, score))
    
    def _generate_threat_recommendations(self, threats: List[Dict]) -> List[str]:
        """Generate recommendations based on detected threats"""
        recommendations = []
        
        for threat in threats:
            threat_type = threat.get("type", "")
            
            if threat_type == "brute_force":
                recommendations.append("Enable fail2ban or similar intrusion prevention")
                recommendations.append("Implement rate limiting on login endpoints")
                recommendations.append("Use strong, unique passwords")
            
            elif threat_type == "suspicious_process":
                recommendations.append("Investigate suspicious processes immediately")
                recommendations.append("Check if authorized security testing")
        
        if not recommendations:
            recommendations.append("Continue monitoring for suspicious activity")
        
        return recommendations


# Global instance
_security_agent: Optional[SecurityAgent] = None


def get_security_agent(llm_client=None) -> SecurityAgent:
    """Get the security agent instance"""
    global _security_agent
    if _security_agent is None:
        _security_agent = SecurityAgent(llm_client)
    return _security_agent


if __name__ == "__main__":
    # Test the security agent
    import asyncio
    
    print("=== Testing Security Agent ===\n")
    
    async def test():
        agent = SecurityAgent()
        
        # Test exploit search
        task = AgentTask(
            description="Search for Apache exploits",
            task_type="exploit_search",
            context={"keyword": "apache"}
        )
        
        result = await agent.run(task)
        print("Exploit Search Result:")
        print(f"  Exploits found: {result.get('result', {}).get('exploits_found', 0)}")
    
    asyncio.run(test())

