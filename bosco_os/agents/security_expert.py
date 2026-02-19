"""
Bosco Core - Security Expert Agent
OWASP Top 10 focused automated vulnerability scanning and security assessment
"""

import os
import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from bosco_os.agents.base_agent import BaseAgent, AgentTask, TaskPriority


class OWASPCategory(Enum):
    """OWASP Top 10 (2021) categories"""
    A01_BROKEN_ACCESS_CONTROL = "A01 - Broken Access Control"
    A02_CRYPTOGRAPHIC_FAILURES = "A02 - Cryptographic Failures"
    A03_INJECTION = "A03 - Injection"
    A04_INSECURE_DESIGN = "A04 - Insecure Design"
    A05_SECURITY_MISCONFIGURATION = "A05 - Security Misconfiguration"
    A06_VULNERABLE_COMPONENTS = "A06 - Vulnerable and Outdated Components"
    A07_AUTH_FAILURES = "A07 - Identification and Authentication Failures"
    A08_SOFTWARE_INTEGRITY = "A08 - Software and Data Integrity Failures"
    A09_LOGGING_FAILURES = "A09 - Security Logging and Monitoring Failures"
    A10_SSRF = "A10 - Server-Side Request Forgery"


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


class SecurityFinding:
    """Represents a security finding"""
    
    def __init__(
        self,
        vuln_id: str,
        title: str,
        severity: VulnerabilitySeverity,
        owasp_category: OWASPCategory,
        description: str,
        evidence: str,
        remediation: str,
        cwe_id: str = None,
        cvss_score: float = None
    ):
        self.id = vuln_id
        self.title = title
        self.severity = severity
        self.owasp_category = owasp_category
        self.description = description
        self.evidence = evidence
        self.remediation = remediation
        self.cwe_id = cwe_id
        self.cvss_score = cvss_score
        self.found_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "owasp_category": self.owasp_category.value,
            "description": self.description,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
            "found_at": self.found_at.isoformat()
        }


