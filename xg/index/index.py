import sys
import hashlib

import typer

from xg.utils.repo import find_repo
from xg.index.index_entry import IndexEntry


class Index:
    version_number: int
    entries: list[IndexEntry]
    extentions: bytes

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

    @staticmethod
    def get_index() -> "Index":
        repo = find_repo()
        index_path = repo / ".git" / "index"
        if not index_path.exists():
            return Index(version_number=2, entries=[], extentions=b"")
        return Index.from_bytes(index_path.read_bytes())
