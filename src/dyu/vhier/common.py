import os
from typing import List, Optional, Union
from pathlib import Path


class FileUtils:
    def __init__(self, dotf: str, paths: List[str]) -> None:
        """Initialize FileUtils with files.f path and search directories, validating their existence."""
        self.FILES_F: str = dotf if dotf else "files.f"

        # Validate files.f path and write permissions
        if os.path.exists(self.FILES_F) and not os.access(self.FILES_F, os.W_OK):
            raise PermissionError(f"Cannot write to {self.FILES_F} (permissions?)")
        elif not os.access(os.path.dirname(self.FILES_F) or ".", os.W_OK):
            raise PermissionError(
                f"Cannot write to directory for {self.FILES_F} (permissions?)"
            )

        # Initialize and validate search directories
        self.search_dirs: List[str] = paths or ["."]
        self.search_dirs.extend(os.getenv("VERILOG_SEARCH_PATH", "").split(":"))
        self.search_dirs = [d for d in self.search_dirs if d and os.path.exists(d)]
        if not self.search_dirs:
            raise ValueError(
                "No valid search directories provided or found in VERILOG_SEARCH_PATH"
            )

        # Log invalid directories
        invalid_dirs = [
            d
            for d in (paths or []) + os.getenv("VERILOG_SEARCH_PATH", "").split(":")
            if d and not os.path.exists(d)
        ]
        for invalid_dir in invalid_dirs:
            print(f"Search directory does not exist: {invalid_dir}")

    def _read_file(self, file_path: str) -> Optional[str]:
        """Read content from a file and handle potential errors."""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except IOError as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def _write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file and handle potential errors."""
        try:
            with open(file_path, "w") as f:
                f.write(content)
            return True
        except IOError as e:
            print(f"Error writing to {file_path}: {e}")
            return False

    def check_files_f_duplicates(self, content: str) -> List[str]:
        """Check files.f for duplicate include directory entries."""
        lines = content.splitlines()
        incdirs = [
            line.strip()
            for line in lines
            if line.strip().startswith(("-incdir", "+incdir+", "-y"))
        ]
        unique_incdirs = list(
            dict.fromkeys(incdirs)
        )  # Preserve order, remove duplicates
        if len(incdirs) > len(unique_incdirs):
            print(
                f"Warning: Duplicate include dir entries found in {self.FILES_F}: {incdirs}"
            )
            print(f"Unique include dir entries: {unique_incdirs}")
        return unique_incdirs

    def deduplicate_files_f(self) -> None:
        """Remove duplicate include directory entries from files.f."""
        content = self._read_file(self.FILES_F)
        if content is None:
            return

        lines = content.splitlines()
        incdirs = self.check_files_f_duplicates(content)
        other_lines = [
            line
            for line in lines
            if not line.strip().startswith(("-incdir", "+incdir+", "-y"))
        ]
        new_content = "\n".join(incdirs + other_lines) + "\n"

        if new_content != content:
            if self._write_file(self.FILES_F, new_content):
                print(f"Deduplicated {self.FILES_F}: {repr(new_content[:100])}...")

    def _search_file_in_dirs(
        self, file_name: str, extensions: Union[str, List[str]] = ""
    ) -> Optional[str]:
        """Search for a file with given name and optional extensions in search directories."""
        if isinstance(extensions, str):
            extensions = [extensions] if extensions else []

        for root in self.search_dirs:
            for dirpath, _, files in os.walk(root, followlinks=True):
                candidates = (
                    [file_name]
                    if not extensions
                    else [f"{file_name}{ext}" for ext in extensions]
                )
                for candidate in candidates:
                    if candidate in files:
                        full_path = os.path.join(dirpath, candidate)
                        if os.access(full_path, os.R_OK):
                            print(f"Found {file_name} at: {full_path}")
                            return os.path.abspath(full_path)
                        print(
                            f"Found {file_name} at {full_path} but cannot read (permissions?)"
                        )
            print(f"Recursively searched for {file_name} in {root}")
        print(f"Could not find {file_name} in search directories")
        return None

    def find_include_file(self, include_file: str) -> Optional[str]:
        """Recursively search for the include file and return its directory path."""
        full_path = self._search_file_in_dirs(include_file)
        return os.path.dirname(full_path) if full_path else None

    def find_macro_file(self, macro_name: str) -> Optional[str]:
        """Recursively search for a file containing the macro definition and return its path."""
        for root in self.search_dirs:
            for dirpath, _, files in os.walk(root, followlinks=True):
                for file in files:
                    if file.endswith((".v", ".vh")):
                        file_path = os.path.join(dirpath, file)
                        if not os.access(file_path, os.R_OK):
                            print(f"Cannot read {file_path} (permissions?)")
                            continue
                        content = self._read_file(file_path)
                        if content and f"`define {macro_name}" in content:
                            full_path = os.path.abspath(file_path)
                            print(f"Found macro {macro_name} in: {full_path}")
                            return full_path
            print(f"Recursively searched for macro {macro_name} in {root}")
        print(f"Could not find definition for macro {macro_name}")
        return None

    def find_module_file(self, module_name: str) -> Optional[str]:
        """Recursively search for a .v or .sv file for the given module and return its full path."""
        return self._search_file_in_dirs(module_name, [".v", ".sv"])

    def _modify_file_content(
        self, content: Optional[str], existing_content: str, mode: str
    ) -> None:
        """Modify files.f content by prepending or appending."""
        if content is None:
            return

        print(f"{mode.capitalize()}ing to {self.FILES_F}: {repr(content)}")
        self.deduplicate_files_f()

        existing = self._read_file(self.FILES_F) or ""
        new_content = content + existing if mode == "prepend" else existing + content

        if self._write_file(self.FILES_F, new_content):
            print(f"Updated {self.FILES_F} successfully ({mode}ed)")

    def prepend_to_file(self, content: Optional[str]) -> None:
        """Prepend content to the beginning of files.f."""
        self._modify_file_content(
            content, self._read_file(self.FILES_F) or "", "prepend"
        )

    def append_to_file(self, content: Optional[str]) -> None:
        """Append content to the end of files.f."""
        self._modify_file_content(
            content, self._read_file(self.FILES_F) or "", "append"
        )
