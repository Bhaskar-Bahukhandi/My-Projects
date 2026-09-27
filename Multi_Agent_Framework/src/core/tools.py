import subprocess
import os

def execute_python_code(code: str) -> str:
    """
    Executes Python code and returns the stdout or stderr.
    This function is exposed to the WorkerAgent via Gemini Function Calling.
    """
    # ---------------------------------------------------------
    # SECURITY SANDBOX (Authentic Developer Note)
    # ---------------------------------------------------------
    # TODO(bhaskar): My first draft just used python's native `exec()` function.
    # This was a massive security vulnerability. If the LLM hallucinated `os.system('rm -rf /')`, 
    # it would destroy my local machine. 
    # FIX: I am writing the code to a temporary file and executing it in a subprocess 
    # with a strict 5-second timeout. In a real enterprise setting, I would run this 
    # inside an isolated Docker container, but this prevents infinite while-loops locally.
    
    temp_file = "temp_agent_execution.py"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Run in an isolated subprocess with a strict timeout
        result = subprocess.run(
            [sys.executable, temp_file] if 'sys' in globals() else ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        
        if result.returncode == 0:
            return f"Execution successful.\nOutput:\n{result.stdout}"
        else:
            return f"Execution failed.\nError:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Execution failed. Code timed out after 5 seconds (Possible infinite loop)."
    except Exception as e:
        return f"Execution failed. Error: {str(e)}"
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
def read_file(filepath: str) -> str:
    """Reads the contents of a local file."""
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
        
def write_file(filepath: str, content: str) -> str:
    """Writes content to a local file."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"
