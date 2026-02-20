"""
Bosco Core - Project Idea Builder
Helps users build projects from idea to completion with documentation and resources
"""

import os
import json
import subprocess
import urllib.request
import urllib.parse
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class ProjectBuilder:
    """
    Helps build projects from idea to completion
    Provides step-by-step guidance, resources, and documentation
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        # Project type templates
        self.project_templates = {
            'web_app': {
                'name': 'Web Application',
                'description': 'Full-stack web application',
                'tech_stack': ['Frontend: React/Vue/Angular', 'Backend: Node.js/Python/Go', 'Database: PostgreSQL/MongoDB', 'DevOps: Docker, CI/CD'],
                'steps': [
                    'Define requirements and features',
                    'Design database schema',
                    'Set up project structure',
                    'Implement backend API',
                    'Build frontend UI',
                    'Add authentication',
                    'Write tests',
                    'Deploy to production'
                ],
                'tools': ['VS Code', 'Git', 'Docker', 'Postman']
            },
            'mobile_app': {
                'name': 'Mobile Application',
                'description': 'iOS or Android app',
                'tech_stack': ['React Native/Flutter', 'Firebase/Supabase', 'REST/GraphQL API'],
                'steps': [
                    'Define app features and UI/UX',
                    'Set up development environment',
                    'Create app architecture',
                    'Implement core features',
                    'Add navigation and routing',
                    'Integrate backend services',
                    'Test on devices',
                    'Build and publish'
                ],
                'tools': ['VS Code', 'Android Studio/Xcode', 'Flutter/React Native CLI']
            },
            'api': {
                'name': 'REST/GraphQL API',
                'description': 'Backend API service',
                'tech_stack': ['Node.js/Express', 'Python/FastAPI', 'PostgreSQL/MongoDB', 'Redis'],
                'steps': [
                    'Design API endpoints',
                    'Set up project with dependencies',
                    'Create database models',
                    'Implement controllers',
                    'Add authentication (JWT)',
                    'Write API documentation',
                    'Add validation and error handling',
                    'Write unit tests',
                    'Set up CI/CD'
                ],
                'tools': ['VS Code', 'Postman', 'Docker', 'pgAdmin']
            },
            'cli_tool': {
                'name': 'CLI Tool',
                'description': 'Command-line interface tool',
                'tech_stack': ['Python/Go/Rust', 'Click/Argparse', 'Colorama'],
                'steps': [
                    'Define CLI commands',
                    'Set up project structure',
                    'Implement argument parsing',
                    'Add subcommands',
                    'Add colors and formatting',
                    'Write documentation',
                    'Add testing',
                    'Create distribution package'
                ],
                'tools': ['VS Code', 'Python/Go compiler']
            },
            'game': {
                'name': 'Game',
                'description': '2D or 3D game',
                'tech_stack': ['Unity/Unreal/Godot', 'Python/Pygame', 'JavaScript/Phaser'],
                'steps': [
                    'Design game concept',
                    'Create game assets',
                    'Set up game engine',
                    'Implement game logic',
                    'Add physics and collisions',
                    'Create levels',
                    'Add sound and effects',
                    'Test and optimize',
                    'Build for distribution'
                ],
                'tools': ['Unity/Godot', 'Blender', 'Aseprite']
            },
            'machine_learning': {
                'name': 'Machine Learning Project',
                'description': 'ML model or AI application',
                'tech_stack': ['Python', 'TensorFlow/PyTorch', 'Scikit-learn', 'Jupyter'],
                'steps': [
                    'Define problem and metrics',
                    'Collect and preprocess data',
                    'Explore and visualize data',
                    'Build baseline model',
                    'Improve and optimize',
                    'Evaluate performance',
                    'Deploy model',
                    'Monitor and maintain'
                ],
                'tools': ['Jupyter Notebook', 'Python', 'TensorFlow', 'Weights & Biases']
            },
            'automation': {
                'name': 'Automation Script',
                'description': 'Task automation or bot',
                'tech_stack': ['Python', 'Selenium/Playwright', 'APIs'],
                'steps': [
                    'Identify automation tasks',
                    'Choose automation tools',
                    'Set up environment',
                    'Write automation scripts',
                    'Handle errors gracefully',
                    'Add scheduling',
                    'Test thoroughly',
                    'Deploy and monitor'
                ],
                'tools': ['Python', 'Selenium', 'Cron', 'APIs']
            },
            'iot': {
                'name': 'IoT Project',
                'description': 'Internet of Things device',
                'tech_stack': ['Arduino/ESP32', 'Python', 'MQTT', 'Cloud (AWS IoT)'],
                'steps': [
                    'Define IoT use case',
                    'Select hardware',
                    'Set up development environment',
                    'Write firmware',
                    'Connect to network',
                    'Set up cloud backend',
                    'Create dashboard',
                    'Deploy and test'
                ],
                'tools': ['Arduino IDE', 'Python', 'Cloud IoT platform']
            },
            'desktop_app': {
                'name': 'Desktop Application',
                'description': 'Native desktop software',
                'tech_stack': ['Electron/Qt', 'Python/Tkinter', 'C#/.NET', 'Go'],
                'steps': [
                    'Design application UI',
                    'Set up development environment',
                    'Implement core features',
                    'Add system integration',
                    'Write tests',
                    'Build executable',
                    'Create installer',
                    'Distribute application'
                ],
                'tools': ['VS Code', 'Electron/Qt', 'Build tools']
            }
        }

    def _run_cmd(self, cmd: str, timeout: int = 30) -> str:
        """Run shell command"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout + result.stderr
        except:
            return ""

    def _search_web(self, query: str) -> List[Dict[str, str]]:
        """Search the web for resources"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read().decode('utf-8', errors='ignore')
            
            results = []
            # Simple parsing
            import re
            pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.DOTALL)
            
            for match in matches[:5]:
                results.append({
                    'url': match[0],
                    'title': match[1].strip(),
                    'snippet': match[2].strip()[:150]
                })
            
            return results
        except:
            return []

    def analyze_idea(self, idea: str) -> Dict[str, Any]:
        """
        Analyze a project idea and suggest project type
        
        Args:
            idea: User's project idea description
            
        Returns:
            Analysis with suggested project type and details
        """
        idea_lower = idea.lower()
        
        # Keyword matching for project type
        type_scores = {}
        
        # Web app keywords
        web_keywords = ['web', 'website', 'app', 'online', 'dashboard', 'portal']
        if any(k in idea_lower for k in web_keywords):
            type_scores['web_app'] = type_scores.get('web_app', 0) + 2
        
        # Mobile keywords
        mobile_keywords = ['mobile', 'android', 'ios', 'phone', 'app']
        if any(k in idea_lower for k in mobile_keywords):
            type_scores['mobile_app'] = type_scores.get('mobile_app', 0) + 3
        
        # API keywords
        api_keywords = ['api', 'backend', 'service', 'server']
        if any(k in idea_lower for k in api_keywords):
            type_scores['api'] = type_scores.get('api', 0) + 3
        
        # CLI keywords
        cli_keywords = ['cli', 'command', 'tool', 'script', 'terminal']
        if any(k in idea_lower for k in cli_keywords):
            type_scores['cli_tool'] = type_scores.get('cli_tool', 0) + 3
        
        # Game keywords
        game_keywords = ['game', 'gaming', 'play', 'player']
        if any(k in idea_lower for k in game_keywords):
            type_scores['game'] = type_scores.get('game', 0) + 3
        
        # ML keywords
        ml_keywords = ['machine learning', 'ml', 'ai', 'neural', 'model', 'deep learning', 'prediction']
        if any(k in idea_lower for k in ml_keywords):
            type_scores['machine_learning'] = type_scores.get('machine_learning', 0) + 3
        
        # Automation keywords
        auto_keywords = ['automation', 'bot', 'auto', 'schedule', 'cron']
        if any(k in idea_lower for k in auto_keywords):
            type_scores['automation'] = type_scores.get('automation', 0) + 3
        
        # IoT keywords
        iot_keywords = ['iot', 'sensor', 'arduino', 'raspberry', 'hardware', 'device']
        if any(k in idea_lower for k in iot_keywords):
            type_scores['iot'] = type_scores.get('iot', 0) + 3
        
        # Desktop keywords
        desktop_keywords = ['desktop', 'window', 'software', 'program']
        if any(k in idea_lower for k in desktop_keywords):
            type_scores['desktop_app'] = type_scores.get('desktop_app', 0) + 2
        
        # Find best match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
        else:
            best_type = 'web_app'  # Default
        
        template = self.project_templates.get(best_type, self.project_templates['web_app'])
        
        return {
            'idea': idea,
            'suggested_type': best_type,
            'project_name': template['name'],
            'description': template['description'],
            'tech_stack': template['tech_stack'],
            'steps': template['steps'],
            'tools': template['tools'],
            'confidence': type_scores.get(best_type, 0) / 3
        }

    def get_project_plan(self, project_type: str) -> Dict[str, Any]:
        """Get detailed project plan for a type"""
        template = self.project_templates.get(project_type, self.project_templates['web_app'])
        return template

    def search_online_resources(self, topic: str) -> List[Dict[str, str]]:
        """Search for online resources on a topic"""
        queries = [
            f"{topic} tutorial getting started",
            f"{topic} documentation official",
            f"{topic} best practices 2024"
        ]
        
        all_results = []
        for query in queries:
            results = self._search_web(query)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in all_results:
            if r['url'] not in seen:
                seen.add(r['url'])
                unique_results.append(r)
        
        return unique_results[:10]

    def generate_project_structure(self, project_type: str, project_name: str) -> str:
        """Generate project folder structure"""
        
        structures = {
            'web_app': f"""{project_name}/
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── middleware/
│   │   ├── config/
│   │   └── app.js
│   ├── package.json
│   └── .env
├── database/
│   └── schema.sql
├── docker-compose.yml
├── README.md
└── .gitignore""",

            'mobile_app': f"""{project_name}/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   ├── services/
