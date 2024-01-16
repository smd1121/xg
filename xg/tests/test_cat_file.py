import subprocess

from typer.testing import CliRunner

from xg.cli import app
from xg.tests.utils import temp_file, temp_git_repo

runner = CliRunner()


def test_cat_blob():
    # given a random file, write it to the object database with git,
    # and it can be retrieved with xg cat-file
    with temp_git_repo() as d:
        file_name, content = temp_file()

        object_id = subprocess.run(
            ["git", "hash-object", str(file_name), "-w"], capture_output=True, cwd=d, check=True
        ).stdout.strip()

        result = runner.invoke(app, ["cat-file", "-p", object_id])
        assert result.exit_code == 0
        assert result.stdout == content

        result = runner.invoke(app, ["cat-file", "-s", object_id])
        assert result.exit_code == 0
        assert result.stdout.rstrip() == str(len(content))

        result = runner.invoke(app, ["cat-file", "-t", object_id])
        assert result.exit_code == 0
        assert result.stdout.rstrip() == "blob"

        result = runner.invoke(app, ["cat-file", "-e", object_id])
        assert result.exit_code == 0

        result = runner.invoke(app, ["cat-file", "-e", "a" * 40])
        assert result.exit_code == 1
