import sys
from pathlib import Path

from typer import echo


def find_repo() -> Path:
    """Find the root of the repo, or exit if it doesn't exist."""
    p = Path.cwd()
    while not (p / ".git").is_dir():
        if p == p.parent:
            echo("fatal: not a git repository (or any of the parent directories): .git", err=True)
            sys.exit(128)
        p = p.parent
    return p
