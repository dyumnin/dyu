from .toolbase import ToolBase
from .patterns import COMMANDS

class VCS(ToolBase):
    def __init__(self, dotf: str, paths: list,max_iterations:int=50):
        """Initialize VCS with tool-specific configuration."""
        super().__init__(
            tool="vcs",
            dotf=dotf,
            paths=paths,
            include_directive="+incdir+",
            include_group=0,  # First group for include file
            module_group=2,  # Group 3 for both error types
            error_prefixes=["Error-[", "** Error:", "** at"],
            max_iterations = max_iterations
        )
        self.COMMAND = COMMANDS["vcs"]

if __name__ == "__main__":
    VCS("files.f", ["."]).main()
