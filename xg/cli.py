import typer

from xg.commands.init import init
from xg.commands.cat_file import cat_file
from xg.commands.hash_object import hash_object

app = typer.Typer()
app.command()(init)
app.command()(cat_file)
app.command()(hash_object)


def main():
    app()