│   ├── hooks/
│   ├── utils/
│   ├── assets/
│   └── App.tsx
├── android/
├── ios/
├── index.js
├── package.json
├── tsconfig.json
└── app.json""",

            'api': f"""{project_name}/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── middleware/
│   ├── services/
│   ├── utils/
│   ├── config/
│   └── index.js
├── tests/
│   └── api.test.js
├── .env
├── package.json
├── docker-compose.yml
└── README.md""",

            'cli_tool': f"""{project_name}/
├── {project_name}/
│   ├── __init__.py
│   ├── cli.py
│   └── utils/
├── tests/
├── docs/
├── setup.py
├── requirements.txt
├── README.md
└── .gitignore""",

            'machine_learning': f"""{project_name}/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── exploration.ipynb
│   └── modeling.ipynb
├── src/
│   ├── data/
│   ├── models/
│   └── visualization/
├── models/
├── outputs/
├── requirements.txt
├── README.md
└── .gitignore""",

            'automation': f"""{project_name}/
├── scripts/
├── config/
├── logs/
├── requirements.txt
├── run.py
├── README.md
└── .gitignore"""
        }
        
        return structures.get(project_type, "Project structure not available for this type")

    def create_project(self, project_name: str, project_type: str, location: str = ".") -> str:
        """Create a new project with structure"""
        
        # Create project directory
        project_path = os.path.join(location, project_name)
        
        try:
            os.makedirs(project_path, exist_ok=True)
            
            # Generate and save structure
            structure = self.generate_project_structure(project_type, project_name)
            
            # Save structure to file
            structure_file = os.path.join(project_path, "PROJECT_STRUCTURE.txt")
            with open(structure_file, 'w') as f:
                f.write(structure)
            
            # Create basic files based on type
            if project_type == 'web_app':
                # Create frontend package.json
                frontend_pkg = {
                    "name": f"{project_name}-frontend",
                    "version": "1.0.0",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    }
                }
                with open(os.path.join(project_path, "frontend", "package.json"), 'w') as f:
                    json.dump(frontend_pkg, f, indent=2)
                
                # Create backend package.json
                backend_pkg = {
                    "name": f"{project_name}-backend",
                    "version": "1.0.0",
                    "main": "src/index.js",
                    "scripts": {
                        "start": "node src/index.js",
                        "dev": "nodemon src/index.js"
                    },
                    "dependencies": {
                        "express": "^4.18.0",
                        "cors": "^2.8.5"
                    }
                }
                with open(os.path.join(project_path, "backend", "package.json"), 'w') as f:
                    json.dump(backend_pkg, f, indent=2)
            
            elif project_type == 'api':
                pkg = {
                    "name": project_name,
                    "version": "1.0.0",
                    "main": "src/index.js",
                    "scripts": {
                        "start": "node src/index.js",
                        "dev": "nodemon src/index.js",
                        "test": "jest"
                    },
                    "dependencies": {
                        "express": "^4.18.0",
                        "cors": "^2.8.5",
                        "dotenv": "^16.0.0"
                    },
                    "devDependencies": {
                        "nodemon": "^2.0.0",
                        "jest": "^29.0.0"
                    }
                }
                with open(os.path.join(project_path, "package.json"), 'w') as f:
                    json.dump(pkg, f, indent=2)
            
            elif project_type == 'cli_tool':
                # Create setup.py
                setup_content = f"""from setuptools import setup, find_packages

