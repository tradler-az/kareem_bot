#!/usr/bin/env python3
"""
Bosco Core - Advanced Features Test Script
Tests all the new advanced capabilities
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_vector_memory():
    """Test vector memory system"""
    print("\n" + "="*50)
    print("Testing Vector Memory (RAG)")
    print("="*50)
    
    try:
        from bosco_os.brain.vector_memory import VectorMemory
        
        vm = VectorMemory()
        print(f"✓ VectorMemory initialized")
        print(f"  Stats: {vm.get_stats()}")
        
        # Add test documents
        vm.add("Bosco was created by Tradler", metadata={"type": "fact"})
        vm.add("Python is a programming language", metadata={"type": "fact"})
        vm.add("Security is important for systems", metadata={"type": "fact"})
        
        # Search
        results = vm.search("who created Bosco", n_results=3)
        print(f"✓ Search completed: {len(results)} results")
        
        return True
    except Exception as e:
        print(f"✗ Vector Memory test failed: {e}")
        return False


async def test_multi_agent():
    """Test multi-agent system"""
    print("\n" + "="*50)
    print("Testing Multi-Agent Orchestration")
    print("="*50)
    
    try:
        from bosco_os.agents import get_orchestrator, create_task, TaskPriority
        
        orchestrator = get_orchestrator()
        print(f"✓ Orchestrator initialized")
        print(f"  Agents: {len(orchestrator.get_status()['agents'])}")
        
        # Test DevOps agent
        task = create_task(
            "List Docker images",
            "docker_images",
            TaskPriority.NORMAL,
            {}
        )
        
        result = await orchestrator.execute_task(task)
        print(f"✓ DevOps task executed: {result.get('success')}")
        
        # Test Research agent
        task = create_task(
            "Search for Python",
            "web_search",
            TaskPriority.NORMAL,
            {"query": "Python programming"}
        )
        
        result = await orchestrator.execute_task(task)
        print(f"✓ Research task executed: {result.get('success')}")
        
        return True
    except Exception as e:
        print(f"✗ Multi-agent test failed: {e}")
        return False


async def test_security_expert():
    """Test security expert agent"""
    print("\n" + "="*50)
    print("Testing Security Expert Agent")
    print("="*50)
    
    try:
        from bosco_os.agents.security_expert import get_security_expert, AgentTask
        
        agent = get_security_expert()
        print(f"✓ Security Expert initialized")
        
        # Test CVE lookup
        task = AgentTask(
            description="Look up Apache CVE",
            task_type="cve",
            context={"component": "apache", "version": "2.4"}
        )
        
        result = await agent.run(task)
        print(f"✓ CVE lookup executed: {result.get('success')}")
        
        return True
    except Exception as e:
        print(f"✗ Security Expert test failed: {e}")
        return False


async def test_threat_detector():
    """Test threat detector"""
    print("\n" + "="*50)
    print("Testing Threat Detector")
    print("="*50)
    
    try:
        from bosco_os.capabilities.security.threat_detector import ThreatDetector
        
        detector = ThreatDetector()
        print(f"✓ Threat Detector initialized")
        print(f"  Patterns loaded: {len(detector.patterns)}")
        
        # Test detection
        test_text = "Failed login attempt from IP 192.168.1.100"
        events = detector.detect_in_text(test_text, source="test")
        print(f"✓ Detection test: {len(events)} threats detected")
        
        # Get stats
        stats = detector.get_threat_summary()
        print(f"  Stats: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Threat Detector test failed: {e}")
        return False


async def test_screen_capture():
    """Test screen capture"""
    print("\n" + "="*50)
    print("Testing Screen Capture")
    print("="*50)
    
    try:
        from bosco_os.perception.screen_capture import ScreenCapture
        
        capture = ScreenCapture()
        print(f"✓ Screen Capture initialized")
        print(f"  Backend: {capture.backend}")
        
        size = capture.get_screen_size()
        print(f"  Screen size: {size}")
        
        return True
    except Exception as e:
        print(f"✗ Screen Capture test failed: {e}")
        return False


async def test_mcp_server():
    """Test MCP server"""
    print("\n" + "="*50)
    print("Testing MCP Server")
    print("="*50)
    
    try:
        from bosco_os.mcp.server import MCPServer, MCPTool
        
        server = MCPServer("test-server")
        print(f"✓ MCP Server initialized")
        
        # Register a tool
        async def hello_handler(params):
            return {"message": f"Hello, {params.get('name', 'World')}!"}
        
        server.register_tool(MCPTool(
            name="hello",
            description="Say hello",
            input_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            handler=hello_handler
        ))
        
        print(f"  Tools registered: {len(server.list_tools())}")
        
        return True
    except Exception as e:
        print(f"✗ MCP Server test failed: {e}")
        return False


async def test_validator():
    """Test ReAct validator"""
    print("\n" + "="*50)
    print("Testing ReAct Validator")
    print("="*50)
    
    try:
        from bosco_os.core.validator import ReActEngine, ExecutionValidator
        
        # Test validator
        validator = ExecutionValidator()
        print(f"✓ Execution Validator initialized")
        
        result = validator.validate("echo 'test'")
        print(f"  Safe command: {result['action']}")
        
        result = validator.validate("sudo rm -rf /")
        print(f"  Dangerous command: {result['action']}")
        
        # Test ReAct engine
        engine = ReActEngine()
        print(f"✓ ReAct Engine initialized")
        
        result = await engine.execute_with_retry("echo 'Hello'")
        print(f"  Command execution: {result['success']}")
        
        return True
    except Exception as e:
        print(f"✗ Validator test failed: {e}")
        return False


async def test_execution_sandbox():
    """Test execution sandbox"""
    print("\n" + "="*50)
    print("Testing Execution Sandbox")
    print("="*50)
    
    try:
        from bosco_os.core.execution_sandbox import ExecutionSandbox
        
        sandbox = ExecutionSandbox(timeout=5)
        print(f"✓ Execution Sandbox initialized")
        
        # Test safe code
        code = "print('Hello from sandbox')"
        result = await sandbox.execute_python(code)
        print(f"  Safe code: {result.success}")
        
        # Test dangerous code detection
        dangerous = "import os; os.system('rm -rf /')"
        analysis = sandbox.analyze_code(dangerous)
        print(f"  Dangerous code detected: {not analysis['safe']}")
        
        return True
    except Exception as e:
        print(f"✗ Sandbox test failed: {e}")
        return False


async def test_vision_engine():
    """Test vision engine"""
    print("\n" + "="*50)
    print("Testing Vision Engine")
    print("="*50)
    
    try:
        from bosco_os.perception.vision_engine import VisionEngine
        
        engine = VisionEngine()
        print(f"✓ Vision Engine initialized")
        print(f"  Provider: {engine.vision_provider}")
        
        # Test element detection (requires screen)
        elements = await engine.detect_elements()
        print(f"  Elements detected: {len(elements)}")
        
        return True
    except Exception as e:
        print(f"✗ Vision Engine test failed: {e}")
        return False


async def test_mcp_server_manager():
    """Test MCP server manager"""
    print("\n" + "="*50)
    print("Testing MCP Server Manager")
    print("="*50)
    
    try:
        from bosco_os.mcp.server_manager import get_mcp_server_manager
        
        manager = get_mcp_server_manager()
        print(f"✓ MCP Server Manager initialized")
        
        # List presets
        presets = manager.get_presets()
        print(f"  Available presets: {len(presets)}")
        
        for preset in presets[:3]:
            print(f"    - {preset['id']}: {preset['name']}")
        
        return True
    except Exception as e:
        print(f"✗ MCP Server Manager test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "#"*50)
    print("# BOSCO CORE - ADVANCED FEATURES TEST SUITE")
    print("#"*50)
    
    tests = [
        ("Vector Memory (RAG)", test_vector_memory),
        ("Multi-Agent System", test_multi_agent),
        ("Security Expert Agent", test_security_expert),
        ("Threat Detector", test_threat_detector),
        ("Screen Capture", test_screen_capture),
        ("MCP Server", test_mcp_server),
        ("ReAct Validator", test_validator),
        ("Execution Sandbox", test_execution_sandbox),
        ("Vision Engine", test_vision_engine),
        ("MCP Server Manager", test_mcp_server_manager),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bosco Core advanced features are working.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

