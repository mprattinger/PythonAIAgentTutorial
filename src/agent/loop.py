import json

import litellm
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# MODEL = "openai//var/lib/llama/models/qwen2.5-7b-instruct-q4_k_m.gguf"
MAX_ITERATIONS = 20

console = Console()


def _fmt_args(args: dict) -> str:
    """Format tool args as key=value pairs, truncated."""
    parts = [
        f"[dim]{k}=[/dim][white]{str(v)[:60]}[/white]" for k, v in args.items()]
    return "  ".join(parts)


async def run_agent(
    user_message: str,
    tools: list,
    model: str,
    history: list[dict] = None,
    system_prompt: str = None,
) -> tuple[str, list[dict]]:
    history = history or []
    tool_map = {t.name: t for t in tools}
    tool_schemas = [t.schema() for t in tools]

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history)
    if user_message:
        messages.append({"role": "user", "content": user_message})

    new_messages = []
    if user_message:
        new_messages.append({"role": "user", "content": user_message})

    for _ in range(MAX_ITERATIONS):
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tool_schemas or None,
            reasoning_effort="none"
        )

        msg = response.choices[0].message

        # Convert to plain dict for storage
        assistant_msg = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        messages.append(assistant_msg)
        new_messages.append(assistant_msg)

        if not msg.tool_calls:
            # Final text response
            text = msg.content or ""
            console.print(Panel(Markdown(text), border_style="green",
                          title="[bold green]assistant[/bold green]", title_align="left"))
            return text, new_messages

        # Execute tool calls
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            console.print(
                f"  [bold magenta]⚡ {fn_name}[/bold magenta]  {_fmt_args(fn_args)}")

            tool = tool_map.get(fn_name)
            if tool:
                result = await tool.execute(fn_args)
            else:
                result = f"Error: unknown tool '{fn_name}'"

            preview = result[:200] + "..." if len(result) > 200 else result
            console.print(f"  [green]✓[/green] [dim]{preview}[/dim]")
            console.print()

            tool_result_msg = {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            }
            messages.append(tool_result_msg)
            new_messages.append(tool_result_msg)

    error = "Error: max iterations reached"
    console.print(Panel(error, border_style="red"))
    return error, new_messages
