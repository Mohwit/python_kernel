#!/usr/bin/env python3
"""
Persistent Docker Kernel

A secure Python code execution environment using Docker containers with persistent
state stored in isolated volumes.
"""

import json
import inspect
from typing import Any, Dict, Optional
from .docker_runner import DockerRunner

class PersistentKernel:
    """
    Persistent Docker Kernel for secure Python code execution.
    
    Executes Python code in isolated Docker containers while maintaining
    persistent state across executions using Docker volumes.
    """

    def __init__(self, 
                 namespace: Optional[Dict[str, Any]] = None, 
                 imports: str = "", 
                 timeout: int = 30,
                 memory_limit: str = "512m",
                 cpu_limit: str = "0.5",
                 session_id: str = "default",
                 default_packages: Optional[list] = None) -> None:
        """
        Initialize the persistent kernel.
        
        Args:
            namespace: Initial variables and functions to load
            imports: Import statements to run on initialization  
            timeout: Execution timeout in seconds
            memory_limit: Docker memory limit (e.g., "512m")
            cpu_limit: Docker CPU limit (e.g., "0.5")
            session_id: Unique identifier for this kernel session
            default_packages: List of packages to install automatically
        """
        self.initial_namespace = namespace or {}
        self.imports = imports
        self.timeout = timeout
        self.session_id = session_id
        self.default_packages = default_packages or []
        
        # Initialize Docker runner
        self.docker_runner = DockerRunner(
            memory_limit=memory_limit,
            cpu_limit=cpu_limit,
            timeout=timeout,
            session_id=session_id
        )
        
        # Build Docker image if needed
        if not self.docker_runner._image_exists():
            print("Building Docker image for persistent kernel...")
            if not self.docker_runner.build_image():
                raise RuntimeError("Failed to build Docker image")
            print()
        
        # Initialize state and install default packages
        self._initialize_volume_state()
        self._install_default_packages()
        
        # Run imports if specified
        if self.imports:
            result = self._execute_with_state(self.imports)
            if not result["success"]:
                raise RuntimeError(f"Failed to initialize imports: {result['error']}")

    def reset(self) -> None:
        """Reset the kernel namespace to initial state."""
        self._initialize_volume_state()
        self._install_default_packages()
        if self.imports:
            result = self._execute_with_state(self.imports)
            if not result["success"]:
                print(f"Warning: Failed to re-initialize imports after reset: {result['error']}")

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in the persistent kernel.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with 'success', 'output', and 'error' keys
        """
        if not isinstance(code, str):
            return {
                "success": False,
                "output": "",
                "error": "Code must be a string",
            }
        
        return self._execute_with_state(code)

    def _execute_with_state(self, code: str) -> Dict[str, Any]:
        """Execute code while maintaining persistent state."""
        full_code = self._build_stateful_code(code)
        result = self.docker_runner.execute(full_code)
        
        if not result.success:
            return {
                "success": False,
                "output": result.output,
                "error": result.error
            }
        
        # Filter out state management messages from output
        try:
            lines = result.output.strip().split('\n')
            output_lines = [line for line in lines 
                          if not line.startswith(("STATE_SAVED", "STATE_LOADED"))]
            
            return {
                "success": True,
                "output": '\n'.join(output_lines),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": result.output,
                "error": f"Error processing execution result: {str(e)}"
            }

    def _build_stateful_code(self, user_code: str) -> str:
        """Build the complete code that maintains state across executions using volume storage."""
        
        # Build imports section
        imports_section = ""
        if self.imports:
            imports_section = f"# Execute imports\n{self.imports}\n"
        
        stateful_code = f'''
import json
import sys
import inspect
import os
from io import StringIO
import textwrap

{imports_section}

# State file path in the mounted volume
STATE_FILE = '/app/state/kernel_state.json'

# Load previous state from volume
current_state = {{}}
try:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            current_state = json.load(f)
        print("STATE_LOADED")
except Exception as e:
    print(f"Warning: Could not load state: {{e}}")

# Restore functions first and preserve them for later
restored_functions = {{}}
if '__functions__' in current_state:
    restored_functions = current_state['__functions__'].copy()
    for func_name, func_source in current_state['__functions__'].items():
        try:
            # Execute the function definition
            exec(func_source, globals())
        except Exception as e:
            print(f"Warning: Could not restore function {{func_name}}: {{e}}")
    # Remove function definitions from state
    del current_state['__functions__']

# Restore variables to globals
for key, value in current_state.items():
    globals()[key] = value

# Set up function definition tracking
import ast
import types

# Define the user code for parsing
user_code = {repr(user_code)}

# Parse the user code to extract function definitions
try:
    user_ast = ast.parse(user_code)
    function_sources = {{}}
    
    for node in ast.walk(user_ast):
        if isinstance(node, ast.FunctionDef):
            # Extract the function source from the original code
            lines = user_code.split('\\n')
            if node.lineno <= len(lines):
                # Get the function definition lines
                func_lines = []
                start_line = node.lineno - 1
                
                # Find the end of the function by looking for the next non-indented line
                indent_level = None
                for i in range(start_line, len(lines)):
                    line = lines[i]
                    if line.strip():  # Non-empty line
                        if indent_level is None:
                            indent_level = len(line) - len(line.lstrip())
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent < indent_level and line.strip():
                            break
                    func_lines.append(line)
                
                if func_lines:
                    func_source = '\\n'.join(func_lines).rstrip()
                    function_sources[node.name] = func_source
except SyntaxError:
    function_sources = {{}}

# Capture stdout
old_stdout = sys.stdout
captured_output = StringIO()
sys.stdout = captured_output

try:
    # Execute user code
{self._indent_code(user_code)}
    
    # Capture new state (JSON-serializable objects and functions)
    new_state = current_state.copy()  # Start with existing state
    function_definitions = {{}}
    excluded_keys = ['json', 'sys', 'StringIO', 'old_stdout', 'captured_output', 'current_state', 'new_state', 'inspect', 'func_name', 'func_source', 'e', 'os', 'textwrap', 'STATE_FILE', 'function_definitions', 'excluded_keys', 'globals_snapshot', 'ast', 'types', 'user_ast', 'function_sources', 'node', 'lines', 'func_lines', 'start_line', 'indent_level', 'i', 'line', 'current_indent', 'func_source', 'restored_functions']
    
    # Start with restored functions from the beginning of execution
    function_definitions.update(restored_functions)
    
    # Create a snapshot of globals to avoid "dictionary changed size during iteration" error
    globals_snapshot = dict(globals())
    
    for key, value in globals_snapshot.items():
        if not key.startswith('_') and key not in excluded_keys:
            # Handle functions
            if callable(value) and hasattr(value, '__code__'):
                # If we already have this function's source from existing state, keep it
                if key not in function_definitions:
                    try:
                        func_source = inspect.getsource(value)
                        # Remove common leading whitespace
                        func_source = textwrap.dedent(func_source)
                        function_definitions[key] = func_source
                    except (OSError, TypeError):
                        # For dynamically created functions, check parsed sources first
                        if key in function_sources:
                            function_definitions[key] = function_sources[key]
                        elif hasattr(value, '_kernel_source'):
                            function_definitions[key] = value._kernel_source
                        # If we can't get source, skip this function
                # If function already exists in function_definitions, keep the existing source
            else:
                # Handle regular JSON-serializable objects
                try:
                    json.dumps(value)  # Test if serializable
                    new_state[key] = value
                except (TypeError, ValueError):
                    # Skip non-serializable objects
                    pass
    
    # Add function definitions to state if any exist
    if function_definitions:
        new_state['__functions__'] = function_definitions
    
    # Save state to volume
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f, indent=2)
        print("STATE_SAVED")
    except Exception as e:
        print(f"Warning: Could not save state: {{e}}")
    
    # Get the output
    output = captured_output.getvalue()
    
    # Print the output
    sys.stdout = old_stdout
    if output:
        print(output.rstrip())
    
except Exception as e:
    sys.stdout = old_stdout
    print(f"Error: {{str(e)}}")
    # Try to save current state even on error
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(current_state, f, indent=2)
    except:
        pass
'''
        
        return stateful_code

    def _initialize_volume_state(self) -> None:
        """Initialize the state in the Docker volume with initial namespace."""
        if not self.initial_namespace:
            return
        
        # Serialize initial namespace properly
        serializable_state = {}
        function_definitions = {}
        
        for key, value in self.initial_namespace.items():
            if not key.startswith('_'):
                # Handle functions
                if callable(value) and hasattr(value, '__code__'):
                    try:
                        # Get function source code and dedent it
                        import inspect
                        import textwrap
                        func_source = inspect.getsource(value)
                        func_source = textwrap.dedent(func_source)
                        function_definitions[key] = func_source
                    except (OSError, TypeError):
                        # If we can't get source, skip this function
                        pass
                else:
                    # Handle regular JSON-serializable objects
                    try:
                        json.dumps(value)  # Test if serializable
                        serializable_state[key] = value
                    except (TypeError, ValueError):
                        # Skip non-serializable objects
                        pass
        
        # Add function definitions to state if any exist
        if function_definitions:
            serializable_state['__functions__'] = function_definitions
        
        # Create initial state file in volume
        init_code = f'''
import json
import os

STATE_FILE = '/app/state/kernel_state.json'
initial_state_json = {repr(json.dumps(serializable_state))}

try:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        f.write(initial_state_json)
    print("Initial state saved to volume")
except Exception as e:
    print(f"Warning: Could not save initial state: {{e}}")
'''
        
        result = self.docker_runner.execute(init_code)
        if not result.success:
            print(f"Warning: Failed to initialize volume state: {result.error}")

    def _install_default_packages(self) -> None:
        """Install default packages specified during initialization."""
        if not self.default_packages:
            return
            
        print(f"Installing {len(self.default_packages)} default packages...")
        
        for package in self.default_packages:
            print(f"Installing {package}...")
            result = self.install_package(package)
            if not result.get("success", False):
                print(f"Warning: Failed to install default package '{package}'")
            else:
                print(f"Successfully installed {package}")
        
        print("Default packages installation completed")
        print()  # Add blank line for consistency

    def _indent_code(self, code: str, indent: str = "    ") -> str:
        """Indent code for inclusion in a try block."""
        return '\n'.join(indent + line for line in code.split('\n'))

    def get_namespace(self) -> Dict[str, Any]:
        """Get the current namespace from volume storage."""
        # Read current state from volume
        code = '''
import json
import os

STATE_FILE = '/app/state/kernel_state.json'
try:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        print(f"NAMESPACE_JSON:{json.dumps(state)}")
    else:
        print("NAMESPACE_JSON:{}")
except Exception as e:
    print(f"Error reading namespace: {e}")
    print("NAMESPACE_JSON:{}")
'''
        
        result = self.docker_runner.execute(code)
        if result.success:
            for line in result.output.strip().split('\n'):
                if line.startswith("NAMESPACE_JSON:"):
                    try:
                        return json.loads(line[15:])
                    except json.JSONDecodeError:
                        pass
        
        return {}

    def set_variable(self, name: str, value: Any) -> bool:
        """Set a variable in the volume-stored namespace."""
        # Test if value is serializable
        if callable(value) and hasattr(value, '__code__'):
            # Handle functions - get source code
            try:
                import inspect
                import textwrap
                func_source = inspect.getsource(value)
                func_source = textwrap.dedent(func_source)
                
                code = f'''
import json
import os

STATE_FILE = '/app/state/kernel_state.json'
try:
    # Load current state
    state = {{}}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    # Add function
    if '__functions__' not in state:
        state['__functions__'] = {{}}
    state['__functions__']['{name}'] = {repr(func_source)}
    
    # Save state
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    print("Function set successfully")
except Exception as e:
    print(f"Error setting function: {{e}}")
'''
                result = self.docker_runner.execute(code)
                return result.success
            except (OSError, TypeError):
                return False
        else:
            # Handle regular JSON-serializable objects
            try:
                json.dumps(value)  # Test if serializable
                
                code = f'''
import json
import os

STATE_FILE = '/app/state/kernel_state.json'
try:
    # Load current state
    state = {{}}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    # Set variable
    state['{name}'] = {repr(value)}
    
    # Save state
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    print("Variable set successfully")
except Exception as e:
    print(f"Error setting variable: {{e}}")
'''
                result = self.docker_runner.execute(code)
                return result.success
            except (TypeError, ValueError):
                return False

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable from the volume-stored namespace."""
        namespace = self.get_namespace()
        return namespace.get(name, default)

    def install_package(self, package_name: str) -> Dict[str, Any]:
        """Install a Python package in the Docker environment."""
        return self.execute(f"""
import subprocess
import sys

print(f"Installing {package_name}...")
result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '{package_name}'], 
                      capture_output=True, text=True)
if result.returncode == 0:
    print(f"Successfully installed {package_name}")
    print("Package is now available for use!")
else:
    print(f"Failed to install {package_name}")
    print(f"Error: {{result.stderr.strip()}}")
""")

    def cleanup(self) -> bool:
        """Clean up the persistent volumes for this kernel session."""
        return self.docker_runner.cleanup_volumes()