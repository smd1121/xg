import typer

from xg.commands.init import init
from xg.commands.cat_file import cat_file
from xg.commands.ls_files import ls_files
from xg.commands.show_index import show_index
from xg.commands.hash_object import hash_object

app = typer.Typer()
app.command()(init)
app.command()(cat_file)
app.command()(hash_object)
app.command(hidden=True)(show_index)
app.command()(ls_files)


def main():
    app()
