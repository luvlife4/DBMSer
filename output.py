import os
import time
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
console = Console()
parts = [
    ("red", "DBM"),
    ("dark_orange", "Ser"),
    ("yellow", "Th"),
    ("green", "in"),
    ("cyan", "ki"),
    ("blue", "ng"),
    ("magenta", "...."),
]
def print_welcome():
    console.print(
        "[red]开始聊天，[/red]"
        "[dark_orange]我是[/dark_orange]"
        "[yellow]DBMSer[/yellow]"
        "[green]，欢迎[/green]"
        "[cyan]随时[/cyan]"
        "[blue]提问[/blue]"
        "[magenta]！[/magenta]"
    )

def render_reply(reply: str):
    console.print(
        Panel(
            Markdown(reply),
            title="DBMSer",
            border_style="cyan"
        )
    )

def print_thinking():
    for color, text in parts:
        console.print(f"[bold {color}]{text}[/bold {color}]", end="")
        time.sleep(0.06)
        sys.stdout.flush() 
    console.print()