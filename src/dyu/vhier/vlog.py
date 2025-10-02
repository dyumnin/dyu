from .toolbase import ToolBase
from .patterns import COMMANDS

class Vlog(ToolBase):
    def __init__(self, dotf: str, paths: list, max_iterations:int = 50):
        """Initialize Vlog with tool-specific configuration."""
        super().__init__(
            tool="vlog",
            dotf=dotf,
            paths=paths,
            include_directive="-incdir",
            include_group=2,  # Third group for include file
            module_group=0 if "UNCOMPILED_MODULE" in COMMANDS["vlog"] else 2,  # Group 2 for MODULE_NOT_DEFINED
            error_prefixes=["** Error:", "** at"],
            max_iterations = max_iterations
        )
        self.COMMAND = COMMANDS["vlog"]

if __name__ == "__main__":
    Vlog("files.f", ["."]).main()
