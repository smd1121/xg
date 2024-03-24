import sys
from pathlib import Path

from typer import Option, Argument, echo
from typing_extensions import Annotated

from xg.index.index import Index, UpdateIndexError


def update_index(
    files: Annotated[list[str] | None, Argument(help="Files to update")] = None,
    verbose: Annotated[bool, Option("-v", "--verbose", help="Show actions.")] = False,
    refresh: Annotated[bool, Option("--refresh", help="Refresh and check index status.")] = False,
    add: Annotated[bool, Option("--add", help="Add files to index.")] = False,
    remove: Annotated[bool, Option("--remove", help="Remove files from index if they don't exist.")] = False,
    force_remove: Annotated[bool, Option("--force-remove", help="Remove files from index.")] = False,
    cacheinfo: Annotated[list[str] | None, Option("--cacheinfo", help="Add a file to the index.")] = None,
):
    """
    Register file contents in the working tree to the index
    """
    # check parameters
    if sum([refresh, add, remove, force_remove]) > 1:
        echo("At most one of --refresh, --add, --remove, --force-remove can be used at a time.", err=True)
        sys.exit(129)

    if refresh and (files or cacheinfo):
        echo("Cannot use --refresh with files or --cacheinfo.", err=True)
        sys.exit(129)

    if files and cacheinfo:
        echo("Cannot use --cacheinfo with files.", err=True)
        sys.exit(129)

    # prepare
    index = Index.get_index()
    if verbose:
        index.update_verbose = True

    # Usage #1. refresh
    if refresh:
        index.refresh()
        return

    # Usage #2. files
    if files:
        for f_ in files:
            f = Path(f_).absolute()
            try:
                if remove:
                    index.remove(f)
                elif force_remove:
                    index.force_remove(f)
                elif add:
                    index.add(f)
                else:
                    index.update(f)
            except UpdateIndexError as e:
                index.write_index()
                echo(f"error: {e}\nfatal: Unable to process path {f}", err=True)
                sys.exit(128)
        index.write_index()
        return

    # Usage #3. cacheinfo
    if cacheinfo:
        for cinfo in cacheinfo:
            mode, obj, path = cinfo.split(",", 2)
            f = Path(path).absolute()
            try:
                if remove:
                    index.remove(f)
                elif force_remove:
                    index.force_remove(f)
                elif add:
                    index.add_from_cacheinfo(mode, obj, path)
                elif f.exists():
                    index.update_from_cacheinfo(mode, obj, path)
            except UpdateIndexError as e:
                index.write_index()
                echo(f"error: {e}\nfatal: git update-index: --cacheinfo cannot add {f}", err=True)
                sys.exit(128)
        index.write_index()
        return
