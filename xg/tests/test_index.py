from xg.utils.repo import find_repo
from xg.index.index import Index


def test_index_to_bytes():
    repo = find_repo()
    index_path = repo / ".git" / "index"
    index = Index.get_index()
    assert index.to_bytes() == index_path.read_bytes()
