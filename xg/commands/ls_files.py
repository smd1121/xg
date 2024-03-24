from pathlib import Path

from xg.index.index import Index


def ls_files():
    """
    List all files in git index in the current directory.
    """
    index = Index.get_index()
    for entry in index.entries:
        cwd = Path.cwd()
        entry_path = entry.metadata.path
        if cwd in entry_path.parents:
            print(entry_path.relative_to(cwd))
