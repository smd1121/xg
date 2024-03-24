from typing import Optional
from pathlib import Path

from xg.utils.obj import hash_blob
from xg.utils.misc import timestamp_to_str
from xg.utils.repo import rel_to_abs
from xg.index.metadata import Metadata


class Flag:
    assume_valid: bool
    extended: bool
    stage: int
    name_length: int

    def __init__(self, assume_valid, extended, stage, name_length):
        self.assume_valid = assume_valid
        self.extended = extended
        self.stage = stage
        self.name_length = name_length

    @staticmethod
    def from_bytes(data: bytes) -> "Flag":
        assert len(data) == 2
        flag = int.from_bytes(data, "big")
        assume_valid = flag & 0x8000 != 0
        extended = flag & 0x4000 != 0
        stage = (flag & 0x3000) >> 12
        name_length = flag & 0x0FFF
        return Flag(assume_valid, extended, stage, name_length)

    def to_bytes(self) -> bytes:
        flag = 0
        if self.assume_valid:
            flag |= 0x8000
        if self.extended:
            flag |= 0x4000
        flag |= self.stage << 12
        flag |= self.name_length
        return flag.to_bytes(2, "big")

    def __rich_repr__(self):
        yield "assume_valid", self.assume_valid
        yield "extended", self.extended
        yield "stage", self.stage
        yield "name_length", self.name_length


class IndexEntry:
    metadata: Metadata
    sha: str
    flags: Flag
    extended_flags: Optional[bytes]
    file_name: str

    def __init__(
        self,
        metadata,
        sha,
        flags,
        extended_flags,
        file_name,
    ):
        self.metadata = metadata
        self.sha = sha
        self.flags = flags
        self.extended_flags = extended_flags
        self.file_name = file_name

    @staticmethod
    def from_bytes(data: bytes) -> tuple["IndexEntry", bytes]:
        ctime_s = int.from_bytes(data[:4], "big")
        ctime_ns = int.from_bytes(data[4:8], "big")
        mtime_s = int.from_bytes(data[8:12], "big")
        mtime_ns = int.from_bytes(data[12:16], "big")
        dev = int.from_bytes(data[16:20], "big")
        inode = int.from_bytes(data[20:24], "big")
        mode = int.from_bytes(data[24:28], "big")
        uid = int.from_bytes(data[28:32], "big")
        gid = int.from_bytes(data[32:36], "big")
        file_size = int.from_bytes(data[36:40], "big")
        sha = data[40:60].hex()
        flags = Flag.from_bytes(data[60:62])

        entry_len = 62

        # if flags.extended == True, then there is a 16-bit extended flag
        if flags.extended:
            extended_flags = data[62:64]
            entry_len += 2
        else:
            extended_flags = None

        if flags.name_length < 0xFFF:
            file_name = data[entry_len : entry_len + flags.name_length]
            assert data[entry_len + flags.name_length] == 0
            entry_len += flags.name_length + 1
        else:
            # if name_length >= 0xFFF, then find `\x00` to get the file name
            file_name, _ = data[entry_len:].split(b"\x00", maxsplit=1)
            entry_len += len(file_name) + 1

        entry_len = (entry_len + 7) // 8 * 8  # aligned to 8 bytes
        rest = data[entry_len:]  # remove padding

        metadata = Metadata(
            rel_to_abs(file_name.decode()),
            ctime_s,
            ctime_ns,
            mtime_s,
            mtime_ns,
            dev,
            inode,
            mode,
            uid,
            gid,
            file_size,
        )

        return (
            IndexEntry(
                metadata,
                sha,
                flags,
                extended_flags,
                file_name.decode(),
            ),
            rest,
        )

    def to_bytes(self) -> bytes:
        result = b""
        result += self.metadata.to_bytes()
        result += bytes.fromhex(self.sha)
        result += self.flags.to_bytes()
        if self.flags.extended:
            assert self.extended_flags is not None
            result += self.extended_flags
        result += self.file_name.encode()
        result += b"\x00"
        result += b"\x00" * ((len(result) + 7) // 8 * 8 - len(result))
        return result

    @staticmethod
    def from_path(path: Path) -> "IndexEntry":
        metadata = Metadata.get_metadata(path)
        _, sha = hash_blob(path.read_bytes())
        flags = Flag(assume_valid=False, extended=False, stage=0, name_length=len(path.name))
        extended_flags = None
        file_name = path.name
        return IndexEntry(metadata, sha, flags, extended_flags, file_name)

    @staticmethod
    def from_cache_info(mode: str, obj: str, path: str) -> "IndexEntry":
        p = rel_to_abs(path)
        metadata = Metadata.from_cache_info(p, int(mode, 8))
        flags = Flag(assume_valid=False, extended=False, stage=0, name_length=len(path))
        return IndexEntry(metadata, obj, flags, None, path)

    # 以下用于 show-index 输出

    verbose: bool = False

    def __rich_repr__(self):
        if not self.verbose:
            yield "file_name", self.file_name
            yield "ctime", timestamp_to_str(self.metadata.ctime_s, self.metadata.ctime_ns)
            yield "mtime", timestamp_to_str(self.metadata.mtime_s, self.metadata.mtime_ns)
            yield "sha", self.sha
        else:
            yield "metadata", self.metadata
            yield "sha", self.sha
            yield "flags", self.flags
            yield "extended_flags", self.extended_flags
            yield "file_name", self.file_name
