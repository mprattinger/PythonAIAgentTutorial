import re
import asyncio

from .base import Tool


DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"mkfs",
    r"dd\s+if=",
    r":\(\)\s*\{.*\}",   # fork bomb
    r">\s*/dev/sd",
]


class ExecTool(Tool):
    name = "exec"
    description = "Run a shell command and return the output. Use for listing files, checking system state, running scripts, etc."
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            }
        },
        "required": ["command"],
    }

    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    async def execute(self, args: dict) -> str:
        command = args["command"]

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                return f"Blocked: command matches dangerous pattern '{pattern}'"

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout
            )
            return (stdout + stderr).decode().strip() or "(no output)"
        except asyncio.TimeoutError:
            return f"Error: command timed out after {self.timeout}s"
        except Exception as e:
            return f"Error executing command: {e}"
