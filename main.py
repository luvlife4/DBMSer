from agent import agent_loop
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

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

if __name__ == "__main__":
    try:
        print_welcome()
        while True:
            user_input = input(">>  ").strip()
            if user_input.lower() == "exit":
                console.print("\n[yellow]下次见！[/yellow]")
                break
            if not user_input:
                continue

            reply = agent_loop(user_input)
            render_reply(reply)

    except KeyboardInterrupt:
        console.print("\n[cyan]下次见～[/cyan]")