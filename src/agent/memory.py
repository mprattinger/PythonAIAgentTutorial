import os
import shutil

WORKSPACE = os.path.expanduser("~/.ai-assistant/workspace")
TEMPLATES = os.path.join(os.path.dirname(
    __file__), "..", "workspace-templates")


class MemoryManager:
    def __init__(self):
        os.makedirs(WORKSPACE, exist_ok=True)
        self.workspace = WORKSPACE
        self._seed_templates()

    def _seed_templates(self):
        templates_dir = os.path.abspath(TEMPLATES)

        if not os.path.isdir(templates_dir):
            return

        is_fresh = not os.path.exists(os.path.join(self.workspace, "SOUL.md"))
        for filename in os.listdir(templates_dir):
            if filename == "BOOTSTRAP.md" and not is_fresh:
                continue
            dest = os.path.join(self.workspace, filename)
            if not os.path.exists(dest):
                shutil.copy2(os.path.join(templates_dir, filename), dest)

    def read_all(self) -> dict[str, str]:
        files = ["AGENTS.md", "BOOTSTRAP.md",
                 "MEMORY.md", "SOUL.md", "USER.md"]
        result = {}
        for filename in files:
            path = os.path.join(self.workspace, filename)
            try:
                with open(path) as f:
                    content = f.read().strip()
                if content:
                    key = os.path.splitext(filename)[0].lower()
                    result[key] = content
            except FileNotFoundError:
                pass

        return result
