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

from src.agent import get_agent
from src.memory import memory_manager
from src.config import config


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


def print_session_info():
    """Print current session information."""
    agent = get_agent()
    info = agent.get_session_info()
    
    if "error" in info:
        console.print(f"[red]Error: {info['error']}[/red]")
        return
    
    info_text = f"""
Session ID: {info['session_id']}
Messages: {info['message_count']}
Files in context: {info['files_in_context']}
Created: {info['created_at']}
Last updated: {info['last_updated']}
"""
    
    if info['last_error']:
        info_text += f"Last error: {info['last_error']['error']}"
    
    console.print(Panel(info_text, title="Session Info", border_style="green"))


def list_sessions():
    """List available sessions."""
    sessions = memory_manager.list_sessions()
    
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return
    
    session_table = Table(title="Available Sessions")
    session_table.add_column("Session ID", style="cyan")
    session_table.add_column("Status", style="white")
    
    agent = get_agent()
    current_session = agent.current_session_id
    
    for session_id in sessions:
        status = "Current" if session_id == current_session else "Available"
        session_table.add_row(session_id[:8] + "...", status)
    
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


def handle_command(command: str) -> str:
    """Handle special commands. Returns 'quit', 'handled', or 'continue'."""
    cmd = command.strip().lower()
    
    if cmd == "help":
        print_help()
        return "handled"
    
    elif cmd == "sessions":
        list_sessions()
        return "handled"
    
    elif cmd.startswith("session "):
        session_id = command[8:].strip()
        if session_id:
            agent = get_agent()
            agent.start_session(session_id)
            console.print(f"[green]Switched to session: {session_id}[/green]")
        else:
            console.print("[red]Please provide a session ID[/red]")
        return "handled"
    
    elif cmd == "info":
        print_session_info()
        return "handled"
    
    elif cmd == "clear":
        if Confirm.ask("Are you sure you want to clear the current session?"):
            agent = get_agent()
            # Delete current session from memory
            if agent.current_session_id:
                memory_manager.delete_session(agent.current_session_id)
            # Start completely new session
            agent.start_session()
            console.print("[green]Session cleared. Started new session.[/green]")
        return "handled"
    
    elif cmd == "config":
        config.print_config()
        return "handled"
    
    elif cmd == "multiline":
        console.print("[green]Multi-line input mode activated![/green]")
        user_input = get_multiline_input()
        if user_input:
            # Process the multi-line input
            agent = get_agent()
            console.print("[dim]Processing...[/dim]")
            try:
                response = agent.process_message(user_input)
                formatted_response = format_agent_response(response)
                console.print(Panel(formatted_response, title="Agent", border_style="green"))
            except Exception as e:
                console.print(f"[red]Agent error: {e}[/red]")
                console.print(f"[red]Error type: {type(e).__name__}[/red]")
                import traceback
                console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
        return "handled"
    
    elif cmd in ["quit", "exit"]:
        return "quit"
    
    return "continue"


async def process_streaming_response(agent, user_input: str):
    """Process agent response with streaming for real-time feedback."""
    console.print("[dim]Processing...[/dim]\n")
    
    response_text = ""
    current_tool = None
    
    try:
        async for event in agent.astream_response(user_input):
            event_type = event.get("event")
            
            # Handle different event types
            if event_type == "on_chat_model_stream":
                # Stream tokens as they arrive
                content = event["data"]["chunk"].content
                if content:
                    console.print(content, end="", style="green")
                    response_text += content
            
            elif event_type == "on_tool_start":
                # Show tool invocation
                tool_name = event.get("name", "unknown")
                current_tool = tool_name
                console.print(f"\n\n[dim]🛠️  Using tool: {tool_name}[/dim]")
            
            elif event_type == "on_tool_end":
                # Show tool completion
                if current_tool:
                    console.print(f"[dim]✅ Tool completed: {current_tool}[/dim]\n")
                    current_tool = None
            
            elif event_type == "on_retry":
                # Show retry notification
                data = event.get("data", {})
                retry_count = data.get("retry_count", 0)
                max_retries = data.get("max_retries", 0)
                error_type = data.get("error_type", "Unknown")
                console.print(f"\n[yellow]⚠️  Error encountered on attempt {retry_count}/{max_retries + 1}[/yellow]")
                console.print(f"[yellow]   Error: {error_type}[/yellow]")
                console.print(f"[yellow]   🔄 Retrying automatically...[/yellow]\n")
            
            elif event_type == "on_complete":
                # Streaming completed successfully
                console.print("\n")
                return True
            
            elif event_type == "on_error":
                # Handle errors
                error_data = event.get("data", {})
                console.print(f"\n\n[red]❌ Error: {error_data.get('error', 'Unknown error')}[/red]")
                console.print(f"[dim]Type: {error_data.get('error_type', 'Unknown')}[/dim]")
                return False
        
        return True
        
    except Exception as e:
        console.print(f"\n\n[red]Streaming error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def format_agent_response(response: dict) -> str:
    """Format agent response for display."""
    if not response["success"]:
        error_text = f"[red]Error: {response['error']}[/red]"
        if response.get("error_type"):
            error_text += f"\n[dim]Type: {response['error_type']}[/dim]"
        return error_text
    
    # Format successful response
    response_text = response["response"]
    
    # Add metadata if available
    if response.get("tool_calls"):
        tool_calls = response["tool_calls"]
        if tool_calls:
            response_text += f"\n\n[dim]Tools used: {len(tool_calls)}[/dim]"
    
    return response_text


@click.command()
@click.option("--session-id", help="Start with specific session ID")
@click.option("--model", default=None, help="OpenAI model to use (overrides config)")
@click.option("--stream/--no-stream", default=True, help="Enable streaming mode (default: enabled)")
def main(session_id: Optional[str], model: str, stream: bool):
    """Start the coding agent CLI."""
    
    # Check for OpenAI API key
    if not config.get_openai_api_key():
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        console.print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Validate configuration
    if not config.validate_config():
        console.print("[red]Configuration validation failed. Please check the errors above.[/red]")
        sys.exit(1)
    
    # Initialize agent (use CLI model if provided, otherwise use config)
    agent = get_agent(model_name=model)
    
    # Start session
    if session_id:
        agent.start_session(session_id)
        console.print(f"[green]Resumed session: {session_id}[/green]")
    else:
        session_id = agent.start_session()
        console.print(f"[green]Started new session: {session_id}[/green]")
    
    print_welcome()
    
    # Main interaction loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Handle special commands
            command_result = handle_command(user_input)
            
            if command_result == "quit":  # quit command
                break
            elif command_result == "handled":  # special command handled
                continue
            
            # Process with agent (only if not a special command)
            try:
                if stream:
                    # Use streaming mode
                    asyncio.run(process_streaming_response(agent, user_input))
                else:
                    # Use non-streaming mode
                    console.print("[dim]Processing...[/dim]")
                    response = agent.process_message(user_input)
                    
                    # Display response
                    formatted_response = format_agent_response(response)
                    console.print(Panel(formatted_response, title="Agent", border_style="green"))
            except Exception as e:
                console.print(f"[red]Agent error: {e}[/red]")
                console.print(f"[red]Error type: {type(e).__name__}[/red]")
                import traceback
                console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit gracefully[/yellow]")
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()
