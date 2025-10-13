import os
import subprocess
import re
from typing import List, Tuple, Optional
from .common import FileUtils
from .patterns import TOOLS, COMMANDS


class ToolBase:
    def __init__(
        self,
        tool: str,
        dotf: str,
        paths: List[str],
        include_directive: str,
        include_group: int,
        module_group: int,
        error_prefixes: List[str],
        max_iterations: int = 50,
    ):
        """Initialize ToolBase with tool-specific configuration."""
        self.CURRENT_TOOL = tool
        self.MESSAGE_TYPES = TOOLS.get(self.CURRENT_TOOL, {})
        self.COMMAND = COMMANDS.get(self.CURRENT_TOOL, [])
        self.fu = FileUtils(dotf, paths)
        self.include_directive = include_directive
        self.include_group = include_group
        self.module_group = module_group
        self.error_prefixes = error_prefixes
        self.max_iterations = max_iterations

    def run_command(self) -> str:
        """Run the tool command and return its output."""
        try:
            print("Running ", " ".join(self.COMMAND))
            result = subprocess.run(
                self.COMMAND, capture_output=True, text=True, check=False
            )
            if result.stdout.strip():
                print(f"STDOUT (length: {len(result.stdout)}):")
                print(
                    result.stdout.strip()[:500] + "..."
                    if len(result.stdout) > 500
                    else result.stdout.strip()
                )
            if result.stderr.strip():
                print(f"STDERR (length: {len(result.stderr)}):")
                print(
                    result.stderr.strip()[:500] + "..."
                    if len(result.stderr) > 500
                    else result.stderr.strip()
                )
            return (result.stdout + result.stderr).strip()
        except FileNotFoundError:
            print(
                f"Error: '{self.CURRENT_TOOL}' command not found. Ensure it is installed and in PATH."
            )
            return ""
        except subprocess.SubprocessError as e:
            print(f"Error running {self.CURRENT_TOOL}: {e}")
            return ""

    def parse_output(self, output: str) -> List[Tuple[str, tuple]]:
        """Parse the output for message types and return a list of (type, match_data) tuples."""
        matches = []
        print(f"Total output length: {len(output)}")
        if len(output) > 10000:
            print(
                f"Warning: Large output ({len(output)} characters) may slow down parsing. Consider truncating or filtering."
            )

        lines = output.splitlines()
        match_objects = []
        for msg_type, pattern in self.MESSAGE_TYPES.items():
            print(f"Testing pattern for {msg_type}")
            try:
                compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
                found_matches = list(compiled_pattern.finditer(output))
                print(f"Found {len(found_matches)} matches for {msg_type}")
                for i, match in enumerate(found_matches):
                    groups = match.groups()
                    print(f"  Match {i+1}: groups = {groups}")
                    matches.append((msg_type, groups))
                    match_objects.append(match)
            except re.error as e:
                print(f"Regex error for {msg_type}: {e}")
                continue

        unmatched_errors = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if any(line.startswith(prefix) for prefix in self.error_prefixes):
                error_block = [line]
                j = i + 1
                while j < len(lines) and (
                    lines[j].startswith(
                        (" ", "\t", "** while parsing file included at")
                    )
                ):
                    error_block.append(lines[j])
                    j += 1
                unmatched_errors.append("\n".join(error_block))
                i = j
            else:
                i += 1

        matched_lines = {match.group(0) for match in match_objects}
        unmatched_errors = [
            error
            for error in unmatched_errors
            if not any(line in matched_lines for line in error.splitlines())
        ]
        if unmatched_errors:
            print(f"Unmatched errors ({len(unmatched_errors)}):")
            for error in unmatched_errors[:5]:
                print(f"  {error}")

        return matches

    def get_prepend_pattern(self, error_type: str, match_data: tuple) -> Optional[str]:
        """Generate the pattern to prepend based on error type."""
        content = self.fu._read_file(self.fu.FILES_F) or ""
        if error_type == "INCLUDE_ERROR":
            include_file = match_data[self.include_group]
            include_path = self.fu.find_include_file(include_file)
            if include_path:
                inc_pattern = f"{self.include_directive}{include_path}"
                if inc_pattern in content:
                    print(f"Skipping {inc_pattern} (already in {self.fu.FILES_F})")
                    return None
                return f"{inc_pattern}\n"
        elif error_type == "MACRO_ERROR":
            macro_name = match_data[-1]  # Last group is macro name
            macro_file = self.fu.find_macro_file(macro_name)
            if macro_file:
                if macro_file in content:
                    print(f"Skipping {macro_file} (already in {self.fu.FILES_F})")
                    return None
                return f"{macro_file}\n"
        elif error_type == "TYPEDEF_ERROR":
            file_path, line_num, typedef_name = match_data[:3]
            print(
                f"Warning: Typedef '{typedef_name}' multiply defined in {file_path}:{line_num}. "
                f"Check for redundant include dirs in {self.fu.FILES_F} or missing include guards."
            )
            return None
        return None

    def get_append_pattern(self, error_type: str, match_data: tuple) -> Optional[str]:
        """Generate the pattern to append for uncompiled modules or module not defined errors."""
        if error_type in ["UNCOMPILED_MODULE", "MODULE_NOT_DEFINED"]:
            modules = (
                match_data[self.module_group].strip().split()
                if error_type == "UNCOMPILED_MODULE"
                else [match_data[self.module_group].strip()]
            )
            patterns = []
            content = self.fu._read_file(self.fu.FILES_F) or ""
            for module in modules:
                module_name = (
                    os.path.basename(module).replace(".v", "").replace(".sv", "")
                )
                module_file = self.fu.find_module_file(module_name)
                if module_file:
                    if module_file in content:
                        print(f"Skipping {module_file} (already in {self.fu.FILES_F})")
                        continue
                    patterns.append(f"{module_file}\n")
            return "".join(patterns) if patterns else None
        return None

    def main(self) -> None:
        """Run the error handling loop for the tool."""
        print(f"Starting {self.CURRENT_TOOL} error handler...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Using tool: {self.CURRENT_TOOL}")
        content = self.fu._read_file(self.fu.FILES_F)
        if content:
            print(f"Initial {self.fu.FILES_F} content: {repr(content)}")
            self.fu.check_files_f_duplicates(content)

        iteration = 0
        max_iterations = self.max_iterations
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            print("Running")
            output = self.run_command()
            print("Done Running")
            if not output:
                print("No output from command. Exiting.")
                break

            matches = self.parse_output(output)
            if not matches:
                print("No more message types matched. Exiting.")
                break

            for msg_type, match_data in matches:
                if msg_type in ["UNCOMPILED_MODULE", "MODULE_NOT_DEFINED"]:
                    pattern = self.get_append_pattern(msg_type, match_data)
                    if pattern:
                        self.fu.append_to_file(pattern)
                else:
                    pattern = self.get_prepend_pattern(msg_type, match_data)
                    if pattern:
                        self.fu.prepend_to_file(pattern)
                if not pattern and msg_type != "TYPEDEF_ERROR":
                    print(f"No valid pattern found for {msg_type}: {match_data}")
