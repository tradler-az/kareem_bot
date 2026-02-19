"""
Bosco Core - Research Agent
Specialized agent for research, information gathering, and analysis
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from bosco_os.agents.base_agent import BaseAgent, AgentTask, AgentStatus, TaskPriority


class ResearchAgent(BaseAgent):
    """
    Specialized research agent for:
    - Web search and information gathering
    - Codebase analysis
    - Documentation lookup
    - Fact checking
    - Topic research
    - Summarization
    """
    
    def __init__(self, llm_client=None):
        super().__init__(
            agent_id="research_agent",
            name="Research Agent",
            description="Research and information gathering specialist",
            capabilities=[
                "web_search",
                "codebase_analysis",
                "documentation_lookup",
                "fact_checking",
                "topic_research",
                "summarization",
                "comparison",
                "trending_topics"
            ],
            llm_client=llm_client
        )
        
        self.config.update({
            "max_search_results": 10,
            "search_timeout": 30,
            "max_code_context": 5000
        })
    
    def can_handle(self, task: AgentTask) -> bool:
        """Check if this agent can handle the task"""
        research_types = [
            "search", "research", "lookup", "find", "analyze",
            "documentation", "fact_check", "summarize", "compare",
            "web", "codebase", "learn", "explain", "what_is", "how_to"
        ]
        return task.task_type in research_types or any(t in task.task_type.lower() for t in research_types)
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a research task"""
        self.log(f"Executing research task: {task.task_type}")
        
        task_type = task.task_type.lower()
        
        if "search" in task_type or "find" in task_type or "lookup" in task_type:
            return await self._web_search(task)
        elif "codebase" in task_type or "code" in task_type:
            return await self._codebase_analysis(task)
        elif "doc" in task_type:
            return await self._documentation_lookup(task)
        elif "fact" in task_type or "verify" in task_type:
            return await self._fact_checking(task)
        elif "summarize" in task_type:
            return await self._summarization(task)
        elif "compare" in task_type:
            return await self._comparison(task)
        elif "explain" in task_type or "what_is" in task_type or "how_to" in task_type:
            return await self._explain_topic(task)
        else:
            return await self._general_research(task)
    
    async def _web_search(self, task: AgentTask) -> Dict[str, Any]:
        """Perform web search"""
        query = task.context.get("query", task.description)
        
        if not query:
            return {"error": "No search query provided"}
        
        self.log(f"Searching for: {query}")
        
        # Try using available search capability
        try:
            from capabilities.web_search import search_web
            results = search_web(query, limit=self.config["max_search_results"])
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
        except ImportError:
            # Fallback to simple search
            return await self._simple_search(query)
    
    async def _simple_search(self, query: str) -> Dict[str, Any]:
        """Simple fallback search using duckduckgo or similar"""
        try:
            import requests
            
            # Use DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get("Answer"):
                results.append({
                    "title": "Instant Answer",
                    "content": data["Answer"],
                    "type": "instant_answer"
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict):
                    results.append({
                        "title": topic.get("Text", "")[:60],
                        "content": topic.get("Text", ""),
                        "url": topic.get("URL", ""),
                        "type": "related"
                    })
            
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "error": str(e)
            }
    
    async def _codebase_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze the codebase"""
        target = task.context.get("target", "")
        analysis_type = task.context.get("type", "overview")
        
        if not target:
            # Analyze entire codebase
            return await self._analyze_full_codebase(task)
        
        if analysis_type == "file":
            return await self._analyze_file(task)
        elif analysis_type == "function":
            return await self._find_function(task)
        elif analysis_type == "imports":
            return await self._analyze_imports(task)
        else:
            return await self._search_codebase(task)
    
    async def _analyze_full_codebase(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze the entire codebase"""
        self.log("Analyzing full codebase...")
        
        # Get project root
        project_root = os.getcwd()
        
        # Count files by type
        file_counts = {}
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                total_files += 1
                ext = os.path.splitext(file)[1]
                file_counts[ext] = file_counts.get(ext, 0) + 1
                
                # Count lines in Python files
                if ext == '.py':
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
        
        # Find main entry points
        entry_points = self._find_entry_points(project_root)
        
        return {
            "analysis_type": "full_codebase",
            "project_root": project_root,
            "file_counts": file_counts,
            "total_files": total_files,
            "total_lines": total_lines,
            "entry_points": entry_points,
            "languages": self._detect_languages(file_counts)
        }
    
    def _find_entry_points(self, project_root: str) -> List[Dict]:
        """Find potential entry points"""
        entry_points = []
        
        candidates = ["main.py", "app.py", "run.py", "server.py", "index.js", "server.js"]
        
        for candidate in candidates:
            path = os.path.join(project_root, candidate)
            if os.path.exists(path):
                entry_points.append({
                    "file": candidate,
                    "path": path
                })
        
        return entry_points
    
    def _detect_languages(self, file_counts: Dict) -> Dict[str, int]:
        """Detect programming languages used"""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".html": "HTML",
            ".css": "CSS",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown"
        }
        
        return {
            language_map.get(ext, ext): count
            for ext, count in file_counts.items()
            if ext in language_map
        }
    
    async def _analyze_file(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze a specific file"""
        file_path = task.context.get("file_path", "")
        
        if not file_path or not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Analyze content
            lines = content.split('\n')
            
            analysis = {
                "file": file_path,
                "lines": len(lines),
                "size": len(content),
                "extension": os.path.splitext(file_path)[1],
                "functions": self._extract_functions(content),
                "classes": self._extract_classes(content),
                "imports": self._extract_imports(content)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_functions(self, content: str) -> List[Dict]:
        """Extract function definitions"""
        functions = []
        
        # Python function pattern
        pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
        for match in re.finditer(pattern, content):
            functions.append({
                "name": match.group(1),
                "params": match.group(2).strip(),
                "line": content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict]:
        """Extract class definitions"""
        classes = []
        
        pattern = r'class\s+(\w+)(?:\(([^)]+)\))?:'
        for match in re.finditer(pattern, content):
            classes.append({
                "name": match.group(1),
                "inheritance": match.group(2) or "",
                "line": content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        patterns = [
            r'^import\s+(\S+)',
            r'^from\s+(\S+)\s+import'
        ]
        
        for line in content.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    async def _find_function(self, task: AgentTask) -> Dict[str, Any]:
        """Find a specific function in codebase"""
        function_name = task.context.get("function", "")
        
        if not function_name:
            return {"error": "No function name provided"}
        
        results = []
        project_root = os.getcwd()
        
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            content = f.read()
                            
                        if function_name in content:
                            # Find line number
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if f"def {function_name}" in line or f"class {function_name}" in line:
                                    results.append({
                                        "file": path,
                                        "line": i,
                                        "context": line.strip()
                                    })
                    except:
                        pass
        
        return {
            "function": function_name,
            "found_in": len(results),
            "locations": results
        }
    
    async def _analyze_imports(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze imports in a file or project"""
        file_path = task.context.get("file_path", "")
        
        if not file_path:
            return await self._analyze_project_imports(task)
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            imports = self._extract_imports(content)
            
            return {
                "file": file_path,
                "imports": imports,
                "count": len(imports)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_project_imports(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze all imports in project"""
        all_imports = {}
        
        project_root = os.getcwd()
        
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            imports = self._extract_imports(f.read())
                            
                        for imp in imports:
                            if imp not in all_imports:
                                all_imports[imp] = []
                            all_imports[imp].append(path)
                    except:
                        pass
        
        return {
            "total_unique_imports": len(all_imports),
            "imports": all_imports
        }
    
    async def _search_codebase(self, task: AgentTask) -> Dict[str, Any]:
        """Search for text in codebase"""
        query = task.context.get("query", "")
        
        if not query:
            return {"error": "No search query provided"}
        
        results = []
        project_root = os.getcwd()
        
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.txt', '.md')):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            content = f.read()
                            
                        if query.lower() in content.lower():
                            # Find line numbers
                            lines = content.split('\n')
                            matches = [i+1 for i, line in enumerate(lines) if query.lower() in line.lower()]
                            
                            results.append({
                                "file": path,
                                "matches": len(matches),
                                "lines": matches[:5]
                            })
                    except:
                        pass
        
        return {
            "query": query,
            "files_found": len(results),
            "results": results[:20]
        }
    
    async def _documentation_lookup(self, task: AgentTask) -> Dict[str, Any]:
        """Look up documentation"""
        topic = task.context.get("topic", task.description)
        
        # Search in README files
        doc_files = ["README.md", "README.txt", "CONTRIBUTING.md", "DOCS.md"]
        
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                try:
                    with open(doc_file, 'r') as f:
                        content = f.read()
                    
                    # Simple keyword search
                    if topic.lower() in content.lower():
                        return {
                            "topic": topic,
                            "found_in": doc_file,
                            "preview": content[:500]
                        }
                except:
                    pass
        
        return {
            "topic": topic,
            "found": False,
            "message": "Documentation not found in common files"
        }
    
    async def _fact_check(self, task: AgentTask) -> Dict[str, Any]:
        """Verify a fact"""
        statement = task.context.get("statement", task.description)
        
        # Search for related information
        search_results = await self._simple_search(statement)
        
        # Simple verification
        verified = False
        confidence = 0.0
        
        if search_results.get("results"):
            verified = True
            confidence = 0.6
        
        return {
            "statement": statement,
            "verified": verified,
            "confidence": confidence,
            "sources": search_results.get("results", [])[:3]
        }
    
    async def _summarization(self, task: AgentTask) -> Dict[str, Any]:
        """Summarize content"""
        text = task.context.get("text", "")
        source = task.context.get("source", "")
        
        if source and not text:
            # Load from file
            if os.path.exists(source):
                try:
                    with open(source, 'r') as f:
                        text = f.read()
                except:
                    return {"error": f"Could not read file: {source}"}
        
        if not text:
            return {"error": "No text provided to summarize"}
        
        # Simple extractive summarization
        sentences = text.split('.')
        if len(sentences) > 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = text[:500]
        
        return {
            "original_length": len(text),
            "summary": summary,
            "compression_ratio": len(summary) / max(len(text), 1)
        }
    
    async def _comparison(self, task: AgentTask) -> Dict[str, Any]:
        """Compare two items"""
        item1 = task.context.get("item1", "")
        item2 = task.context.get("item2", "")
        
        if not item1 or not item2:
            return {"error": "Two items required for comparison"}
        
        # Search for information about both
        results1 = await self._simple_search(item1)
        results2 = await self._simple_search(item2)
        
        return {
            "item1": item1,
            "item2": item2,
            "info1": results1.get("results", [])[:3],
            "info2": results2.get("results", [])[:3]
        }
    
    async def _explain_topic(self, task: AgentTask) -> Dict[str, Any]:
        """Explain a topic"""
        topic = task.context.get("topic", task.description)
        
        # Search for explanation
        results = await self._simple_search(f"What is {topic}")
        
        explanation = ""
        if results.get("results"):
            explanation = results["results"][0].get("content", "")
        
        return {
            "topic": topic,
            "explanation": explanation or "No explanation found",
            "sources": results.get("results", [])[:3]
        }
    
    async def _general_research(self, task: AgentTask) -> Dict[str, Any]:
        """General research task"""
        query = task.description
        
        results = await self._simple_search(query)
        
        return {
            "query": query,
            "results": results.get("results", []),
            "count": results.get("count", 0)
        }


# Global instance
_research_agent: Optional[ResearchAgent] = None


def get_research_agent(llm_client=None) -> ResearchAgent:
    """Get the research agent instance"""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent(llm_client)
    return _research_agent


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing Research Agent ===\n")
    
    async def test():
        agent = ResearchAgent()
        
        # Test codebase analysis
        task = AgentTask(
            description="Analyze codebase",
            task_type="codebase_analysis",
            context={"type": "overview"}
        )
        
        result = await agent.run(task)
        print("Codebase Analysis Result:")
        print(f"  Total files: {result.get('result', {}).get('total_files', 0)}")
        print(f"  Languages: {result.get('result', {}).get('languages', {})}")
    
    asyncio.run(test())

