import typer

from xg.commands.init import init

app = typer.Typer()
app.command()(init)


@app.command()
def hello(name: str):
    print(f"Hello -- {name}")


def main():
    app()
