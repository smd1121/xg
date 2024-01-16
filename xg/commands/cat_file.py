import sys
import zlib

from typer import Option, Argument, echo
from typing_extensions import Annotated

from xg.utils.repo import find_repo


def cat_file(
    object_id: Annotated[str, Argument(help="The object to display.")],
    pretty: Annotated[bool, Option("-p", help="Pretty-print the contents of <object>.")] = False,
    show_size: Annotated[bool, Option("-s", help="Show the object's size in bytes.")] = False,
    show_type: Annotated[bool, Option("-t", help="Show the object's type.")] = False,
    exists: Annotated[
        bool, Option("-e", help="Exit with zero status if <object> exists and valid, or non-zero if it doesn't.")
    ] = False,
):
    """
    Display contents of an object.
    """
    # One and only one of these options can be used at a time.
    if sum([pretty, show_size, show_type, exists]) != 1:
        echo("fatal: one and only one of -p, -s, -t or -e can be used at a time", err=True)
        sys.exit(129)

    file_path = find_repo() / ".git" / "objects" / object_id[:2] / object_id[2:]

    if not file_path.is_file():
        if exists:
            sys.exit(1)

        echo(f"fatal: not a valid object name: {object_id}", err=True)
        sys.exit(128)

    with file_path.open("rb") as f:
        content = zlib.decompress(f.read())

    # <type> SPACE <size> NUL <data>
    try:
        hdr, data = content.split(b"\x00", maxsplit=1)
        type_, size = hdr.split(b" ", maxsplit=1)
    except ValueError:
        if exists:
            sys.exit(1)
        echo(f"fatal: invalid object {object_id}", err=True)
        sys.exit(128)

    if exists:
        sys.exit(0)

    if show_type:
        echo(type_.decode())
        sys.exit(0)

    if show_size:
        echo(size.decode())
        sys.exit(0)

    if pretty:
        if type_ == b"blob":
            sys.stdout.buffer.write(data)
            sys.exit(0)
        else:
            raise NotImplementedError(f"pretty-printing of {type_.decode()} objects is not supported")
