"""
ClawMode CLI - Gateway command using Typer.

Reads configuration from ~/.nanobot/config.json and starts the
ClawWork-enabled agent gateway.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich import print as rprint
from rich.console import Console

# Import ClawWork components
from clawmode_integration.agent_loop import ClawWorkAgentLoop, ClawWorkState
from clawmode_integration.task_classifier import TaskClassifier
from clawmode_integration.provider_wrapper import TrackedProvider
from clawmode_integration.tools import create_clawwork_tools
from livebench.economic.tracker import EconomicTracker
from livebench.work.evaluator import WorkEvaluator
from livebench.memory.memory import MemoryStore


app = typer.Typer(
    name="clawmode",
    help="ClawMode Integration - Economic tracking for nanobot agents",
)
console = Console()


def _load_nanobot_config() -> dict:
    """Load nanobot configuration from ~/.nanobot/config.json."""
    config_path = Path.home() / ".nanobot" / "config.json"
    
    if not config_path.exists():
        rprint("[red]❌ Nanobot config not found at ~/.nanobot/config.json[/red]")
        rprint("[yellow]Run 'nanobot onboard' to initialize[/yellow]")
        sys.exit(1)
    
    with open(config_path) as f:
        return json.load(f)


def _check_clawwork_enabled(config: dict) -> bool:
    """Check if ClawWork is enabled in config."""
    return config.get("agents", {}).get("clawwork", {}).get("enabled", False)


def _inject_evaluation_credentials(config: dict):
    """
    Inject evaluation credentials from nanobot config into environment.
    
    This allows the LLMEvaluator to use the same API key as the agent
    without requiring a separate OPENAI_API_KEY.
    """
    providers = config.get("providers", {})
    
    # Find the first provider with an API key
    for provider_name, provider_config in providers.items():
        api_key = provider_config.get("apiKey")
        if api_key:
            os.environ["EVALUATION_API_KEY"] = api_key
            
            # Set API base if available
            api_base = provider_config.get("apiBase") or provider_config.get("baseUrl")
            if api_base:
                os.environ["EVALUATION_API_BASE"] = api_base
            
            rprint(f"[dim]🔧 Evaluation using API key from {provider_name} provider[/dim]")
            break
    
    # Set evaluation model from defaults
    model = config.get("agents", {}).get("defaults", {}).get("model")
    if model:
        os.environ["EVALUATION_MODEL"] = model
        rprint(f"[dim]🔧 Evaluation model: {model}[/dim]")
    
    # Check if we have credentials
    if not os.getenv("EVALUATION_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        rprint("[yellow]⚠️  No evaluation credentials found[/yellow]")
        rprint("[yellow]   Work evaluation will use heuristics only[/yellow]")


def _build_state(config: dict) -> ClawWorkState:
    """
    Build ClawWorkState from nanobot config.
    
    Args:
        config: Nanobot config dictionary
        
    Returns:
        ClawWorkState instance
    """
    clawwork_config = config.get("agents", {}).get("clawwork", {})
    
    # Extract config values with defaults
    signature = clawwork_config.get("signature")
    if not signature:
        # Derive from model name
        model = config.get("agents", {}).get("defaults", {}).get("model", "agent")
        signature = model.replace("/", "-").replace(":", "-")
    
    initial_balance = clawwork_config.get("initialBalance", 1000.0)
    token_pricing = clawwork_config.get("tokenPricing", {})
    input_price = token_pricing.get("inputPrice", 2.5)
    output_price = token_pricing.get("outputPrice", 10.0)
    
    data_path = Path(clawwork_config.get("dataPath", "./livebench/data/agent_data"))
    meta_prompts_dir = clawwork_config.get("metaPromptsDir", "./eval/meta_prompts")
    
    # Initialize components
    tracker = EconomicTracker(
        signature=signature,
        data_path=data_path,
        initial_balance=initial_balance,
        input_price_per_million=input_price,
        output_price_per_million=output_price,
    )
    
    evaluator = WorkEvaluator(
        signature=signature,
        data_path=data_path,
        meta_prompts_dir=Path(meta_prompts_dir) if meta_prompts_dir else None,
        use_strict_eval=bool(os.getenv("EVALUATION_API_KEY")),
    )
    
    memory = MemoryStore(
        signature=signature,
        data_path=data_path,
    )
    
    # Note: classifier will be created after we have the tracked provider
    classifier = None
    
    rprint(f"[green]✅ Initialized economic tracker for {signature}[/green]")
    rprint(f"[dim]   Starting balance: ${initial_balance:.2f}[/dim]")
    
    if os.getenv("EVALUATION_API_KEY"):
        rprint("[green]✅ LLM-based evaluation enabled[/green]")
    else:
        rprint("[yellow]⚠️  Using heuristic evaluation (no LLM)[/yellow]")
    
    return ClawWorkState(
        tracker=tracker,
        evaluator=evaluator,
        memory=memory,
        classifier=classifier,
    )


@app.command()
def agent(
    message: Optional[str] = typer.Option(None, "-m", "--message", help="Single message to send"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
):
    """
    Start ClawMode agent (local CLI mode).
    
    Like 'nanobot agent' but with full ClawWork economic tracking.
    """
    rprint("[yellow]ClawMode agent command not fully implemented yet[/yellow]")
    rprint("[dim]This would start an interactive agent session with economic tracking[/dim]")
    
    config = _load_nanobot_config()
    
    if not _check_clawwork_enabled(config):
        rprint("[red]❌ ClawWork is not enabled in config[/red]")
        rprint("[yellow]Set agents.clawwork.enabled = true in ~/.nanobot/config.json[/yellow]")
        sys.exit(1)
    
    _inject_evaluation_credentials(config)
    state = _build_state(config)
    
    if message:
        rprint(f"\n[bold]Message:[/bold] {message}")
        rprint("[dim](Would process message through ClawWork agent loop)[/dim]")
    else:
        rprint("\n[bold]Interactive Mode[/bold]")
        rprint("[dim]Type messages to chat with the agent[/dim]")
        rprint("[dim]Use /clawwork <instruction> to assign a paid task[/dim]")
        rprint("[dim]Press Ctrl+C to exit[/dim]\n")


@app.command()
def gateway():
    """
    Start ClawMode gateway (channel listener).
    
    Listens for messages on all enabled channels (Telegram, Discord, etc.)
    and processes them through the ClawWork agent loop.
    """
    rprint("[bold cyan]🚀 Starting ClawMode Gateway[/bold cyan]\n")
    
    config = _load_nanobot_config()
    
    if not _check_clawwork_enabled(config):
        rprint("[red]❌ ClawWork is not enabled in config[/red]")
        rprint("[yellow]Set agents.clawwork.enabled = true in ~/.nanobot/config.json[/yellow]")
        sys.exit(1)
    
    _inject_evaluation_credentials(config)
    state = _build_state(config)
    
    # Check for enabled channels
    channels = config.get("channels", {})
    enabled_channels = [
        name for name, cfg in channels.items()
        if cfg.get("enabled", False)
    ]
    
    if not enabled_channels:
        rprint("[yellow]⚠️  No channels enabled[/yellow]")
        rprint("[dim]Enable a channel in ~/.nanobot/config.json (e.g., telegram, discord)[/dim]")
    else:
        rprint(f"[green]✅ Channels enabled: {', '.join(enabled_channels)}[/green]")
    
    rprint("\n[yellow]Gateway command not fully implemented yet[/yellow]")
    rprint("[dim]This would start the nanobot gateway with ClawWork integration[/dim]")
    rprint("[dim]Listen on enabled channels and route messages through ClawWorkAgentLoop[/dim]")


@app.command()
def status():
    """Check ClawWork status and configuration."""
    rprint("[bold]ClawMode Status[/bold]\n")
    
    config = _load_nanobot_config()
    
    enabled = _check_clawwork_enabled(config)
    rprint(f"ClawWork Enabled: {'✅ Yes' if enabled else '❌ No'}")
    
    if enabled:
        clawwork_config = config.get("agents", {}).get("clawwork", {})
        rprint(f"Signature: {clawwork_config.get('signature', 'auto')}")
        rprint(f"Initial Balance: ${clawwork_config.get('initialBalance', 1000):.2f}")
        
        token_pricing = clawwork_config.get("tokenPricing", {})
        rprint("Token Pricing:")
        rprint(f"  - Input: ${token_pricing.get('inputPrice', 2.5)}/M tokens")
        rprint(f"  - Output: ${token_pricing.get('outputPrice', 10.0)}/M tokens")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
