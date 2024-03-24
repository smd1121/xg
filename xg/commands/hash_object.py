import sys
import zlib
from pathlib import Path

from typer import Option, Argument, echo
from typing_extensions import Annotated

from xg.utils.obj import hash_blob
from xg.utils.repo import find_repo


def hash_object(
    file_path: Annotated[str, Argument(help="File to hash.")],
    write: Annotated[bool, Option("-w", help="Actually write the object into repo.")] = False,
):
    """
    Calculate object ID (SHA) and optionally write it to the object database.
    """
    f = Path(file_path)
    if not f.is_file():
        echo(f"fatal: could not open '{f}' for reading: No such file or directory", err=True)
        sys.exit(128)

    with f.open("rb") as f_:
        data = f_.read()

    object_data, object_id = hash_blob(data)

    echo(object_id)

    if write:
        object_dir = find_repo() / ".git" / "objects" / object_id[:2]
        object_dir.mkdir(parents=True, exist_ok=True)
        with (object_dir / object_id[2:]).open("wb") as f_:
            f_.write(zlib.compress(object_data))
