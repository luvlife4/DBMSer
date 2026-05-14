from agent.agent import agent_loop
from output import console,print_welcome,render_reply,print_thinking
if __name__ == "__main__":
    try:
        print_welcome()
        while True:
            user_input = input(">>  ").strip()
            if user_input.lower() == "bye":
                console.print("\n[yellow]下次见！[/yellow]")
                break
            if not user_input:
                continue
            
            print_thinking()
            reply = agent_loop(user_input) 
            render_reply(reply)

    except KeyboardInterrupt:
        console.print("\n[cyan]下次见～[/cyan]")