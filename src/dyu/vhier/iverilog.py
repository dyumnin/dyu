from .toolbase import ToolBase
from .patterns import COMMANDS


class Iverilog(ToolBase):
    def __init__(self, dotf: str, paths: list, max_iterations: int = 50):
        """Initialize Iverilog with tool-specific configuration."""
        super().__init__(
            tool="iverilog",
            dotf=dotf,
            paths=paths,
            include_directive="+incdir+",
            include_group=2,  # Third group for include file
            module_group=0
            if "UNCOMPILED_MODULE" in COMMANDS["iverilog"]
            else 1,  # Group 1 for MODULE_NOT_DEFINED
            error_prefixes=["Error:", "** Error:", "** at"],
            max_iterations=max_iterations,
        )
        self.COMMAND = COMMANDS["iverilog"]


if __name__ == "__main__":
    Iverilog("files.f", ["."]).main()
