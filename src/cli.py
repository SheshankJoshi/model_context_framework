"""Console script for model_context_framework."""
import model_context_framework

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for model_context_framework."""
    console.print("Replace this message by putting your code into "
               "model_context_framework.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
