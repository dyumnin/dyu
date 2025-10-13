# dotf generator

## Overview
The dotf generator is a Python-based tool designed to automate the process of resolving common Verilog compilation errors for tools like Synopsys VCS, Icarus Verilog (`iverilog`), and ModelSim/QuestaSim (`vlog`). It parses error messages from these tools, identifies issues such as missing include files, undefined macros, or uncompiled modules, and updates a `files.f` file by prepending or appending necessary file paths or include directives. The tool supports iterative error resolution with a safety limit to prevent infinite loops.

## Features
- **Error Parsing**: Identifies errors like missing includes, macros, or modules using tool-specific regex patterns.
- **File Management**: Automatically updates `files.f` by adding include directories or source files, with duplicate detection and removal.
- **Tool Support**: Supports VCS, Icarus Verilog, and ModelSim/QuestaSim with customizable commands and error patterns.
- **Search Path Handling**: Recursively searches for files in specified directories or those defined in the `VERILOG_SEARCH_PATH` environment variable.
- **Robust Error Handling**: Validates file permissions and directory existence upfront, with detailed logging.

## Installation

### Prerequisites
- **Python 3.8+**: Ensure Python is installed.
- **Verilog Tools**: Install at least one of the supported tools (VCS, Icarus Verilog, or ModelSim/QuestaSim) and ensure their executables are in your system’s `PATH`.
- **Dependencies**: No external Python packages are required beyond the standard library.

### Setup
1. `pip install dyu`
2. Ensure the Verilog tool executables (`vcs`, `iverilog`, or `vlog`) are accessible in your `PATH`.
3. Optionally, set the `VERILOG_SEARCH_PATH` environment variable to specify directories for searching Verilog files, e.g.:
   ```bash
   export VERILOG_SEARCH_PATH=/path/to/dir1:/path/to/dir2
   ```

## Usage

### Running the Tool
The tool is available as a part of the dyu package and can be run with

```bash
dyu vhier <toolname>
```

Specify the desired Verilog tool as a command-line argument The default tool is `vcs`.


```bash
dyu vhier  [tool_name]
```

**Examples**:
- Run with VCS:
  ```bash
  dyu vhier vcs
  ```
- Run with Icarus Verilog:
  ```bash
  dyu vhier iverilog
  ```
- Run with ModelSim/QuestaSim:
  ```bash
  dyu vhier vlog
  ```

### How It Works
1. The tool validates the specified tool name against supported tools (`vcs`, `iverilog`, `vlog`).
2. It initializes a `FileUtils` instance to manage `files.f` and validate search paths.
3. The tool runs the specified Verilog tool’s command (e.g., `vcs -full64 -f files.f -sverilog -timescale=1ps/1ps`).
4. It parses the output for errors (e.g., missing includes, undefined macros, uncompiled modules).
5. Based on error types:
   - **Include/Macro Errors**: Prepends include directories or macro files to `files.f`.
   - **Module Errors**: Appends module source files to `files.f`.
   - **Typedef Errors**: Logs warnings for multiply-defined typedefs without modifying `files.f`.
6. The process repeats up to 5 iterations or until no errors remain.

### Configuration
- **files.f**: The tool reads and writes to `files.f` by default. Specify a different file using the `dotf` parameter in the tool classes
- **Search Paths**: Defaults to the current directory (`.`). Additional paths can be specified via the `VERILOG_SEARCH_PATH` environment variable or programmatically via the `paths` parameter.
- **Tool Commands**: Defined in `patterns.py`:
  ```python
  COMMANDS = {
      "vlog": ["vlog", "-sv", "-f", "files.f"],
      "vcs": ["vcs", "-full64", "-f", "files.f", "-sverilog", "-timescale=1ps/1ps"],
      "iverilog": ["iverilog", "-g2012", "-f", "files.f"]
  }
  ```

## Project Structure

| File            | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| `__init__.py`   | Entry point to select and run the specified Verilog tool.                   |
| `toolbase.py`   | Base class with shared logic for running tools, parsing errors, and updating `files.f`. |
| `vcs.py`        | VCS-specific configuration (e.g., `+incdir+`, error prefixes).              |
| `iverilog.py`   | Icarus Verilog-specific configuration (e.g., `-incdir`, error prefixes).    |
| `vlog.py`       | ModelSim/QuestaSim-specific configuration (e.g., `-incdir`, error prefixes).|
| `common.py`     | File handling utilities for searching files and managing `files.f`.         |
| `patterns.py`   | Defines `TOOLS` (error patterns) and `COMMANDS` (tool commands).            |

## File Details

- **`__init__.py`**: Initializes a `Vhier` instance to select and run a tool based on the provided tool name . Instantiates `VCS`, `Iverilog`, or `Vlog` and calls their `main` method.
- **`toolbase.py`**: Defines the `ToolBase` class with methods for running commands, parsing output, and generating patterns to update `files.f`. Tool-specific configurations (e.g., include directives, regex group indices) are set during initialization.
- **`vcs.py`, `iverilog.py`, `vlog.py`**: Inherit from `ToolBase`, specifying tool-specific parameters like include directives (`-incdir` or `+incdir+`), regex group indices for error parsing, and error prefixes.
- **`common.py`**: Contains the `FileUtils` class for file operations, including searching for include files, macros, and modules, and managing `files.f` with duplicate detection.
- **`patterns.py`**: Defines tool-specific error patterns (`TOOLS`) and commands (`COMMANDS`).

## Limitations
- The tool assumes `files.f` is in the current working directory unless specified otherwise.
- Only supports VCS, Icarus Verilog, and ModelSim/QuestaSim; additional tools require new classes and patterns.
- The iteration limit is fixed at 50 to prevent infinite loops; adjust in `toolbase.py` if needed.
- Error parsing relies on regex patterns defined in `patterns.py`, which must be maintained for accuracy.

## Troubleshooting
- **Tool Not Found**: Ensure the Verilog tool executable is in your `PATH`.
- **Permission Errors**: Check write permissions for `files.f` and its directory.
- **No Files Found**: Verify that `VERILOG_SEARCH_PATH` or the provided `paths` include directories containing the required Verilog files.
- **Unmatched Errors**: If errors are not handled, check `patterns.py` for correct regex patterns.

## Contributing
Contributions are welcome! To add support for a new tool:
1. Create a new tool class in a file (e.g., `newtool.py`) inheriting from `ToolBase`.
2. Define tool-specific parameters (e.g., include directive, error prefixes).
3. Update `patterns.py` with the tool’s command and error patterns.
4. Add the tool to `main.py`’s tool selection logic.
