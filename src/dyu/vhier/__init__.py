import sys
import os
from .patterns import TOOLS
from .vcs import VCS
from .iverilog import Iverilog
from .vlog import Vlog

class Vhier:
    def __init__(self, tool_name: str = "vcs", dotf: str = "files.f", max_iterations: int = 50, paths: list = None):
        """Initialize Vhier and run the selected tool's main method."""
        valid_tools = list(TOOLS.keys())
        
        # Validate tool name
        if not tool_name:
            print("Error: No tool specified. Provide a tool name as an argument or set VERILOG_TOOL environment variable.")
            print(f"Valid tools: {', '.join(valid_tools)}")
            sys.exit(1)
        
        if tool_name not in valid_tools:
            print(f"Error: Invalid tool '{tool_name}'. Valid tools: {', '.join(valid_tools)}")
            sys.exit(1)
        
        print(f"Selected tool: {tool_name}")
        
        # Instantiate and run the appropriate tool
        try:
            paths = paths or ["."]
            if tool_name == "vcs":
                tool = VCS(dotf, paths, max_iterations)
            elif tool_name == "iverilog":
                tool = Iverilog(dotf, paths, max_iterations)
            elif tool_name == "vlog":
                tool = Vlog(dotf, paths, max_iterations)
            else:
                print(f"Error: No implementation for tool '{tool_name}'")
                sys.exit(1)
            
            tool.main()
        except ImportError as e:
            print(f"Error: Failed to import {tool_name} module: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error running {tool_name}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    Vhier()
