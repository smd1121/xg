from typer import Option
from rich.pretty import pprint
from typing_extensions import Annotated

from xg.index.index import Index


def show_index(verbose: Annotated[bool, Option("-v", "--verbose", help="Show in verbose mode.")] = False):
    """
    Pretty-print the contents of the index file.

    Not a real git command, but a helper function to show the contents of the index file.
    """
    index = Index.get_index()

    for entry in index.entries:
        entry.verbose = verbose

    pprint(index)
