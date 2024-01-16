import tempfile
import subprocess

from typer.testing import CliRunner

from xg.cli import app
from xg.tests.utils import temp_file, random_string, temp_git_repo

runner = CliRunner()


def test_object_id():
    # given a random file, calculate its object ID with xg,
    # the value should be the same as git hash-object
    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, "w", encoding="utf-8") as f_:
            f_.write(random_string())

        result = runner.invoke(app, ["hash-object", f.name])
        assert result.exit_code == 0

        expected_result = subprocess.run(["git", "hash-object", f.name], capture_output=True, check=True)

        assert result.stdout == expected_result.stdout.decode()


def test_write_object():
    # given a random file, write it to the object database with xg,
    # and it can be retrieved with git cat-file
    with temp_git_repo():
        file_path, content = temp_file()

        result = runner.invoke(app, ["hash-object", "-w", str(file_path)])
        assert result.exit_code == 0

        object_id = result.stdout.strip()

        expected_result = subprocess.run(["git", "cat-file", "-p", object_id], capture_output=True, check=True)
        assert expected_result.stdout.decode() == content
