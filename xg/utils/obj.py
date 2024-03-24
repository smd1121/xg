import hashlib


def hash_blob(data: bytes) -> tuple[bytes, str]:
    """
    Calculate object ID (SHA) for a blob object.

    Returns a tuple of object data and object ID.
    """
    # <type> SPACE <size> NUL <data>
    object_data = b"blob" + b" " + str(len(data)).encode() + b"\x00" + data
    return object_data, hashlib.sha1(object_data).hexdigest()
