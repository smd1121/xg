import os
import random
import string
import tempfile
import contextlib
from pathlib import Path

from typer.testing import CliRunner

from xg.cli import app

runner = CliRunner()


def random_string(length: int = 100) -> str:
    alpabet = string.ascii_letters + string.digits + string.punctuation + " \n\t"
    return "".join(random.choices(alpabet, k=length))


@contextlib.contextmanager
def temp_git_repo():
    with tempfile.TemporaryDirectory() as d:
        runner.invoke(app, ["init", d])
        cwd = Path.cwd()
        os.chdir(d)
        try:
            yield d
        finally:
            os.chdir(cwd)


def temp_file(file_name: str = "test.txt", d: Path = Path(".")) -> tuple[Path, str]:
    file_path = Path(d) / file_name

    content = random_string()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path, content
