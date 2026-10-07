import json
import os
from datetime import datetime, timezone

SESSIONS_DIR = os.path.expanduser("~/.ai-assistant/sessions")


class SessionManager:
    def __init__(self, session_key: str):
        self.session_key = session_key
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        self.path = os.path.join(SESSIONS_DIR, f"{session_key}.jsonl")
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write(json.dumps({"session_key": session_key, "created_at": datetime.now(
                    timezone.utc).isoformat()}) + "\n")

    def load(self, n: int = 50) -> list[dict]:
        messages = []
        with open(self.path, "r") as f:
            lines = f.readlines()
        for line in lines[1:]:  # skip metadata on line 0
            try:
                entry = json.loads(line)
                entry.pop("timestamp", None)
                messages.append(entry)
            except json.JSONDecodeError:
                continue
        return messages[-n:]

    def append(self, messages: list[dict]):
        ts = datetime.now(timezone.utc).isoformat()
        with open(self.path, "a") as f:
            for msg in messages:
                f.write(json.dumps({**msg, "timestamp": ts}) + "\n")
