import sys
import hashlib
from pathlib import Path

import typer

from xg.utils.repo import find_repo, rel_to_abs
from xg.index.index_entry import IndexEntry


class UpdateIndexError(RuntimeError):
    pass


class Index:
    version_number: int
    entries: list[IndexEntry]
    extentions: bytes

    update_verbose: bool = False

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    def __init__(self, version_number: int, entries: list[IndexEntry], extentions: bytes):
        self.version_number = version_number
        self.entries = entries
        self.extentions = extentions

    def __rich_repr__(self):
        yield "version_number", self.version_number
        yield "entry_count", self.entry_count
        yield "entries", self.entries
        yield "extentions", self.extentions

    @staticmethod
    def from_bytes(data: bytes) -> "Index":
        if data[:4] != b"DIRC":
            typer.echo("Invalid index file signature", err=True)
            sys.exit(1)

        version_number = int.from_bytes(data[4:8], "big")
        entry_count = int.from_bytes(data[8:12], "big")
        entries = []
        rest_data = data[12:]
        for _ in range(entry_count):
            entry, rest_data = IndexEntry.from_bytes(rest_data)
            entries.append(entry)

        sha = rest_data[-20:]
        if sha != hashlib.sha1(data[:-20]).digest():
            typer.echo("[Warning] Invalid index file checksum", err=True)

        return Index(version_number=version_number, entries=entries, extentions=rest_data[:-20])

    def to_bytes(self) -> bytes:
        result = b"DIRC"
        result += self.version_number.to_bytes(4, "big")
        result += self.entry_count.to_bytes(4, "big")
        for entry in self.entries:
            result += entry.to_bytes()
        result += self.extentions
        result += hashlib.sha1(result).digest()
        return result

    @staticmethod
    def get_index() -> "Index":
        repo = find_repo()
        index_path = repo / ".git" / "index"
        if not index_path.exists():
            return Index(version_number=2, entries=[], extentions=b"")
        return Index.from_bytes(index_path.read_bytes())

    def write_index(self):
        repo = find_repo()
        index_path = repo / ".git" / "index"
        index_path.write_bytes(self.to_bytes())

    def path_to_index_entry(self, path: Path) -> IndexEntry | None:
        for entry in self.entries:
            if entry.metadata.path == path:
                return entry
        return None

    def update(self, path: Path):
        if not self.path_to_index_entry(path):
            raise UpdateIndexError(f"error: {path} cannot add to the index - missing --add option?")
        self.add(path)

    def add(self, path: Path):
        if not path.exists():
            raise UpdateIndexError(f"error: {path} does not exist and --remove not passed")
        entry = self.path_to_index_entry(path)
        if entry:
            self.entries.remove(entry)

        new_entry = IndexEntry.from_path(path)
        self.entries.append(new_entry)
        self.sort_entries()

        if self.update_verbose:
            typer.echo(f"add '{path}'")

    def force_remove(self, path: Path):
        entry = self.path_to_index_entry(path)
        if entry:
            self.entries.remove(entry)
            if self.update_verbose:
                typer.echo(f"remove '{path}'")

    def remove(self, path: Path):
        if not path.exists():
            self.force_remove(path)

    def refresh(self):
        need_update = []
        for i, entry in enumerate(self.entries):
            if not entry.metadata.path.exists():
                need_update.append(entry.file_name)
                continue
            new_entry = IndexEntry.from_path(entry.metadata.path)
            if new_entry.sha != entry.sha:
                need_update.append(entry.file_name)
            else:
                self.entries[i] = new_entry

    def update_from_cacheinfo(self, mode: str, obj: str, path: str):
        p = rel_to_abs(path)
        entry = self.path_to_index_entry(p)
        if not entry:
            raise UpdateIndexError(f"error: {p}: cannot add to the index - missing --add option?")
        self.add_from_cacheinfo(mode, obj, path)

    def add_from_cacheinfo(self, mode: str, obj: str, path: str):
        p = rel_to_abs(path)
        entry = self.path_to_index_entry(p)
        if entry:
            self.entries.remove(entry)
        new_entry = IndexEntry.from_cache_info(mode, obj, path)
        self.entries.append(new_entry)
        self.sort_entries()

        if self.update_verbose:
            typer.echo(f"add '{path}'")

    def sort_entries(self):
        self.entries.sort(key=lambda x: x.file_name)
