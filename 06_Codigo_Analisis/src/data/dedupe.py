import hashlib
from collections import defaultdict
from pathlib import Path


def md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(root, pattern="*.jpg"):
    groups = defaultdict(list)
    for path in Path(root).rglob(pattern):
        groups[md5(path)].append(str(path))
    return {key: values for key, values in groups.items() if len(values) > 1}
