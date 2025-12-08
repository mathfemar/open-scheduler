"""File operations: list and read .py files under a project root."""
import os
from typing import List, Dict


def _should_skip(dirpath: str) -> bool:
    parts = dirpath.split(os.sep)
    skip = {"venv", "env", ".git", "__pycache__"}
    return any(p in skip for p in parts)


def list_files(root: str) -> List[Dict]:
    """Recursively find .py files under `root`.

    Returns list of dicts: {relpath, abspath, size_kb}
    """
    out = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        if _should_skip(dirpath):
            # prevent descending into these dirs
            dirnames[:] = [d for d in dirnames if d not in ("venv", "env", ".git", "__pycache__")]
            continue
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            abspath = os.path.join(dirpath, fname)
            try:
                size_kb = max(1, os.path.getsize(abspath) // 1024)
            except OSError:
                size_kb = 0
            rel = os.path.relpath(abspath, root)
            out.append({"relpath": rel, "abspath": abspath, "size_kb": size_kb})
    # sort by path
    out.sort(key=lambda x: x['relpath'])
    return out


def read_file(path: str, root: str = None) -> str:
    """Read file content. If `root` provided, path may be relative to it."""
    p = path
    if root and not os.path.isabs(p):
        p = os.path.join(root, p)
    p = os.path.abspath(p)
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()