setup(
    name='{project_name}',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={{
        'console_scripts': [
            '{project_name}={project_name}.cli:main',
        ],
    }},
)
"""
                with open(os.path.join(project_path, "setup.py"), 'w') as f:
                    f.write(setup_content)
            
            # Create README template
            readme = f"""# {project_name}

## Description
Your project description here

## Tech Stack
{', '.join(self.project_templates.get(project_type, {}).get('tech_stack', []))}

## Getting Started

### Prerequisites
- Required tools and software

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name}.git
cd {project_name}

# Install dependencies
# (add your package manager command here)
```

### Usage
```bash
# Add usage instructions
```

## Project Structure
See PROJECT_STRUCTURE.txt for full directory structure

## Documentation
Add your documentation here

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT
"""
            with open(os.path.join(project_path, "README.md"), 'w') as f:
                f.write(readme)
            
            # Create .gitignore
            gitignore = """# Dependencies
node_modules/
__pycache__/
*.pyc
.env

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
coverage/
.pytest_cache/
"""
            with open(os.path.join(project_path, ".gitignore"), 'w') as f:
                f.write(gitignore)
            
            return f"✅ Project '{project_name}' created at {project_path}\n\nProject structure:\n{structure}"
            
        except Exception as e:
            return f"❌ Error creating project: {str(e)}"

    def get_documentation_links(self, project_type: str) -> Dict[str, str]:
        """Get official documentation links for project type"""
        
        docs = {
            'web_app': {
                'React': 'https://react.dev/',
                'Node.js': 'https://nodejs.org/docs/',
                'Express': 'https://expressjs.com/',
                'PostgreSQL': 'https://www.postgresql.org/docs/',
                'Docker': 'https://docs.docker.com/'
            },
            'mobile_app': {
                'React Native': 'https://reactnative.dev/docs/',
                'Flutter': 'https://docs.flutter.dev/',
                'Firebase': 'https://firebase.google.com/docs'
            },
            'api': {
                'Express': 'https://expressjs.com/',
                'FastAPI': 'https://fastapi.tiangolo.com/',
                'PostgreSQL': 'https://www.postgresql.org/docs/',
                'REST API': 'https://restfulapi.net/'
            },
            'cli_tool': {
                'Click': 'https://click.palletsprojects.com/',
                'Argparse': 'https://docs.python.org/3/library/argparse.html'
            },
            'machine_learning': {
                'TensorFlow': 'https://www.tensorflow.org/guide',
                'PyTorch': 'https://pytorch.org/docs/',
                'Scikit-learn': 'https://scikit-learn.org/stable/',
                'Jupyter': 'https://jupyter.org/documentation'
            },
            'game': {
                'Unity': 'https://docs.unity3d.com/',
                'Godot': 'https://docs.godotengine.org/',
                'Pygame': 'https://www.pygame.org/docs/'
            },
            'automation': {
                'Selenium': 'https://www.selenium.dev/documentation/',
                'Python': 'https://docs.python.org/3/'
            },
            'iot': {
                'Arduino': 'https://www.arduino.cc/reference/en/',
                'ESP32': 'https://docs.espressif.com/',
                'MQTT': 'https://mqtt.org/documentation/'
            },
            'desktop_app': {
                'Electron': 'https://www.electronjs.org/docs',
                'Qt': 'https://doc.qt.io/',
                'PyQt': 'https://www.riverbankcomputing.com/static/Docs/PyQt6/'
            }
        }
        
        return docs.get(project_type, {})

    def get_learning_path(self, project_type: str) -> List[Dict[str, str]]:
        """Get recommended learning path"""
        
        paths = {
            'web_app': [
                {'step': 1, 'topic': 'HTML/CSS Fundamentals', 'duration': '1 week'},
                {'step': 2, 'topic': 'JavaScript Basics', 'duration': '2 weeks'},
                {'step': 3, 'topic': 'React or Vue.js', 'duration': '2 weeks'},
                {'step': 4, 'topic': 'Node.js & Express', 'duration': '2 weeks'},
                {'step': 5, 'topic': 'Database Design (SQL)', 'duration': '1 week'},
                {'step': 6, 'topic': 'Authentication & Security', 'duration': '1 week'},
                {'step': 7, 'topic': 'Docker & Deployment', 'duration': '1 week'}
            ],
            'machine_learning': [
                {'step': 1, 'topic': 'Python Programming', 'duration': '2 weeks'},
                {'step': 2, 'topic': 'Math (Linear Algebra, Calculus)', 'duration': '2 weeks'},
                {'step': 3, 'topic': 'Data Analysis (Pandas, NumPy)', 'duration': '2 weeks'},
                {'step': 4, 'topic': 'Machine Learning Basics', 'duration': '3 weeks'},
                {'step': 5, 'topic': 'Deep Learning & Neural Networks', 'duration': '3 weeks'},
                {'step': 6, 'topic': 'Model Deployment', 'duration': '1 week'}
            ],
            'api': [
                {'step': 1, 'topic': 'REST API Design', 'duration': '1 week'},
                {'step': 2, 'topic': 'Node.js or Python Backend', 'duration': '2 weeks'},
                {'step': 3, 'topic': 'Database (SQL or NoSQL)', 'duration': '2 weeks'},
                {'step': 4, 'topic': 'Authentication (JWT)', 'duration': '1 week'},
                {'step': 5, 'topic': 'API Documentation', 'duration': '1 week'},
                {'step': 6, 'topic': 'Testing & CI/CD', 'duration': '1 week'}
            ]
        }
        
        return paths.get(project_type, [{'step': 1, 'topic': 'Basics', 'duration': 'varies'}])

    def build_project(self, user_idea: str) -> str:
        """
        Main method - Build complete project guidance from idea
        
        Args:
            user_idea: The user's project idea
            
        Returns:
            Complete project guide with steps, resources, and structure
        """
        # Step 1: Analyze the idea
        analysis = self.analyze_idea(user_idea)
        
        project_type = analysis['suggested_type']
        template = self.project_templates[project_type]
        
        # Step 2: Get online resources
        resources = self.search_online_resources(template['name'])
        
        # Step 3: Get documentation links
        docs = self.get_documentation_links(project_type)
        
        # Step 4: Get learning path
        learning_path = self.get_learning_path(project_type)
        
        # Build the response
        result = f"""
╔══════════════════════════════════════════════════════════════════╗
║           PROJECT IDEA BUILDER - COMPLETE GUIDE                 ║
╚══════════════════════════════════════════════════════════════════╝

📝 YOUR IDEA: {user_idea}

🎯 SUGGESTED PROJECT TYPE: {analysis['project_name']}
   Description: {analysis['description']}
   Confidence: {int(analysis['confidence'] * 100)}%

═══════════════════════════════════════════════════════════════════
                    📚 TECH STACK
═══════════════════════════════════════════════════════════════════
"""
        
        for tech in template['tech_stack']:
            result += f"  • {tech}\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    🛠️  TOOLS NEEDED
═══════════════════════════════════════════════════════════════════
"""
        
        for tool in template['tools']:
            result += f"  • {tool}\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    📋 STEP-BY-STEP GUIDE
═══════════════════════════════════════════════════════════════════
"""
        
        for i, step in enumerate(template['steps'], 1):
            result += f"  {i}. {step}\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    📖 LEARNING PATH
═══════════════════════════════════════════════════════════════════
"""
        
        for item in learning_path:
            result += f"  Week {item['step']}: {item['topic']} ({item['duration']})\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    🔗 DOCUMENTATION LINKS
═══════════════════════════════════════════════════════════════════
"""
        
        for name, url in docs.items():
            result += f"  • {name}: {url}\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    🌐 ONLINE RESOURCES
═══════════════════════════════════════════════════════════════════
"""
        
        for i, res in enumerate(resources[:5], 1):
            result += f"  {i}. {res['title']}\n"
            result += f"     {res['url'][:70]}...\n\n"
        
        result += """
═══════════════════════════════════════════════════════════════════
                    📂 PROJECT STRUCTURE
═══════════════════════════════════════════════════════════════════
"""
        
        structure = self.generate_project_structure(project_type, "your_project")
        result += f"""
{structure}

═══════════════════════════════════════════════════════════════════
                    🚀 READY TO START?
═══════════════════════════════════════════════════════════════════

Say "create project [name]" to generate the project files!

Example commands:
  • "create project my-app as web_app"
  • "create project ml-project as machine_learning"
  • "create project my-api"

═══════════════════════════════════════════════════════════════════
"""
        
        return result


# Global instance
_project_builder = None

def get_project_builder() -> ProjectBuilder:
    """Get project builder instance"""
    global _project_builder
    if _project_builder is None:
        _project_builder = ProjectBuilder()
    return _project_builder


# Convenience functions
def analyze_idea(idea: str) -> Dict[str, Any]:
    """Analyze a project idea"""
    return get_project_builder().analyze_idea(idea)

def build_project(idea: str) -> str:
    """Build complete project guide"""
    return get_project_builder().build_project(idea)

def create_project(name: str, project_type: str = 'web_app') -> str:
    """Create project files"""
    return get_project_builder().create_project(name, project_type)


if __name__ == "__main__":
    print("=== Project Idea Builder Test ===\n")
    
    builder = ProjectBuilder()
    
    # Test with an idea
    print("Testing with idea: 'I want to build a machine learning app'")
    result = builder.build_project("I want to build a machine learning app")
    print(result[:2000])

