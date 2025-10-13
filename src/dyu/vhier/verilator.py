from .toolbase import ToolBase
from .patterns import COMMANDS


class Verilator(ToolBase):
    def __init__(self, dotf: str, paths: list, max_iterations: int = 50):
        """Initialize Iverilog with tool-specific configuration."""
        super().__init__(
            tool="verilator",
            dotf=dotf,
            paths=paths,
            include_directive="+incdir+",
            include_group=1,  # Third group for include file
            module_group=1,
            # if "UNCOMPILED_MODULE" in COMMANDS["verilator"]
            # else 1,  # Group 1 for MODULE_NOT_DEFINED
            error_prefixes=["Error:", "** Error:", "** at"],
            max_iterations=max_iterations,
        )
        self.COMMAND = COMMANDS["verilator"]


if __name__ == "__main__":
    Verilator("files.f", ["."]).main()