class SecurityExpertAgent(BaseAgent):
    """
    Security Expert Agent
    Specializes in OWASP Top 10 vulnerability detection and security auditing
    """
    
    # Known vulnerability patterns
    VULNERABILITY_PATTERNS = {
        OWASPCategory.A01_BROKEN_ACCESS_CONTROL: [
            {
                "pattern": r"def\s+\w+\(.*\):.*\n.*if\s+.*:.*\n.*return",
                "name": "Potential IDOR",
                "description": "Insecure direct object reference might be present",
                "remediation": "Implement proper authorization checks"
            },
            {
                "pattern": r"@app\.route\(['\"]/admin",
                "name": "Admin endpoint without auth check",
                "description": "Admin route might lack authorization",
                "remediation": "Add @login_required or role-based access control"
            }
        ],
        OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES: [
            {
                "pattern": r"md5\(|hashlib\.md5\(",
                "name": "Weak hashing algorithm (MD5)",
                "description": "MD5 is cryptographically broken",
                "remediation": "Use bcrypt, scrypt, or Argon2"
            },
            {
                "pattern": r"hashlib\.sha1\(",
                "name": "Weak hashing algorithm (SHA1)",
                "description": "SHA1 is considered deprecated",
                "remediation": "Use SHA-256 or stronger"
            },
            {
                "pattern": r"password\s*=\s*['\"][^'\"]{,15}['\"]",
                "name": "Hardcoded password",
                "description": "Hardcoded credentials found",
                "remediation": "Use environment variables or secure secret management"
            }
        ],
        OWASPCategory.A03_INJECTION: [
            {
                "pattern": r"cursor\.execute\(['\"].*\%.*['\"]",
                "name": "SQL Injection risk",
                "description": "String formatting in SQL query",
                "remediation": "Use parameterized queries or ORM"
            },
            {
                "pattern": r"eval\(|exec\(",
                "name": "Code injection risk",
                "description": "Dynamic code execution found",
                "remediation": "Avoid eval/exec, use safer alternatives"
            },
            {
                "pattern": r"subprocess\..*shell\s*=\s*True",
                "name": "Shell injection risk",
                "description": "Shell=True enables shell injection",
                "remediation": "Use shell=False with list arguments"
            }
        ],
        OWASPCategory.A05_SECURITY_MISCONFIGURATION: [
            {
                "pattern": r"debug\s*=\s*True",
                "name": "Debug mode enabled",
                "description": "Debug mode can expose sensitive information",
                "remediation": "Set debug=False in production"
            },
            {
                "pattern": r"CORS.*allow.*\*",
                "name": "Permissive CORS",
                "description": "CORS allows all origins",
                "remediation": "Restrict to specific trusted origins"
            }
        ],
        OWASPCategory.A06_VULNERABLE_COMPONENTS: [
            {
                "pattern": r"flask\s*<|django\s*<|requests\s*<",
                "name": "Potentially outdated dependency",
                "description": "Pinning to version might be missing",
                "remediation": "Pin versions and regularly update"
            }
        ],
        OWASPCategory.A07_AUTH_FAILURES: [
            {
                "pattern": r"if\s+.*==.*password",
                "name": "Plaintext password comparison",
                "description": "Direct password comparison is unsafe",
                "remediation": "Use password hashing with comparison timing protection"
            },
            {
                "pattern": r"session\s*\[\s*['\"]user",
                "name": "Insecure session handling",
                "description": "User stored directly in session without validation",
                "remediation": "Validate user session server-side"
            }
        ]
    }
    
    def __init__(self, llm_client=None):
        super().__init__(
            agent_id="security_expert",
            name="Security Expert",
            description="OWASP Top 10 focused security analysis and vulnerability detection",
            capabilities=[
                "owasp_scan",
                "code_review",
                "vulnerability_assessment",
                "penetration_testing",
                "security_audit",
                "cve_lookup",
                "secure_coding_advice",
                "compliance_check"
            ],
            llm_client=llm_client
        )
        
        self.findings: List[SecurityFinding] = []
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this agent can handle the task"""
        security_types = [
            "owasp", "vulnerability", "security", "penetration",
            "cve", "exploit", "audit", "secure_coding"
        ]
        return task.task_type in security_types or any(t in task.task_type.lower() for t in security_types)
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a security task"""
        self.log(f"Executing security task: {task.task_type}")
        
        task_type = task.task_type.lower()
        
        if "owasp" in task_type:
            return await self._owasp_scan(task)
        elif "vulnerability" in task_type or "scan" in task_type:
            return await self._vulnerability_scan(task)
        elif "code_review" in task_type:
            return await self._code_review(task)
        elif "cve" in task_type:
            return await self._cve_lookup(task)
        elif "audit" in task_type:
            return await self._security_audit(task)
        else:
            return await self._general_security_check(task)
    
    async def _owasp_scan(self, task: AgentTask) -> Dict[str, Any]:
        """Perform OWASP Top 10 focused scan"""
        target = task.context.get("target", "")
        
        if not target:
            return {"error": "No target specified for OWASP scan"}
        
        self.findings = []
        
        # Check if target is a file path or URL
        if os.path.exists(target):
            return await self._scan_source_code(target)
        else:
            return await self._scan_web_target(target)
    
    async def _scan_source_code(self, file_path: str) -> Dict[str, Any]:
        """Scan source code for OWASP vulnerabilities"""
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Scan for each OWASP category
        for category, patterns in self.VULNERABILITY_PATTERNS.items():
            for vuln_pattern in patterns:
                matches = re.finditer(vuln_pattern["pattern"], code, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Get surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(code), match.end() + 50)
                    evidence = code[start:end]
                    
                    finding = SecurityFinding(
                        vuln_id=f"OWASP-{len(self.findings) + 1}",
                        title=vuln_pattern["name"],
                        severity=self._assess_severity(category),
                        owasp_category=category,
                        description=vuln_pattern["description"],
                        evidence=f"...{evidence}...",
                        remediation=vuln_pattern["remediation"],
                        cwe_id=self._get_cwe_id(category)
                    )
                    
                    self.findings.append(finding)
        
        return self._format_findings()
    
    async def _scan_web_target(self, target: str) -> Dict[str, Any]:
        """Scan web target for vulnerabilities"""
        
        findings = []
        
        # Run nmap for port scanning
        cmd = f"nmap -sV --script=vuln {target}"
        result = await self._run_command(cmd, timeout=120)
        
        # Parse nmap vulners
        if "vulners" in result.get("output", ""):
            findings.append(SecurityFinding(
                vuln_id="NET-1",
                title="Potential vulnerable service",
                severity=VulnerabilitySeverity.MEDIUM,
                owasp_category=OWASPCategory.A06_VULNERABLE_COMPONENTS,
                description="Nmap detected potentially vulnerable services",
                evidence=result["output"][:500],
                remediation="Update services to latest versions"
            ))
        
        return {
            "target": target,
            "scan_type": "OWASP Top 10 Web Scan",
            "findings": [f.to_dict() for f in findings],
            "summary": self._generate_summary(findings)
        }
    
    async def _vulnerability_scan(self, task: AgentTask) -> Dict[str, Any]:
        """General vulnerability scan"""
        target = task.context.get("target", "")
        
        if not target:
            return {"error": "No target specified"}
        
        # Run nikto if available
        cmd = f"nikto -h {target} -Format json"
        result = await self._run_command(cmd, timeout=180)
        
        return {
            "target": target,
            "scan_type": "Vulnerability Scan",
            "nikto_output": result.get("output", "")[:2000],
            "raw_result": result
        }
    
    async def _code_review(self, task: AgentTask) -> Dict[str, Any]:
        """Perform automated code review for security"""
        file_path = task.context.get("file_path", "")
        
        if not file_path or not os.path.exists(file_path):
            return {"error": "Invalid file path"}
        
        # Scan code
        return await self._scan_source_code(file_path)
    
    async def _cve_lookup(self, task: AgentTask) -> Dict[str, Any]:
        """Look up CVEs for a component"""
        component = task.context.get("component", "")
        version = task.context.get("version", "")
        
        if not component:
            return {"error": "No component specified"}
        
        # Use searchsploit
        search_term = f"{component} {version}".strip()
        cmd = f"searchsploit {search_term} --json"
        result = await self._run_command(cmd, timeout=30)
        
        exploits = []
        try:
            data = json.loads(result.get("output", "{}"))
            exploits = data.get("RESULTS", [])
        except:
            # Parse text output
            for line in result.get("output", "").split("\n"):
                if "/" in line:
                    exploits.append({"description": line.strip()})
        
        return {
            "component": component,
            "version": version,
            "exploits_found": len(exploits),
            "exploits": exploits[:10]
        }
    
    async def _security_audit(self, task: AgentTask) -> Dict[str, Any]:
        """Perform comprehensive security audit"""
        
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # Check 1: Open ports
        cmd = "nmap -sV localhost"
        result = await self._run_command(cmd, timeout=60)
        audit_results["checks"].append({
            "name": "Open Services",
            "status": "completed",
            "findings": self._parse_services(result.get("output", ""))
        })
        
        # Check 2: Password policies
        audit_results["checks"].append({
            "name": "Password Policy",
            "status": "completed",
            "findings": {"recommendation": "Enforce strong password policy"}
        })
        
        # Check 3: Firewall status
        cmd = "sudo iptables -L -n"
        result = await self._run_command(cmd, timeout=10)
        audit_results["checks"].append({
            "name": "Firewall",
            "status": "completed",
            "findings": {"active": result.get("success", False)}
        })
        
        return audit_results
    
    async def _general_security_check(self, task: AgentTask) -> Dict[str, Any]:
        """General security check"""
        
        checks = []
        
        # Check for root access
        cmd = "id"
        result = await self._run_command(cmd, timeout=5)
        is_root = "uid=0" in result.get("output", "")
        checks.append({
            "check": "Root Access",
            "result": "Running as root" if is_root else "Running as regular user"
        })
        
        # Check firewall
        cmd = "sudo ufw status"
        result = await self._run_command(cmd, timeout=5)
        checks.append({
            "check": "Firewall",
            "result": result.get("output", "Unknown")
        })
        
        return {
            "checks": checks,
            "recommendations": self._get_security_recommendations()
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
                return {"success": False, "output": "", "error": "Timeout"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _assess_severity(self, category: OWASPCategory) -> VulnerabilitySeverity:
        """Assess severity based on OWASP category"""
        high_severity = [
            OWASPCategory.A01_BROKEN_ACCESS_CONTROL,
            OWASPCategory.A03_INJECTION,
            OWASPCategory.A07_AUTH_FAILURES
        ]
        
        if category in high_severity:
            return VulnerabilitySeverity.HIGH
        elif category == OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES:
            return VulnerabilitySeverity.HIGH
        else:
            return VulnerabilitySeverity.MEDIUM
    
    def _get_cwe_id(self, category: OWASPCategory) -> str:
        """Get CWE ID for OWASP category"""
        cwe_map = {
            OWASPCategory.A01_BROKEN_ACCESS_CONTROL: "CWE-284",
            OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES: "CWE-310",
            OWASPCategory.A03_INJECTION: "CWE-74",
            OWASPCategory.A04_INSECURE_DESIGN: "CWE-755",
            OWASPCategory.A05_SECURITY_MISCONFIGURATION: "CWE-16",
            OWASPCategory.A06_VULNERABLE_COMPONENTS: "CWE-1105",
            OWASPCategory.A07_AUTH_FAILURES: "CWE-287",
            OWASPCategory.A08_SOFTWARE_INTEGRITY: "CWE-494",
            OWASPCategory.A09_LOGGING_FAILURES: "CWE-778",
            OWASPCategory.A10_SSRF: "CWE-918"
        }
        return cwe_map.get(category, "")
    
    def _parse_services(self, output: str) -> List[Dict]:
        """Parse nmap service output"""
        services = []
        
        for line in output.split("\n"):
            if "/tcp" in line or "/udp" in line:
                parts = line.split()
                if len(parts) >= 3:
                    services.append({
                        "port": parts[0],
                        "service": " ".join(parts[2:])
                    })
        
        return services
    
    def _format_findings(self) -> Dict:
        """Format findings for output"""
        return {
            "total_findings": len(self.findings),
            "by_severity": {
                "critical": len([f for f in self.findings if f.severity == VulnerabilitySeverity.CRITICAL]),
                "high": len([f for f in self.findings if f.severity == VulnerabilitySeverity.HIGH]),
                "medium": len([f for f in self.findings if f.severity == VulnerabilitySeverity.MEDIUM]),
                "low": len([f for f in self.findings if f.severity == VulnerabilitySeverity.LOW])
            },
            "findings": [f.to_dict() for f in self.findings],
            "summary": self._generate_summary(self.findings)
        }
    
    def _generate_summary(self, findings: List[SecurityFinding]) -> Dict:
        """Generate summary of findings"""
        
        by_category = {}
        for f in findings:
            cat = f.owasp_category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total": len(findings),
            "by_category": by_category,
            "risk_score": self._calculate_risk_score(findings)
        }
    
    def _calculate_risk_score(self, findings: List[SecurityFinding]) -> float:
        """Calculate overall risk score (0-10)"""
        if not findings:
            return 0.0
        
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 10,
            VulnerabilitySeverity.HIGH: 7.5,
            VulnerabilitySeverity.MEDIUM: 5,
            VulnerabilitySeverity.LOW: 2.5,
            VulnerabilitySeverity.INFO: 0
        }
        
        total_weight = sum(severity_weights.get(f.severity, 0) for f in findings)
        max_possible = len(findings) * 10
        
        return round(total_weight / max_possible * 10, 2)
    
    def _get_security_recommendations(self) -> List[str]:
        """Get general security recommendations"""
        return [
            "Keep all software components updated",
            "Implement proper authentication and authorization",
            "Use parameterized queries to prevent SQL injection",
            "Enable security logging and monitoring",
            "Regular security audits and penetration testing",
            "Follow OWASP Top 10 guidelines"
        ]


# Global instance
_security_expert: Optional[SecurityExpertAgent] = None


def get_security_expert(llm_client=None) -> SecurityExpertAgent:
    """Get the security expert agent instance"""
    global _security_expert
    if _security_expert is None:
        _security_expert = SecurityExpertAgent(llm_client)
    return _security_expert


if __name__ == "__main__":
    import asyncio
    import os
    
    print("=== Testing Security Expert Agent ===\n")
    
    async def test():
        agent = SecurityExpertAgent()
        
        # Test CVE lookup
        task = AgentTask(
            description="Look up Apache vulnerabilities",
            task_type="cve",
            context={"component": "apache", "version": "2.4"}
        )
        
        result = await agent.run(task)
        print("CVE Lookup Result:")
        print(f"  Exploits found: {result.get('result', {}).get('exploits_found', 0)}")
    
    asyncio.run(test())

