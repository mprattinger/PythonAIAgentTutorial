from datetime import datetime, timezone

from agent.memory import MemoryManager


def build_system_prompt(memory: MemoryManager, channel: str | None, chat_id: str | None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        "You are a personal AI assistant.",
        f"Current date/time: {now}",
        f"Workspace: {memory.workspace}",
        f"Always use absolute paths when reading or writing files. Your workspace is {memory.workspace}.",
    ]

    if channel:
        parts.append(f"Channel: {channel}")
    if chat_id:
        parts.append(f"Chat ID: {chat_id}")

    sections = ["\n".join(parts)]

    for tag, content in memory.read_all().items():
        sections.append(f"<{tag}>\n{content}\n</{tag}>")

    return "\n\n".join(sections)
