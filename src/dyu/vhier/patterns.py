# patterns.py
# Defines regex patterns for different tools, optimized and robust against arbitrary line breaks

TOOLS = {
    "vlog": {
        "INCLUDE_ERROR": r"\*\* Error:\s*(.*?)\s*\((\d+)\):\s*Cannot find `include file\s*\"(.*?)\"\s*in directories\s*:",
        "MACRO_ERROR": r"\*\* Error:\s*(.*?)\s*\((\d+)\):\s*\(vlog-2163\)\s*Macro\s*`(.*?)`\s*is undefined\s*",
        "UNCOMPILED_MODULE": r"Referenced\s*\(but uncompiled\)\s*modules or primitives\s*:\s*((?:[\w]+\s*)+)",
        "TYPEDEF_ERROR": r"\*\* at\s*(.*?)\s*\((\d+)\):\s*\(vlog-2426\)\s*Typedef\s*'(.*?)'\s*multiply defined\s*\.\s*Previous definition found at",
        "MODULE_NOT_DEFINED": r"\*\* Error:\s*(.*?)\s*\((\d+)\):\s*Module\s*'([\w]+)'\s*is not defined\s*"
    },
    "iverilog": {
        "INCLUDE_ERROR": r"(.*?)\s*:(\d+)\s*:\s*Include file\s*(.*?)\s*not found\s*",
        "MACRO_ERROR": r"Error\s*:\s*(.*?)\s*:\s*\(vlog-2163\)\s*Macro\s*`(.*?)`\s*is undefined\s*\.",
        "UNCOMPILED_MODULE": r"Referenced\s*\(but uncompiled\)\s*modules or primitives\s*:\s*((?:[\w]+\s*)+)",
        "TYPEDEF_ERROR": r"Error\s*:\s*(.*?)\s*:\s*\(vlog-2426\)\s*Typedef\s*'(.*?)'\s*multiply defined\s*\.\s*Previous definition found at",
        "MODULE_NOT_DEFINED": r"Error\s*:\s*(.*?)\s*:\s*Module\s*'([\w]+)'\s*is not defined\s*"
    },
    "vcs": {
        "INCLUDE_ERROR": r"Error-\[SFCOR\]\s*Source file cannot be opened\s*Source file\s*\"(.*?)\"\s*cannot be opened for reading\s*due to\s*'No such file or\s*directory'\s*\.\s*(?:[^\n]*\n)*?\s*\"([^\"]+)\"\s*,\s*(\d+)",
        "MACRO_ERROR": r"Error-\[UM\]\s*Undefined macro\s*(.*?)\s*,\s*(\d+)\s*(?:[^\n]*\n)*?\s*Undefined macro exists as\s*:\s*'(.*?)'",
        "UNCOMPILED_MODULE": r"Error-\[URMI\]\s*Unresolved modules\s*(.*?)\s*,\s*(\d+)\s*(?:[^\n]*\n)*?\s*\"\s*(\w+)(?:[\s\S]*?)?\"\s*Module definition of above instance is not found\s*",
        "TYPEDEF_ERROR": r"Error-\[TDEF\]\s*Typedef multiply defined\s*(.*?)\s*,\s*(\d+)\s*(?:[^\n]*\n)*?\s*Typedef\s*'(.*?)'\s*multiply defined\s*",
        "MODULE_NOT_DEFINED": r"Error-\[URMI\]\s*Unresolved modules\s*(.*?)\s*,\s*(\d+)\s*(?:[^\n]*\n)*?\s*\"\s*(\w+)(?:[\s\S]*?)?\"\s*Module definition of above instance is not found\s*"
    }
}
COMMANDS= {
         "vlog":["vlog", "-sv", "-f", "files.f"],
         "vcs":["vcs", "-full64", "-f", "files.f", "-sverilog", "-timescale=1ps/1ps"],
         "iverilog":["iverilog", "-g2012", "-f", "files.f"]
         }
