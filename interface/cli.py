"""
Simple CLI interface for the coding agent.
Provides colored output and basic interaction features.
"""

import os
import sys
import asyncio
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.style import Style
from pyfiglet import Figlet
from src.config import config

# Import LangGraph agent
from src.langgraph_agent import (
    create_langgraph_agent,
    get_memory,
    stream_simple,
    AgentState
)


console = Console()


def print_agentcode_ascii(
    console: Console,
    text: str = "AgentCode",
    font: str = "ansi_shadow",
    gradient: str = "dark_to_light",
) -> None:
    """Print AgentCode ASCII art banner with gradient colors."""
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _lerp(a, b, t):
        return int(a + (b - a) * t)

    def _interpolate_palette(palette, width):
        if width <= 1:
            return [palette[0]]
        out, steps_total = [], width - 1
        for x in range(width):
            pos = x / steps_total
            seg = min(int(pos * (len(palette) - 1)), len(palette) - 2)
            seg_start, seg_end = seg / (len(palette) - 1), (seg + 1) / (len(palette) - 1)
            local_t = (pos - seg_start) / (seg_end - seg_start + 1e-9)
            c1, c2 = _hex_to_rgb(palette[seg]), _hex_to_rgb(palette[seg + 1])
            rgb = tuple(_lerp(a, b, local_t) for a, b in zip(c1, c2))
            out.append("#{:02x}{:02x}{:02x}".format(*rgb))
        return out

    def _print_block_with_horizontal_gradient(lines, palette):
        width = max(len(line) for line in lines) if lines else 0
        ramp = _interpolate_palette(palette, width)
        for line in lines:
            t = Text()
            padded = line.ljust(width)
            for j, ch in enumerate(padded):
                t.append(ch if ch == " " else ch, Style(color=ramp[j], bold=True))
            console.print(t)

    fig = Figlet(font=font)
    lines = fig.renderText(text).rstrip("\n").splitlines()
    # AgentCode color palette - blue to cyan gradient
    palette = ["#1e3a8a", "#1e40af", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe"]
    if gradient == "light_to_dark":
        palette = list(reversed(palette))
    _print_block_with_horizontal_gradient(lines, palette)


def print_welcome():
    """Print welcome message with AgentCode banner."""
    # Print the AgentCode ASCII banner
    print_agentcode_ascii(console)
    
    # Print welcome text below the banner
    welcome_text = Text("🤖 A simple agent for CRUD operations on codebases", style="bold blue")
    welcome_text.append("\nType 'help' for commands, 'quit' to exit")
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))


def print_help():
    """Print help information."""
    help_table = Table(title="Available Commands")
    help_table.add_column("Command", style="cyan")
    help_table.add_column("Description", style="white")
    
    help_table.add_row("help", "Show this help message")
    help_table.add_row("sessions", "List available sessions")
    help_table.add_row("session <id>", "Switch to a session")
    help_table.add_row("info", "Show current session info")
    help_table.add_row("config", "Show current configuration")
    help_table.add_row("multiline", "Enter multi-line input mode")
    help_table.add_row("clear", "Clear current session")
    help_table.add_row("quit/exit", "Exit the agent")
    help_table.add_row("", "")
    help_table.add_row("Or just type your request!", "The agent will help you with coding tasks")
    
    console.print(help_table)


def print_session_info(session_id: str):
    """Print current session information."""
    info_text = f"""
Session ID: {session_id}
Agent: LangGraph 2-Agent System
Memory: Automatic checkpointing enabled
"""
    console.print(Panel(info_text, title="Session Info", border_style="green"))


def list_sessions():
    """List available sessions."""
    memory = get_memory()
    sessions = memory.list_sessions()
    
    if not sessions:
        console.print("[yellow]No sessions found (sessions are in-memory for current run).[/yellow]")
        return
    
    session_table = Table(title="Available Sessions")
    session_table.add_column("Session ID", style="cyan")
    
    for session_id in sessions:
        session_table.add_row(session_id[:8] + "...")
    
    console.print(session_table)


def get_multiline_input() -> str:
    """Get multi-line input from user."""
    console.print("[dim]Enter your request (press Ctrl+D or type 'END' on a new line when done):[/dim]")
    lines = []
    
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
    except EOFError:
        # Ctrl+D pressed
        pass
    
    return "\n".join(lines).strip()


def handle_command(command: str, current_session_id: str, agent, stream: bool) -> tuple:
    """Handle special commands. Returns (action, new_session_id) where action is 'quit', 'handled', or 'continue'."""
    cmd = command.strip().lower()
    
    if cmd == "help":
        print_help()
        return ("handled", current_session_id)
    
    elif cmd == "sessions":
        list_sessions()
        return ("handled", current_session_id)
    
    elif cmd.startswith("session "):
        new_session_id = command[8:].strip()
        if new_session_id:
            console.print(f"[green]Switched to session: {new_session_id}[/green]")
            return ("handled", new_session_id)
        else:
            console.print("[red]Please provide a session ID[/red]")
        return ("handled", current_session_id)
    
    elif cmd == "info":
        print_session_info(current_session_id)
        return ("handled", current_session_id)
    
    elif cmd == "clear":
        if Confirm.ask("Are you sure you want to clear the current session?"):
            # Generate new session ID
            import uuid
            new_session_id = str(uuid.uuid4())
            console.print(f"[green]Session cleared. Started new session: {new_session_id}[/green]")
            return ("handled", new_session_id)
        return ("handled", current_session_id)
    
    elif cmd == "config":
        config.print_config()
        return ("handled", current_session_id)
    
    elif cmd == "multiline":
        console.print("[green]Multi-line input mode activated![/green]")
        user_input = get_multiline_input()
        if user_input:
            # Process the multi-line input
            console.print("[dim]Processing...[/dim]")
            try:
                if stream:
                    asyncio.run(process_streaming_response(agent, user_input, current_session_id))
                else:
                    result = process_non_streaming(agent, user_input, current_session_id)
                    console.print(Panel(result, title="Agent", border_style="green"))
            except Exception as e:
                console.print(f"[red]Agent error: {e}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return ("handled", current_session_id)
    
    elif cmd in ["quit", "exit"]:
        return ("quit", current_session_id)
    
    return ("continue", current_session_id)


def create_initial_state(user_input: str, session_id: str) -> AgentState:
    """
    Create initial state for LangGraph agent.
    
    Note: Only sets NEW values. LangGraph checkpointer will restore 
    previous state (like messages) automatically when using the same session_id.
    """
    return {
        "user_input": user_input,
        "session_id": session_id,
        "response": "",
        "plan": [],
        "execution_results": [],
        "files_modified": [],
        "next_action": "",
        "tool_call_count": 0,
        "retry_count": 0,
        "reflection_notes": []
        # Note: "messages" is NOT reset here - checkpointer restores it
    }


async def process_streaming_response(agent, user_input: str, session_id: str):
    """Process agent response with streaming for real-time feedback."""
    try:
        async for chunk in stream_simple(agent, user_input, session_id):
            console.print(chunk, end="")
        console.print("\n")
        return True
    except Exception as e:
        console.print(f"\n[red]Streaming error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def process_non_streaming(agent, user_input: str, session_id: str) -> str:
    """Process agent response without streaming."""
    try:
        initial_state = create_initial_state(user_input, session_id)
        
        # Get memory config
        memory = get_memory()
        config_dict = memory.get_config(session_id)
        
        # Invoke agent
        result = agent.invoke(initial_state, config_dict)
        
        # Format response
        response = result.get("response", "No response generated")
        
        # Add execution details
        execution_results = result.get("execution_results", [])
        if execution_results:
            successful = sum(1 for r in execution_results if r.get("success"))
            response += f"\n\n[dim]Executed {successful}/{len(execution_results)} steps successfully[/dim]"
        
        files_modified = result.get("files_modified", [])
        if files_modified:
            response += f"\n[dim]Files modified: {', '.join(files_modified)}[/dim]"
        
        retry_count = result.get("retry_count", 0)
        if retry_count > 0:
            response += f"\n[dim]Retries: {retry_count}[/dim]"
        
        return response
        
    except Exception as e:
        import traceback
        return f"[red]Error: {e}[/red]\n[dim]{traceback.format_exc()}[/dim]"


@click.command()
@click.option("--session-id", help="Start with specific session ID")
@click.option("--model", default=None, help="OpenAI model to use (overrides config)")
@click.option("--stream/--no-stream", default=True, help="Enable streaming mode (default: enabled)")
def main(session_id: Optional[str], model: str, stream: bool):
    """Start the coding agent CLI with LangGraph."""
    
    # Check for OpenAI API key
    if not config.get_openai_api_key():
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        console.print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Validate configuration
    if not config.validate_config():
        console.print("[red]Configuration validation failed. Please check the errors above.[/red]")
        sys.exit(1)
    
    # Initialize LangGraph agent with memory
    console.print("[dim]Initializing LangGraph agent...[/dim]")
    agent = create_langgraph_agent(with_memory=True)
    
    # Generate or use provided session ID
    import uuid
    if not session_id:
        session_id = str(uuid.uuid4())
    
    console.print(f"[green]Session: {session_id}[/green]")
    
    print_welcome()
    
    # Main interaction loop
    current_session_id = session_id
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Handle special commands
            command_result, new_session_id = handle_command(user_input, current_session_id, agent, stream)
            
            # Update session if changed
            if new_session_id != current_session_id:
                current_session_id = new_session_id
            
            if command_result == "quit":  # quit command
                break
            elif command_result == "handled":  # special command handled
                continue
            
            # Process with agent (only if not a special command)
            try:
                if stream:
                    # Use streaming mode
                    asyncio.run(process_streaming_response(agent, user_input, current_session_id))
                else:
                    # Use non-streaming mode
                    console.print("[dim]Processing...[/dim]")
                    response = process_non_streaming(agent, user_input, current_session_id)
                    console.print(Panel(response, title="Agent", border_style="green"))
            except Exception as e:
                console.print(f"[red]Agent error: {e}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit gracefully[/yellow]")
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()
